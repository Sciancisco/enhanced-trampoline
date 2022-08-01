from collections import deque, namedtuple
from threading import Thread

import cv2


CameraRecorderSpec = namedtuple('CameraRecorderSpec', 'cam_index fourcc fps')


class CameraRecorder(Thread):

    def __init__(self, cam_index, fourcc, fps):
        super().__init__()
        self._cam_index = cam_index
        self._fourcc = cv2.VideoWriter_fourcc(*fourcc)
        self._fps = fps
        self._resolution = None
        self._is_recording = False
        self._buffer = deque()

    # to launch in a thread
    def run(self):
        self._buffer.clear()
        cam = cv2.VideoCapture(self._cam_index)
        self._resolution = (int(cam.get(3)), int(cam.get(4)))

        self._is_recording = True

        while cam.isOpened() and self._is_recording:
            ret, frame = cam.read()
            if ret:
                # https://github.com/ContinuumIO/anaconda-issues/issues/223
                frame = cv2.resize(frame.astype('uint8'), self._resolution, cv2.INTER_LANCZOS4)
                self._buffer.append(frame)
            else:
                self._is_recording = False
        
        if not cam.isOpened():
            self._is_recording = False

        cam.release()

    def save_video(self, filename):
        if not self._buffer:
            print("Nothing to save")
            return

        writer = cv2.VideoWriter(filename, self._fourcc, self._fps, self._resolution)

        for frame in self._buffer:
            writer.write(frame)

        writer.release()

    def stop(self):
        self._is_recording = False

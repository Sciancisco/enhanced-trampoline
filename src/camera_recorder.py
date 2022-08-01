from collections import deque, namedtuple
from threading import Thread

import cv2


CameraRecorderSpec = namedtuple('CameraRecorderSpec', 'cam_index fourcc fps resolution')


class CameraRecorder(Thread):

    def __init__(self, cam_index, fourcc, fps):
        super().__init__()
        self._cam_index = cam_index
        self._fourcc = cv2.VideoWriter_fourcc(*fourcc)
        self._fps = fps
        self._is_recording = False
        self._buffer = deque()

    # to launch in a thread
    def run(self):
        self._buffer.clear()
        cam = cv2.VideoCapture(self._cam_index)

        self._is_recording = True

        while cam.isOpened() and self._is_recording:
            ret, frame = cam.read()
            if ret:
                frame = frame.astype('uint8')
                self._buffer.append(frame)
        
        if not cam.isOpened():
            self._is_recording = False

        cam.release()

    def save_video(self, filename):
        if not self._buffer:
            print("Nothing to save")
            return

        resolution = (self._buffer[0].shape[0], self._buffer[0].shape[1])
        writer = cv2.VideoWriter(filename, self._fourcc, self._fps, resolution)

        for frame in self._buffer:
            writer.write(frame)

        writer.release()

    def stop(self):
        self._is_recording = False

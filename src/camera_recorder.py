from collections import deque, namedtuple

import cv2


CameraRecorderSpec = namedtuple('CameraRecorderSpec', 'cam_index fourcc fps resolution')


class CameraRecorder(Thread):

    def __init__(self, cam_index, fourcc, fps, resolution):
        super().__init__()
        self._cam_index = cam_index
        self._fourcc = cv2.VideoWriter_fourcc(*fourcc)
        self._fps = fps
        self._resolution = resolution
        self._is_recording = False
        self._buffer = deque()

    # to launch in a thread
    def run(self):
        self._buffer.clear()
        cam = cv2.VideoCapture(self._cam_index)

        self._is_recording = True

        while self._is_recording:
            _, frame = cam.read()
            self._buffer.append(frame)

        cam.release()

    def save_video(self, filename):
        writer = cv2.VideoWriter(filename, self._fourcc, self._fps, self._resolution)

        for frame in self._buffer:
            writer.write(frame)

        writer.release()

    def stop(self):
        self._is_recording = False

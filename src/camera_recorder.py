from collections import deque, namedtuple
import time

import cv2


class CameraRecorder:

    def __init__(self, cam_index, fourcc, fps):
        self._cam = cv2.VideoCapture(cam_index)
        self._fourcc = cv2.VideoWriter_fourcc(*fourcc)  # TODO: better use DIVX for windows?
        self._resolution = (int(self._cam.get(3)), int(self._cam.get(4)))
        self._fps = None
        self._is_recording = False
        self._buffer = deque()
        
    def __del__(self):
        # make sure to release if object deleted at runtime 
        self._cam.release()

    # to launch in a thread
    def start_recording(self):
        if self._is_recording:
            raise Exception("Already recording.")

        self._buffer.clear()
        nb_frames = 0
        start = time.time()
        self._is_recording = True

        while self._cam.isOpened() and self._is_recording:
            ret, frame = self._cam.read()
            if ret:
                # https://github.com/ContinuumIO/anaconda-issues/issues/223
                frame = cv2.resize(frame.astype('uint8'), self._resolution, cv2.INTER_LANCZOS4)
                self._buffer.append(frame)
                nb_frames += 1
            else:
                self._is_recording = False

        stop = time.time()
        self._fps = nb_frames / (stop - start)

        if not self._cam.isOpened():
            self._is_recording = False
    
    def stop_recording(self):
        self._is_recording = False

    def save_video(self, filename):
        if not self._buffer:
            print("Nothing to save")
            return
        try:
            writer = cv2.VideoWriter(filename, self._fourcc, self._fps, self._resolution)

            for frame in self._buffer:
                writer.write(frame)

        finally:
            writer.release()


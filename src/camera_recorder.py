from collections import deque, namedtuple
from copy import copy
from threading import Thread
import time

import cv2

import _logging

logger = _logging.get_console_logger(__name__)


class CameraRecorderError(Exception):
    pass


class CameraRecorder:
    def __init__(self, camera_index, fourcc):
        self._cam = cv2.VideoCapture(camera_index)
        self._fourcc = cv2.VideoWriter_fourcc(*fourcc)
        self._resolution = (
            int(self._cam.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            int(self._cam.get(cv2.CAP_PROP_FRAME_WIDTH)),
        )
        self._fps = None
        self._buffer = deque()

        self._recorder_thread = None
        self._stop_recorder = False
        self._is_recording = False
        self._start_recording = False
        self._stop_recording = False

        # self._logger = logger.getChild(repr(self))

    def __repr__(self):
        return f"CameraRecorder@{hex(id(self))[-7:]}"

    def __del__(self):
        # make sure to release if object deleted at runtime
        self._cam.release()

    @property
    def is_recorder_running(self):
        return self._recorder_thread is not None and self._recorder_thread.is_alive()

    @property
    def is_recording(self):
        return self._is_recording

    def _recorder(self):
        while not self._stop_recorder:
            time.sleep(0.001)

            if self._start_recording and self._buffer_lock.acquire():
                self._start_recording = False
                self._stop_recording = False
                self._is_recording = True
                self._buffer.clear()

                if not self._cam.isOpened():
                    self._cam.open()

                nb_frames = 0
                start = time.time()

                while not self._stop_recording and not self._stop_recorder and self._cam.isOpened():
                    ret, frame = self._cam.read()
                    if ret:
                        # camera is sideways
                        frame = cv2.rotate(frame.astype("uint8"), cv2.ROTATE_90_CLOCKWISE)
                        self._buffer.append(frame)
                        nb_frames += 1
                    else:
                        self._stop_recording = True

                stop = time.time()
                self._fps = nb_frames / (stop - start)
                self._buffer_lock.release()

                self._is_recording = False

        self._is_recording = False
        self._cam.release()

    def start_recorder(self):
        if not self.is_recorder_running:
            self._stop_recorder = False
            self._recorder_thread = Thread(target=self._recorder)
            self._recorder_thread.start()
        else:
            raise CameraRecorderError("Recorder already started.")

    def stop_recorder(self):
        if self._recorder_thread is not None:  # there is a thread only if self.start_recorder was called
            self._stop_recording = True  # stops recording
            self._stop_recorder = True  # stop the recorder
            self._recorder_thread.join()
            self._recorder_thread = None

    def start_recording(self):
        if not self._is_recording:
            self._start_recording = True
        else:
            raise CameraRecorderError("Already recording.")

    def stop_recording(self):
        self._stop_recording = True

    def save_video(self, filename):
        if self._buffer:
            buffer = copy(self._buffer)  # snapshot of the buffer, makes it thread safe
            try:
                # of great help to figure out VideoWriter's quirks
                # https://github.com/ContinuumIO/anaconda-issues/issues/223
                writer = cv2.VideoWriter(filename, self._fourcc, self._fps, self._resolution)

                for frame in buffer:
                    writer.write(frame)

            finally:
                writer.release()
        else:
            raise CameraRecorderError("Nothing to save.")

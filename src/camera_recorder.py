from collections import deque, namedtuple
from threading import Lock, Thread
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
        self._buffer_lock = Lock()
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
    def is_recorder_started(self):
        return self._recorder_thread is not None and self._recorder_thread.is_alive()

    @property
    def is_recording(self):
        return self._is_recording

    @property
    def has_stop_recorder(self):
        return self._stop_recorder

    @property
    def last_frame(self):
        return self._buffer[-1]

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
        if self._recorder_thread is None or not self._recorder_thread.is_alive():
            self._stop_recorder = False
            self._recorder_thread = Thread(target=self._recorder)
            self._recorder_thread.start()
        else:
            raise CameraRecorderError("Recorder already started.")

    def stop_recorder(self):
        if self._recorder_thread is not None:
            self._stop_recording = True
            self._stop_recorder = True
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
        if self._buffer_lock.locked() or self._is_recording:
            self._stop_recording = True

        if self._buffer:
            self._buffer_lock.acquire()
            try:
                # of great help to figure out VideoWriter's quirks
                # https://github.com/ContinuumIO/anaconda-issues/issues/223
                writer = cv2.VideoWriter(filename, self._fourcc, self._fps, self._resolution)

                for frame in self._buffer:
                    writer.write(frame)

            finally:
                writer.release()
                self._buffer_lock.release()
        else:
            raise CameraRecorderError("Nothing to save.")

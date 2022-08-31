from enum import Enum
from collections import deque, namedtuple
from copy import copy
from threading import Thread  # NOTE: this code assumes that the GIL exists.
import time

import cv2


class CameraRecorderError(Exception):
    pass


class _States(Enum):

    NOT_RUNNING = ()
    IDLE = ()
    RECORDING = ()

    @classmethod
    def init_automaton(cls):
        for state in cls:
            state._clear_nexts()

        cls.NOT_RUNNING._add_next(cls.IDLE)
        cls.NOT_RUNNING._add_next(cls.NOT_RUNNING)

        cls.IDLE._add_next(cls.NOT_RUNNING)
        cls.IDLE._add_next(cls.RECORDING)

        cls.RECORDING._add_next(cls.IDLE)
        cls.RECORDING._add_next(cls.NOT_RUNNING)

    def __init__(self):
        self._nexts = set()

    def _add_next(self, state):
        self._nexts.add(state)

    def _clear_nexts(self):
        self._nexts.clear()

    def to(self, state):
        if state in self._nexts:
            return state
        else:
            raise CameraRecorderError(f"Cannot transition from {self} to {state}.")


_State.init_automaton()


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
        self._state = _States.NOT_RUNNING

    def __repr__(self):
        return f"CameraRecorder@{hex(id(self))[-7:]}"

    def __del__(self):
        # make sure to release if object deleted at runtime
        self._cam.release()

    @property
    def is_recorder_running(self):
        return self._state in {_States.IDLE, _States.RECORDING}

    @property
    def is_recording(self):
        return self._state is _States.RECORDING

    def _recorder(self):
        self._state = self._state.to(_States.IDLE)

        while self._state is not _States.NOT_RUNNING:
            time.sleep(0.001)

            if self._state is _States.RECORDING:
                self._buffer.clear()

                if not self._cam.isOpened():
                    self._cam.open()

                nb_frames = 0
                start = time.time()

                while self._state is _States.RECORDING and self._cam.isOpened():
                    ret, frame = self._cam.read()
                    if ret:
                        # camera is sideways
                        frame = cv2.rotate(frame.astype("uint8"), cv2.ROTATE_90_CLOCKWISE)
                        self._buffer.append(frame)
                        nb_frames += 1
                    else:
                        self._state = self._state.to(_States.IDLE)

                stop = time.time()
                self._fps = nb_frames / (stop - start)

        self._cam.release()
        self._state = self._state.to(_States.NOT_RUNNING)

    def start_recorder(self):
        if self._state is _States.NOT_RUNNING:
            self._recorder_thread = Thread(target=self._recorder)
            self._recorder_thread.start()
        else:
            raise CameraRecorderError("Recorder already started.")

    def stop_recorder(self):
        self._state = self._state.to(_States.NOT_RUNNING)
        self._recorder_thread.join()
        self._recorder_thread = None

    def start_recording(self):
        self._state = self._state.to(_States.RECORDING)

    def stop_recording(self):
        self._state = self._state.to(_State.IDLE)

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

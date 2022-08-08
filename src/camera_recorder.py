from collections import deque, namedtuple
from threading import Lock, Thread
import time

import cv2

import _logging

logger = _logging.get_console_logger(__name__)


class CameraRecorder(Thread):
    def __init__(self, camera_index, fourcc):
        super().__init__()

        self._cam = cv2.VideoCapture(cam_index)
        self._fourcc = cv2.VideoWriter_fourcc(*fourcc)  # TODO: better use DIVX for windows?
        self._resolution = (int(self._cam.get(3)), int(self._cam.get(4)))
        self._fps = None
        self._buffer = deque()

        self._quit = False
        self._start_recording = False
        self._stop_recording = False
        self._is_recording = False
        self._buffer_lock = Lock()

        self._logger = logger.getChild(repr(self))

    def __repr__(self):
        return f"CameraRecorder@{hex(id(self))}"

    def __del__(self):
        # make sure to release if object deleted at runtime
        self._cam.release()

    @property
    def is_recording(self):
        return self._is_recording

    @property
    def has_quit(self):
        return self._quit

    def run(self):
        self._logger.info("Camera recorder running...")

        while not self._quit:
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

                self._logger.info("Recording...")

                while not self._stop_recording and not self._quit and self._cam.isOpened():
                    ret, frame = self._cam.read()
                    if ret:
                        frame = frame.astype("uint8")
                        self._buffer.append(frame)
                        nb_frames += 1
                    else:
                        self._stop_recording = True

                stop = time.time()
                self._fps = nb_frames / (stop - start)
                self._buffer_lock.release()

                self._is_recording = False
                self._logger.info("Stopped recording.")

        self._is_recording = False
        self._cam.release()
        self._logger.warning("Camera recorder quit.")

    def start_recording(self):
        if not self._is_recording:
            self._start_recording = True
        else:
            self._logger.warning("Already recording, won't restart.")

    def stop_recording(self):
        self._stop_recording = True

    def quit(self):
        if self.is_alive():
            self._quit = True
        else:
            self._logger.warning("Tried to quit a non-running camera recorder.")

    def save_video(self, filename):
        if self._buffer_lock.locked() or self._is_recording:
            self._stop_recording = True
            self._logger.warning("Stopping recording before saving.")

        if self._buffer:
            self._buffer_lock.acquire()
            try:
                # of great help to figure out VideoWriter's quirks
                # https://github.com/ContinuumIO/anaconda-issues/issues/223
                writer = cv2.VideoWriter(filename, self._fourcc, self._fps, self._resolution)

                for frame in self._buffer:
                    writer.write(frame)

                self._logger.info(f"Saved {len(self._buffer)} frames to '{filename}'")

            finally:
                writer.release()
                self._buffer_lock.release()
        else:
            self._logger.warning("Nothing to save.")

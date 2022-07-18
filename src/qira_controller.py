import subprocess
import time
from enum import Enum

import keyboard
import mouse
import pygetwindow as gw
import requests


class State(Enum):

    LAUNCHED = -2
    TERMINATED = -1
    READY = 0
    START = 1
    ROUTINE = 2
    REVIEW = 3


class Trampoline(Enum):

    ONE = 1
    TWO = 2


class QiraControllerError(Exception):
    pass


class QiraController:

    WINDOW_SIZE = (720, 480)
    WINDOW_POSITION = (0, 0)
    TRAMPOLINE_SELECTOR_POSITION = (-1, -1)  # TODO: find out these positions
    TRAMPOLINE_1_POSITION = (-1, -1)
    TRAMPOLINE_2_POSITION = (-1, -1)

    URL = '127.0.0.1:8080'
    EXE_PATH = 'C:\Program Files (x86)\Qira\Qira.exe'

    def __init__(self, exe_path, window_title, url):
        self._exe_path = exe_path
        self._window_title = window_title
        self._url = url
        self._proc = None
        self._window = None
        self._state = State.TERMINATED

    def _is_proc_running(self):
        return self._proc is None or self._proc.returncode is not None:

    def _window_exists(self, function, *args, **kwargs):
        return self._window and self._window_title in gw.getAllTitles():

    def _position_window(self):
        if not self._is_proc_running():
            raise QiraControllerError("No Qira process running.")

        if not self._window_exists():
            raise QiraControllerError("No Qira window found.")

        self._window.moveTo(*self.WINDOW_POSITION)
        self._window.resizeTo(*self.WINDOW_SIZE)

    def _press_space(self):
        if not self._is_proc_running():
            raise QiraControllerError("No Qira process running.")

        if not self._window_exists():
            raise QiraControllerError("No Qira window found.")

        self._window.activate()
        print("Press space")

    def _select_trampoline(self, trampoline):
        if not self._is_proc_running():
            raise QiraControllerError("No Qira process running.")

        if not self._window_exists():
            raise QiraControllerError("No Qira window found.")

        self._position_window()
        self._window.activate()
        mouse.move(*self.TRAMPOLINE_SELECTOR_POSITION)
        mouse.click()
        time.sleep(.01)

        if trampoline == Trampoline.ONE:
            mouse.move(*self.TRAMPOLINE_1_POSITION)
            mouse.click()
        elif trampoline == Trampoline.TWO:
            mouse.move(*self.TRAMPOLINE_2_POSITION)
            mouse.click()
        else:
            raise QiraControllerError("Invalid argument: trampoline must be in enum Trampoline")

    def _detect_state(self):
        if not self._is_proc_running():
            raise QiraControllerError("No Qira process running.")

        if not self._window_exists():
            raise QiraControllerError("No Qira window found.")
        # TODO ?
        raise NotImplementedError("Not implemented yet.")

    def launch(self):
        if not self._is_proc_running():
            self._proc = subporcess.Popen(self._exe)

            t = 0
            timeout = 10
            while self._window_title not in gw.getAllTitles() and t < timeout:
                time.sleep(1)
                t += 1

            if not t < timeout:
                raise QiraControllerError("Could not acquire Qira window.")
            else:
                self._window = gw.getWindowWithTitle(self._window_title)
                self._state = State.LAUNCHED
        else:
            raise QiraControllerError("Qira is already running.")

    def terminate(self):
        # TODO: test terminate -> close, close -> terminate, close -> close, terminate -> terminate
        if self._is_proc_running():
            self._proc.terminate()
        self._proc = None
        self._window = None
        self._state = State.TERMINATED

    def close(self):
        if not self._is_proc_running():
            raise QiraControlerError("No process found.")

        if self._window:
            self._window.close()
            while self._window_title in gw.getAllTitles():
                time.sleep(1)
            self._state = State.TERMINATED  # TODO: verify behaviour

    def send_routine_meta(self, firstname, lastname):
        if not self._is_proc_running():
            raise QiraControllerErro("No Qira process running.")

        data = {'firstname': firstname, 'lastname': lastname}
        requests.post(f'{url}/routinemeta', data=data)  # TODO: add error handling

    #
    # transition functions
    #
    def ready(self):
        # set state READY
        if self._state == State.LAUNCHED:
            self._state = State.READY

        elif self._state == State.REVIEW:
            self._press_space()
            self._state = State.READY

        else:
            raise QiraControllerError(f"Cannot transition from {self._state} to {State.READY}.")

    def start(self):
        # set state START
        if self._state == State.READY:
            self._press_sapce()
            self._state = State.START
        else:
            raise QiraControllerError(f"Cannot transition from {self._state} to {State.START}.")

    def routine(self):
        # set state ROUTINE
        if self._state == State.START:
            self._press_sapce()
            self._state = State.ROUTINE
        else:
            raise QiraControllerError(f"Cannot transition from {self._state} to {State.ROUTINE}.")

    def review(self):
        # set state REVIEW
        if self._state == State.ROUTINE:
            self._state = State.REVIEW
        else:
            raise QiraControllerError(f"Cannot transition from {self._state} to {State.REVIEW}.")

    def review_short(self):
        # set state REVIEW after a short routine
        if self._state == State.ROUTINE:
            self._press_space()
            self._state = State.REVIEW
        else:
            raise QiraControllerError(f"Cannot transition from {self._state} to {State.REVIEW}.")

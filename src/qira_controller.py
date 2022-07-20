import subprocess
import time
from enum import Enum

import pyautogui
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
    ONETWO = 12
    AUTO = 0


class QiraControllerError(Exception):
    pass


class QiraController:

    WINDOW_SIZE = (1600, 855)
    WINDOW_POSITION = (0, 0)
    TRAMPOLINE_SELECTOR_POSITION = (240, 200)  # positions on a 1600x900 tn panel
    TRAMPOLINE_1_POSITION = (240, 225)
    TRAMPOLINE_2_POSITION = (240, 245)
    TRAMPOLINE_12_POSITION = (240, 260)
    TRAMPOLINE_AUTO_POSITION = (240, 280)

    ADDRESS = '127.0.0.1:8080'
    EXE_PATH = 'C:\Program Files (x86)\Qira\Qira.exe'
    WINDOW_TITLE = 'Qira v2.1.0'

    def __init__(self, exe_path, window_title, address):
        self._exe_path = exe_path
        self._window_title = window_title
        self._address = address
        self._proc = None
        self._window = None
        self._state = State.TERMINATED

    def _is_proc_running(self):
        return self._proc is not None and self._proc.returncode is None

    def _window_exists(self):
        return self._window and self._window_title in gw.getAllTitles()

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
        pyautogui.press(' ')

    def _detect_state(self):
        if not self._is_proc_running():
            raise QiraControllerError("No Qira process running.")

        if not self._window_exists():
            raise QiraControllerError("No Qira window found.")
        # TODO ?
        raise NotImplementedError("Not implemented yet.")

    def launch(self):
        if not self._is_proc_running():
            self._proc = subprocess.Popen(self._exe_path)

            t = 0
            timeout = 10
            while self._window_title not in gw.getAllTitles() and t < timeout:
                time.sleep(1)
                t += 1

            if not t < timeout:
                raise QiraControllerError("Could not acquire Qira window.")
            else:
                self._window = gw.getWindowsWithTitle(self._window_title)[0]
                self._state = State.READY
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
            raise QiraControllerError("No process found.")

        if self._window:
            self._window.close()
            while self._window_title in gw.getAllTitles():
                time.sleep(1)
            self._state = State.TERMINATED  # TODO: verify behaviour

    def send_routine_meta(self, firstname, lastname):
        if not self._is_proc_running():
            raise QiraControllerErro("No Qira process running.")

        data = {'firstname': firstname, 'lastname': lastname}
        requests.post(f'http://{self._address}/routinemeta', json=data)

    def select_trampoline(self, trampoline):
        if not self._is_proc_running():
            raise QiraControllerError("No Qira process running.")

        if not self._window_exists():
            raise QiraControllerError("No Qira window found.")

        if self._state != State.READY:
            raise QiraControllerError(f"Can only select trampoline in {State.READY}.")

        self._position_window()
        self._window.activate()
        # maybe init the controller with the positions directly
        pyautogui.click(*self.TRAMPOLINE_SELECTOR_POSITION)
        time.sleep(.3)

        if trampoline == Trampoline.ONE:
            pyautogui.click(*self.TRAMPOLINE_1_POSITION)
        elif trampoline == Trampoline.TWO:
            pyautogui.click(*self.TRAMPOLINE_2_POSITION)
        elif trampoline == Trampoline.ONETWO:
            pyautogui.click(*self.TRAMPOLINE_12_POSITION)
        elif trampoline == Trampoline.AUTO:
            pyautogui.click(*self.TRAMPOLINE_AUTO_POSITION)
        else:
            raise QiraControllerError("Invalid argument: trampoline must be in enum Trampoline.")

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
            self._press_space()
            self._state = State.START
        else:
            raise QiraControllerError(f"Cannot transition from {self._state} to {State.START}.")

    def routine(self):
        # set state ROUTINE
        if self._state == State.START:
            self._press_space()
            self._state = State.ROUTINE
        else:
            raise QiraControllerError(f"Cannot transition from {self._state} to {State.ROUTINE}.")

    def review(self):
        # set state REVIEW
        if self._state == State.ROUTINE:
            self._press_space()
            self._state = State.REVIEW
        else:
            raise QiraControllerError(f"Cannot transition from {self._state} to {State.REVIEW}.")


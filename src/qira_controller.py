import subprocess
import time
from enum import Enum

import pyautogui
import pygetwindow as gw
import requests


class State(Enum):

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

    def __init__(self,
        exe_path,
        window_title,
        address,
        window_size,
        window_position,
        trampoline_selector_position,
        trampoline_1_position,
        trampoline_2_position,
        trampoline_12_position,
        trampoline_auto_position
    ):
        self._exe_path = exe_path
        self._window_title = window_title
        self._address = address
        self._window_size = window_size
        self._window_position = window_position
        self._trampoline_selector_position = trampoline_selector_position
        self._trampoline_1_position = trampoline_1_position
        self._trampoline_2_position = trampoline_2_position
        self._trampoline_12_position = trampoline_12_position
        self._trampoline_auto_position = trampoline_auto_position
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

        self._window.moveTo(*self._window_position)
        self._window.resizeTo(*self._window_size)

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

        if not self._window_exists():
            raise QiraControllerError("No window found.")

        if self._window:
            self._window.close()
            while self._window_title in gw.getAllTitles():
                time.sleep(1)
            self._state = State.TERMINATED  # TODO: verify behaviour

    def send_routine_meta(self, firstname, lastname):
        if not self._is_proc_running():
            raise QiraControllerErro("No Qira process running.")

        data = {'firstname': firstname, 'lastname': lastname}
        response = requests.post(f'http://{self._address}/routinemeta', json=data)
        if not response.ok:
            raise QiraControllerError(f"An error occured while sending routine meta: {response.status_code} - {response.reason}")

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
        pyautogui.click(*self._trampoline_selector_position)
        time.sleep(.5)

        if trampoline == Trampoline.ONE:
            pyautogui.click(*self._trampoline_1_position)
        elif trampoline == Trampoline.TWO:
            pyautogui.click(*self._trampoline_2_position)
        elif trampoline == Trampoline.ONETWO:
            pyautogui.click(*self._trampoline_12_position)
        elif trampoline == Trampoline.AUTO:
            pyautogui.click(*self._trampoline_auto_position)
        else:
            raise QiraControllerError("Invalid argument: trampoline must be in enum Trampoline.")

    #
    # transition functions
    #
    def ready(self):
        if not self._is_proc_running():
            raise QiraControllerError("No process found.")

        if not self._window_exists():
            raise QiraControllerError("No window found.")

        # set state READY
        if self._state == State.READY:
            self._window.activate()

        elif self._state == State.REVIEW:
            self._press_space()
            self._state = State.READY

        else:
            raise QiraControllerError(f"Cannot transition from {self._state} to {State.READY}.")

    def start(self):
        if not self._is_proc_running():
            raise QiraControllerError("No process found.")

        if not self._window_exists():
            raise QiraControllerError("No window found.")

        # set state START
        if self._state == State.READY:
            self._press_space()
            self._state = State.START
        else:
            raise QiraControllerError(f"Cannot transition from {self._state} to {State.START}.")

    def routine(self):
        if not self._is_proc_running():
            raise QiraControllerError("No process found.")

        if not self._window_exists():
            raise QiraControllerError("No window found.")

        # set state ROUTINE
        if self._state == State.START:
            self._press_space()
            self._state = State.ROUTINE
        else:
            raise QiraControllerError(f"Cannot transition from {self._state} to {State.ROUTINE}.")

    def review(self):
        if not self._is_proc_running():
            raise QiraControllerError("No process found.")

        if not self._window_exists():
            raise QiraControllerError("No window found.")

        # set state REVIEW
        if self._state == State.ROUTINE:
            self._press_space()
            self._state = State.REVIEW
        else:
            raise QiraControllerError(f"Cannot transition from {self._state} to {State.REVIEW}.")


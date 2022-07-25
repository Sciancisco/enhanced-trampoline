import subprocess
import time
from enum import Enum

import pyautogui
import pygetwindow as gw
import requests


class State(Enum):

    CLOSED = -1
    NOUSB = 0
    READY = 1
    START = 2
    ROUTINE = 3
    REVIEW = 4
    DIAGNOSIS = 5


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
        trampoline_auto_position,
        ready_state_position,
        start_state_position,
        routine_state_position,
        review_state_position,
        nousb_state_position,
        diagnosis_state_position,
        ready_state_color,
        start_state_color,
        routine_state_color,
        review_state_color,
        nousb_state_color,
        diagnosis_state_color
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

        self._ready_state_position = ready_state_position
        self._ready_state_color = ready_state_color
        self._start_state_position = start_state_position
        self._start_state_color = start_state_color
        self._routine_state_position = routine_state_position
        self._routine_state_color = routine_state_color
        self._review_state_position = review_state_position
        self._review_state_color = review_state_color
        self._nousb_state_position = nousb_state_position
        self._nousb_state_color = nousb_state_color
        self._diagnosis_state_position = diagnosis_state_position
        self._diagnosis_state_color = diagnosis_state_color

    def _detect_window(self):
        if self._window_title in gw.getAllTitles():
            return gw.getWindowsWithTitle(self._window_title)[0]
        else:
            return None

    def _position_window(self):
        if not (window := self._detect_window()):
            raise QiraControllerError(f"No Qira window found with title '{self._window_title}'.")

        window.moveTo(*self._window_position)
        window.resizeTo(*self._window_size)

    def _press_space(self):
        if not (window := self._detect_window()):
            raise QiraControllerError(f"No Qira window found with title '{self._window_title}'.")

        window.activate()
        pyautogui.press(' ')

    def _detect_state(self):
        if not (window := self._detect_window()):
            return State.CLOSED

        window.activate()
        screenshot = pyautogui.screenshot()

        if screenshot.getpixel(self._ready_state_position) == self._ready_state_color:
            return State.READY
        elif screenshot.getpixel(self._start_state_position) == self._start_state_color:
            return State.START
        elif screenshot.getpixel(self._routine_state_position) == self._routine_state_color:
            return State.ROUTINE
        elif screenshot.getpixel(self._review_state_position) == self._review_state_color:
            return State.REVIEW
        elif screenshot.getpixel(self._no_usb_state_position) == self._no_usb_state_color:
            return State.NOUSB
        elif screenshot.getpixel(self._diagnosis_state_position) == self._diagnosis_state_color:
            return State.DIAGNOSIS
        else:
            raise QiraControllerError("Could not detect state.")

    def launch(self):
        if not (window := self._detect_window()):  # grab window here if exists
            subprocess.Popen(self._exe_path)

            t = 0
            timeout = 10
            while not (window := self._detect_window()) and t < timeout:
                time.sleep(1)
                t += 1

            if not t < timeout:
                raise QiraControllerError(f"Could not acquire Qira window with title '{self._window_title}'.")
        else:
            window.activate()

    def close(self):
        if window := self._detect_window():
            window.close()

    def send_routine_meta(self, firstname, lastname, timestamp):
        if state := self._detect_state() == State.CLOSED:
            raise QiraControllerError("Qira is not running.")

        if state not in {State.READY, State.START, State.ROUTINE, State.REVIEW}:
            raise QiraControllerError(f"Cannot send routine meta in state {state}.")

        data = {'firstname': firstname, 'lastname': lastname, 'timestamp': timestamp}
        response = requests.post(f'http://{self._address}/routinemeta', json=data)
        if not response.ok:
            raise QiraControllerError(f"An error occured while sending routine meta: {response.status_code} - {response.reason}")

    def select_trampoline(self, trampoline):
        if not (window := self._detect_window()):
            raise QiraControllerError(f"No Qira window found with title '{self._window_title}'.")

        if self._detect_state() != State.READY:
            raise QiraControllerError(f"Can only select trampoline in {State.READY}.")

        self._position_window()
        window.activate()

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
            raise TypeError(f"Invalid argument 'trampoline': must be in enum Trampoline not {trampoline}.")

    def change_state(self):
        self._press_space()

    def get_state(self):
        return self._detect_state()


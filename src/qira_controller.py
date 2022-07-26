from enum import Enum
from threading import Event, Thread  # NOTE: this code assumes that the GIL exists.
import time
import subprocess

import pyautogui
import pygetwindow as gw
import requests


class State(Enum):

    UNDEFINED = -2
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
    def __init__(
        self,
        exe_path,
        window_title,
        address,
        refresh_delay,
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
        diagnosis_state_color,
    ):
        self._exe_path = exe_path
        self._window_title = window_title
        self._address = address

        self._watcher_thread = None
        self._refresh_delay = refresh_delay
        self._refresh_flag = Event()
        self._watcher_is_watching = False
        self._callbacks = set()

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

    def __repr__(self):
        return f"QiraController@{hex(id(self))[-7:]}"

    def _detect_window(self):
        if self._window_title in gw.getAllTitles():
            return gw.getWindowsWithTitle(self._window_title)[0]
        else:
            return None

    def _position_window(self):
        if not (window := self._detect_window()):
            raise QiraControllerError(f"No Qira window found with title '{self._window_title}'.")

        window.maximize()

    def _press_1(self):
        if not (window := self._detect_window()):
            raise QiraControllerError(f"No Qira window found with title '{self._window_title}'.")

        window.activate()
        pyautogui.press("1")

    def _detect_state(self):
        if not (window := self._detect_window()):
            return State.CLOSED

        self._position_window()
        window.activate()

        time.sleep(0.01)
        screenshot = pyautogui.screenshot()

        if screenshot.getpixel(self._ready_state_position) == self._ready_state_color:
            return State.READY
        elif screenshot.getpixel(self._start_state_position) == self._start_state_color:
            return State.START
        elif screenshot.getpixel(self._routine_state_position) == self._routine_state_color:
            return State.ROUTINE
        elif screenshot.getpixel(self._review_state_position) == self._review_state_color:
            return State.REVIEW
        elif screenshot.getpixel(self._nousb_state_position) == self._nousb_state_color:
            return State.NOUSB
        elif screenshot.getpixel(self._diagnosis_state_position) == self._diagnosis_state_color:
            return State.DIAGNOSIS
        else:
            return State.UNDEFINED

    def _call_callbacks(self, from_, to):
        for callback in self._callbacks:
            try:
                callback(from_, to)
            except Exception as e:
                raise QiraControllerError(f"An error occured when calling {callback}: {e}")

    def _watcher(self):
        self._watcher_is_watching = True

        state = self._detect_state()
        while self._watcher_is_watching:
            try:
                previous_state, state = state, self._detect_state()
            except gw.PyGetWindowException:
                pass

            if previous_state != state:
                self._call_callbacks(previous_state, state)

            if self._refresh_flag.wait(self._refresh_delay):
                self._refresh_flag.clear()

    @property
    def is_watching(self):
        return self._watcher_is_watching

    @property
    def state(self):
        return self._detect_state()

    def add_callback(self, callback):
        if callable(callback):
            self._callbacks.add(callback)
        else:
            raise QiraControllerError("callback must be callable.")

    def remove_callback(self, callback):
        self._callbacks.discard(callback)

    def clear_callbacks(self):
        self._callbacks.clear()

    def start_watching(self):
        if self._watcher_thread is None or not self._watcher_thread.is_alive():
            self._watcher_thread = Thread(target=self._watcher)
            self._watcher_thread.start()
        else:
            raise QiraControllerError("Watcher already started.")

    def refresh_state(self):
        self._refresh_flag.set()

    def stop_watching(self):
        if (
            self._watcher_thread is not None and self._watcher_thread.is_alive()
        ):  # there is a thread only if self.start_watching was called
            self._watcher_is_watching = False  # stops the watcher
            self._watcher_thread.join()
            self._watcher_thread = None
        else:
            self._watcher_is_watching = False
            self._watcher_thread = None

    def launch(self):
        if not (window := self._detect_window()):
            subprocess.Popen(self._exe_path)

            t = 0
            timeout = 10
            while not (window := self._detect_window()) and t < timeout:
                time.sleep(1)
                t += 1

            if t >= timeout:
                raise QiraControllerError(f"Could not acquire Qira window with title '{self._window_title}'.")
        else:
            window.activate()

    def close(self):
        if window := self._detect_window():
            window.close()

    def send_routine_meta(self, firstname, lastname, timestamp):
        if self._detect_state() not in {
            State.READY,
            State.START,
            State.ROUTINE,
            State.REVIEW,
        }:
            raise QiraControllerError(f"Cannot send routine meta in state {state}.")

        data = {"firstname": firstname, "lastname": lastname, "timestamp": timestamp}
        response = requests.post(f"http://{self._address}/routinemeta", json=data)
        if not response.ok:
            raise QiraControllerError(
                f"An error occured while sending routine meta: {response.status_code} - {response.reason}"
            )

    def select_trampoline(self, trampoline):
        if not (window := self._detect_window()):
            raise QiraControllerError(f"No Qira window found with title '{self._window_title}'.")

        if (state := self._detect_state()) != State.READY:
            raise QiraControllerError(f"Can only select trampoline in {State.READY}, not {state}.")

        self._position_window()
        window.activate()

        pyautogui.click(*self._trampoline_selector_position)
        time.sleep(0.5)

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
        from_ = self._detect_state()
        self._press_1()
        while (to := self._detect_state()) == from_:  # ensures that the change is detected
            time.sleep(0.01)

        self._call_callbacks(from_, to)

        return from_, to

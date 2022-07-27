import time

from pynput import keyboard

import config
from qira_controller import Trampoline, State


class Server:

    def __init__(self, qira_controller):
        self._qira_controller = qira_controller
        self._timestamp = ''
        self._firstname = ''
        self._lastname = ''
        self._athlete_map = {}
        self._listener = None

    def _send_routine_meta(self):
        try:
            self._qira_controller.send_routine_meta(
                firstname=self._firstname,
                lastname=self._lastname,
                timestamp=self._timestamp
            )
            return True
        except Exception as e:
            print(e)
            return False


    def _on_remote_press(self, key):  # also work for keyboard presses since the remote is basically a keyboard
        try:
            k = key.char
        except:
            k = key.name

        if k in {'0', '2', '3', '4', '5', '6', '7', '8', '9'}:
            if  self._qira_controller.get_state() in {State.READY, State.START, State.ROUTINE, State.REVIEW} and k in self._athlete_map:
                self._firstname, self._lastname = self._athlete_map[k]
                self._send_routine_meta()

        elif k == 'media_play_pause':
            success = False
            try:
                from_, to = self._qira_controller.change_state()
                success = True
            except Exception as e:
                print(e)

            if success:
                if from_ == State.READY and to == State.START:
                    self._timestamp = time.strftime('%Y%m%d_%H%M%S')
                    self._send_routine_meta()
                elif from_ == State.REVIEW and to == State.READY:
                    print("WRITE VIDEO")

        elif k == 'media_previous':
            if self._qira_controller.get_state() == State.READY:
                try:
                    self._qira_controller.select_trampoline(Trampoline.ONE)
                except Exception as e:
                    print(e)

        elif k == 'media_next':
            if self._qira_controller.get_state() == State.READY:
                try:
                    self._qira_controller.select_trampoline(Trampoline.TWO)
                except Exception as e:
                    print(e)

    def _load_athlete_map(self, file):
        raise NotImplementedError("Not yet")

    def main_prompt(self):
        raise NotImplementedError("Not yet")

    def load_prompt(self):
        raise NotImplementedError("Not yet")

    def start(self):
        self._qira_controller.launch()
        if self._listener is None:
            self._listener = keyboard.Listener(on_press=self._on_remote_press)
            self._listener.start()

    def stop(self):
        if self._listener:
            self._listener.stop()
            self._listener = None

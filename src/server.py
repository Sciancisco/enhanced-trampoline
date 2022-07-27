import time

from pynput import keyboard

from qira_controller import Trampoline, State
from camera_recorder import CameraRecorder


class Server:

    def __init__(self,
        qira_controller,
        camera_recorder_spec,
        filename_spec,
        save_data_directory,
        save_video_directory,
        qira_data_directory
        use_cam=True
    ):
        self._qira_controller = qira_controller

        self._camera_recorder_spec = camera_recorder_spec
        self._camera_recorder = None

        self._filename_spec = filename_spec
        self._save_data_directory = save_data_directory
        self._save_video_directory = save_video_directory
        self._qira_data_directory = qira_data_directory

        self._use_cam = use_cam

        self._athlete_map = {}
        self._listener = None

        self._timestamp = ''
        self._firstname = ''
        self._lastname = ''

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

    def _start_video_recording(self):
        if not self._use_cam:
            return

        if self._camera_recorder and self._camera_recorder.is_alive():
            # if Qira's state changes and the server never sees the transition (REVIEW, READY)
            self._camera_recorder.stop()
            filename = self._filename_spec.format(firstname=self._firstname, lastname=self._lastname, timestamp=self._timestamp)
            self._camera_recorder.save_video(f'{self._save_video_directory}/{filename}_recovered.mp4')

        self._camera_recorder = CameraRecorder(**self._camera_recorder_spec)
        self._camera_recorder.start()

    def _stop_video_recording(self):
        if not self._use_cam:
            return

        if self._camera_recorder:
            self._camera_recorder.stop()

    def _save_video(self):
        if not self._use_cam:
            return

        if self._camera_recorder:
            self._camera_recorder.stop()
        filename = self._filename_spec.format(firstname=self._firstname, lastname=self._lastname, timestamp=self._timestamp)
        self._camera_recorder.save_video(f'{self._save_video_directory}/{filename}.mp4')

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
                    self._start_video_recording()

                elif from_ == State.ROUTINE and to == State.REVIEW:
                    self._stop_video_recording()

                elif from_ == State.REVIEW and to == State.READY:
                    self._save_video()

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

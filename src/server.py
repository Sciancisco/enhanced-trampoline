import time

from pynput import keyboard

import _logging
from camera_recorder import CameraRecorder
from qira_controller import QiraController, Trampoline, State


logger = _logging.get_console_logger(__name__)


class Server:
    def __init__(
        self,
        qira_controller_config,
        camera_recorder_config,
        filename_spec,
        video_container,
        save_data_directory,
        save_video_directory,
        qira_data_directory,
        use_cam=True,
    ):
        self._logger = logger.getChild(repr(self))

        self._qira_controller = QiraController(**qira_controller_config)

        if use_cam:
            try:
                self._camera_recorder = CameraRecorder(**camera_recorder_config)
            except:
                self._camera_recorder = None
                self._logger.exception("Error when initializing camera recorder. Camera disabled.")
        else:
            self._camera_recorder = None

        self._filename_spec = filename_spec
        self._video_container = video_container
        self._save_data_directory = save_data_directory
        self._save_video_directory = save_video_directory
        self._qira_data_directory = qira_data_directory

        self._athlete_map = {}
        self._listener = None

        self._timestamp = ""
        self._firstname = ""
        self._lastname = ""

    def __repr__(self):
        return f"Server@{hex(id(self))[-7:]}"

    @staticmethod
    def load_athlete_csv(filename):
        with open(filename) as f:
            content = f.readlines()

        if len(content) < 1:
            raise Exception("File is empty.")

        striped_content = map(str.strip, content)
        fields = next(striped_content)

        if fields != "firstname,lastname":
            raise Exception("Invalid fields. Must match 'firstname,lastname'.")

        athletes = map(lambda a: a.split(","), striped_content)
        number = map(str, range(2, len(content) + 1))
        mapping = zip(number, athletes)

        athlete_map = dict(mapping)

        # validation
        for i, athlete in enumerate(athlete_map.values()):
            if len(athlete) != 2:
                raise Exception(f"Athlete '{athlete}' invalid on line {i+1}. Must follow format 'firstname,lastname'.")

        return athlete_map

    def _send_routine_meta(self):
        try:
            self._qira_controller.send_routine_meta(
                firstname=self._firstname,
                lastname=self._lastname,
                timestamp=self._timestamp,
            )
            self._logger.info(
                "Sent routine meta: "
                f"firstname='{self._firstname}' lastname='{self._lastname}' timestamp='{self._timestamp}'."
            )
            return True
        except Exception as e:
            self._logger.exception(str(e))
            return False

    def _start_video_recording(self):
        if self._camera_recorder is None:
            return

        if self._camera_recorder.is_recorder_started:
            if self._camera_recorder.is_recording:
                # if Qira's state changes and the server never sees the transition (REVIEW, READY)
                self._camera_recorder.stop_recording()
                filename = self._filename_spec.format(
                    firstname=self._firstname,
                    lastname=self._lastname,
                    timestamp=self._timestamp,
                )
                full_path = f"{self._save_video_directory}/{filename}_recovered.{self._video_container}"
                self._camera_recorder.save_video(full_path)
                self._logger.warning(f"Camera was still recording, saved to '{full_path}'")

            self._camera_recorder.start_recording()
            self._logger.info("Started video recording...")
        else:
            self._logger.warning("Camera recorder is not alive.")

    def _stop_video_recording(self):
        if self._camera_recorder is None:
            return

        if self._camera_recorder.is_recorder_started:
            self._camera_recorder.stop_recording()
            self._logger.info("Stopped video recording.")
        else:
            self._logger.warning("Camera recorder is not alive.")

    def _save_video(self):
        if self._camera_recorder is None:
            return

        filename = self._filename_spec.format(
            firstname=self._firstname,
            lastname=self._lastname,
            timestamp=self._timestamp,
        )
        full_path = f"{self._save_video_directory}/{filename}.{self._video_container}"
        try:
            self._camera_recorder.save_video(full_path)
            self._logger.info(f"Saved video to '{full_path}'.")
        except:
            self._logger.exception("Error occured when saving video.")

    def _on_state_transition(self, from_, to):
        self._logger.info(f"Qira changed state ({from_} -> {to})")

        if to == State.REVIEW:
            self._stop_video_recording()

        if from_ == State.REVIEW:
            self._stop_video_recording()
            self._save_video()

        if to == State.START:
            self._timestamp = time.strftime("%Y%m%d_%H%M%S")
            self._start_video_recording()
            self._send_routine_meta()

    def _on_remote_press(self, key):  # also work for keyboard presses since the remote is basically a keyboard
        try:
            k = key.char
        except:
            k = key.name

        if (
            k in {"0", "2", "3", "4", "5", "6", "7", "8", "9"}
            and k in self._athlete_map
            and self._qira_controller.state in {State.READY, State.START, State.ROUTINE, State.REVIEW}
        ):
            self._firstname, self._lastname = self._athlete_map[k]
            self._send_routine_meta()

        elif k == "media_play_pause":
            try:
                from_, to = self._qira_controller.change_state()
                self._logger.info(f"Qira changed state ({from_} -> {to})")
            except Exception as e:
                self._logger.exception(str(e))

        elif k == "space" or k == "1":
            self._qira_controller.refresh_state()
            self._logger.info(f"Pressed {k}, refreshing Qira's state.")

        elif k == "media_previous":
            if self._qira_controller.state == State.READY:
                try:
                    self._qira_controller.select_trampoline(Trampoline.ONE)
                except Exception as e:
                    self._logger.exception(str(e))

        elif k == "media_next":
            if self._qira_controller.state == State.READY:
                try:
                    self._qira_controller.select_trampoline(Trampoline.TWO)
                except Exception as e:
                    print(e)

    @property
    def last_recorded_frame(self):
        if self._camera_recorder:
            return self._camera_recorder.last_frame
        else:
            return None

    def start(self):
        self._logger.info("Starting Qira watcher...")
        try:
            self._qira_controller.start_watching()
        except:
            self._logger.exception("Error occured when starting Qira watcher.")

        self._qira_controller.launch()
        self._qira_controller.add_callback(self._on_state_transition)

        if self._camera_recorder:
            self._logger.info("Starting camera recorder...")
            try:
                self._camera_recorder.start_recorder()
            except:
                self._logger.exception("Error when starting camera recorder.")

        if self._listener is None:
            self._logger.info("Starting keyboard listener...")
            self._listener = keyboard.Listener(on_press=self._on_remote_press)
            self._listener.start()

        self._logger.info("Server started.")

    def stop(self):
        if listener := bool(self._listener):
            self._logger.info("Stopping keyboard listener...")
            self._listener.stop()
            self._listener.join()
            self._listener = None

        if cam_recorder := bool(self._camera_recorder):
            self._logger.info("Stopping camera recorder...")
            self._camera_recorder.stop_recorder()

        if self._qira_controller.is_watching:
            self._logger.info("Stopping Qira watcher...")
            self._qira_controller.stop_watching()

        if listener or cam_recorder or watcher:
            self._logger.info("Server stopped.")
        else:
            self._logger.info("Already stopped.")

    def set_athlete_map(self, athlete_map):
        if athlete_map is None:
            athlete_map = {}
        self._athlete_map = athlete_map

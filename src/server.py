import logging
import time

from pynput import keyboard

from camera_recorder import CameraRecorder
from qira_controller import Trampoline, State


logger = logging.getLogger(__name__)

handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)

logger.addHandler(handler)


class Server:
    def __init__(
        self,
        qira_controller,
        camera_index,
        fourcc,
        filename_spec,
        video_container,
        save_data_directory,
        save_video_directory,
        qira_data_directory,
        use_cam=True,
    ):
        self._qira_controller = qira_controller

        self._camera_index = camera_index
        self._fourcc = fourcc
        self._camera_recorder = None
        self._use_cam = use_cam

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

    def _send_routine_meta(self):
        try:
            self._qira_controller.send_routine_meta(
                firstname=self._firstname,
                lastname=self._lastname,
                timestamp=self._timestamp,
            )
            logger.info(
                f"Sent routine meta: "
                "firstname='{self._firstname}' lastname='{self._lastname}' timestamp='{self._timestamp}'."
            )
            return True
        except Exception as e:
            logger.exception(str(e))
            return False

    def _start_video_recording(self):
        if not self._use_cam:
            return

        if self._camera_recorder.is_alive():
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
                logger.warning(f"Camera was still recording, saved to '{full_path}'")
            else:
                self._camera_recorder.start_recording()
                logger.info("Started video recording...")
        else:
            logger.critical("Camera recorder is not alive, disabling use of camera.")
            self._use_cam = False

    def _stop_video_recording(self):
        if not self._use_cam:
            return

        if self._camera_recorder.is_alive():
            self._camera_recorder.stop_recording()
            logger.info("Stopped video recording.")
        else:
            logger.critical("Camera recorder is not alive, disabling use of camera.")
            self._use_cam = False

    def _save_video(self):
        if not self._use_cam:
            return

        filename = self._filename_spec.format(
            firstname=self._firstname,
            lastname=self._lastname,
            timestamp=self._timestamp,
        )
        full_path = f"{self._save_video_directory}/{filename}.{self._video_container}"
        self._camera_recorder.save_video(full_path)

        logger.info(f"Saved video to '{full_path}'.")

    def _on_remote_press(self, key):  # also work for keyboard presses since the remote is basically a keyboard
        try:
            k = key.char
        except:
            k = key.name

        if (
            k in {"0", "2", "3", "4", "5", "6", "7", "8", "9"}
            and k in self._athlete_map
            and self._qira_controller.get_state() in {State.READY, State.START, State.ROUTINE, State.REVIEW}
        ):
            self._firstname, self._lastname = self._athlete_map[k]
            self._send_routine_meta()

        elif k == "media_play_pause":
            success = False
            try:
                from_, to = self._qira_controller.change_state()
                success = True
            except Exception as e:
                logger.exception(str(e))

            if success:
                if from_ == State.READY and to == State.START:
                    self._timestamp = time.strftime("%Y%m%d_%H%M%S")
                    self._send_routine_meta()
                    self._start_video_recording()

                elif from_ == State.ROUTINE and to == State.REVIEW:
                    # TODO: handle when Qira changes from ROUTINE to REVIEW automatically
                    self._stop_video_recording()

                elif from_ == State.REVIEW and to == State.READY:
                    self._save_video()

        elif k == "media_previous":
            if self._qira_controller.get_state() == State.READY:
                try:
                    self._qira_controller.select_trampoline(Trampoline.ONE)
                except Exception as e:
                    logger.exception(str(e))

        elif k == "media_next":
            if self._qira_controller.get_state() == State.READY:
                try:
                    self._qira_controller.select_trampoline(Trampoline.TWO)
                except Exception as e:
                    print(e)

    def start(self):
        self._qira_controller.launch()
        if self._listener is None:
            self._listener = keyboard.Listener(on_press=self._on_remote_press)
            self._listener.start()
        if self._camera_recorder is None or self._camera_recorder.has_quit:
            self._camera_recorder = CameraRecorder(self._camera_index, self._fourcc)
            self._camera_recorder.start()

    def stop(self):
        if self._listener:
            self._listener.stop()
            self._listener = None
        if self._camera_recorder:
            self._camera_recorder.quit()
            self._camera_recorder = None

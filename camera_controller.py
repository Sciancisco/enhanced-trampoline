import cv2
import keyboard

class CameraController:

    CAMERA_INDEX = 1
    STOP_KEY = ' '

    FOURCC = 'XVID'
    FPS = 60.
    VIDEO_RESOLUTION = (1920, 1080)

    def __init__(self, cam_index, stop_key, fourcc, fps, resolution):
        self._cam_index = cam_index
        self._stop_key = stop_key
        self._fourcc = cv2.VideoWriter_fourcc(*fourcc)
        self._fps = fps
        self._resolution = resolution
        self._is_recording = False

    # to launch in a thread
    def record(self, outfile):
        cam = cv2.VideoCapture(self._cam_index)
        output = cv2.VideoWriter(outfile, self._fourcc, self._fps, self._resolution)

        self._is_recording = True

        while self._is_recording:
            _, frame = cam.read()
            output.write(frame)
            if cv2.waitKey(1/fps) == self._stop_key:
                self._is_recording = False

        output.release()
        cam.release()

    def stop(self):
        if self._is_recording:
            keyboard.press_and_release(self._stop_key)

class QiraConfig:

    ADDRESS = "127.0.0.1:8080"
    EXE_PATH = "C:/Program Files/Qira/Qira"
    WINDOW_TITLE = "Qira v2.1.0"

    WINDOW_SIZE = (1600, 855)
    WINDOW_POSITION = (0, 0)

    TRAMPOLINE_SELECTOR_POSITION = (240, 200)  # positions on a 1600x900 TN panel
    TRAMPOLINE_1_POSITION = (240, 225)
    TRAMPOLINE_2_POSITION = (240, 245)
    TRAMPOLINE_12_POSITION = (240, 260)
    TRAMPOLINE_AUTO_POSITION = (240, 280)

    READY_STATE_POSITION = (40, 175)
    START_STATE_POSITION = (40, 210)
    ROUTINE_STATE_POSITION = (40, 240)
    REVIEW_STATE_POSITION = (40, 280)
    NOUSB_STATE_POSITION = (40, 130)
    DIAGNOSIS_STATE_POSITION = (40, 310)

    READY_STATE_COLOR = (70, 170, 110)
    START_STATE_COLOR = (220, 220, 90)
    ROUTINE_STATE_COLOR = (230, 90, 90)
    REVIEW_STATE_COLOR = (50, 100, 200)
    NOUSB_STATE_COLOR = (230, 90, 90)
    DIAGNOSIS_STATE_COLOR = (50, 100, 200)


class CameraConfig:

    FOURCC = "DIVX"
    CAMERA_INDEX = 0


class ServerConfig:

    FILENAME_SPEC = "{firstname}_{lastname}_{timestamp}"
    SAVE_DATA_DIRECTORY = "C:/Users/Test/enhanced-trampoline/local/save"
    SAVE_VIDEO_DIRECTORY = "C:/Users/Test/enhanced-trampoline/local/save/video"
    QIRA_DATA_DIRECTORY = "C:/Users/Test/enhanced-trampoline/local"

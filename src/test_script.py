from config import QiraConfig, CameraConfig, ServerConfig
from qira_controller import QiraController, Trampoline
from server import Server


qc = QiraController(
    QiraConfig.EXE_PATH,
    QiraConfig.WINDOW_TITLE,
    QiraConfig.ADDRESS,
    QiraConfig.TRAMPOLINE_SELECTOR_POSITION,
    QiraConfig.TRAMPOLINE_1_POSITION,
    QiraConfig.TRAMPOLINE_2_POSITION,
    QiraConfig.TRAMPOLINE_12_POSITION,
    QiraConfig.TRAMPOLINE_AUTO_POSITION,
    QiraConfig.READY_STATE_POSITION,
    QiraConfig.START_STATE_POSITION,
    QiraConfig.ROUTINE_STATE_POSITION,
    QiraConfig.REVIEW_STATE_POSITION,
    QiraConfig.NOUSB_STATE_POSITION,
    QiraConfig.DIAGNOSIS_STATE_POSITION,
    QiraConfig.READY_STATE_COLOR,
    QiraConfig.START_STATE_COLOR,
    QiraConfig.ROUTINE_STATE_COLOR,
    QiraConfig.REVIEW_STATE_COLOR,
    QiraConfig.NOUSB_STATE_COLOR,
    QiraConfig.DIAGNOSIS_STATE_COLOR,
)

server = Server(
    qira_controller=qc,
    camera_index=CameraConfig.CAMERA_INDEX,
    fourcc=CameraConfig.FOURCC,
    filename_spec=ServerConfig.FILENAME_SPEC,
    video_container=ServerConfig.VIDEO_CONTAINER,
    save_data_directory=ServerConfig.SAVE_DATA_DIRECTORY,
    save_video_directory=ServerConfig.SAVE_VIDEO_DIRECTORY,
    qira_data_directory=ServerConfig.QIRA_DATA_DIRECTORY,
)

server._athlete_map = {"2": ["Testy", "McTest"], "3": ["Johnny", "Test"], "4": ["Kevin", "McAttester"]}

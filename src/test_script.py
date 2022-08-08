from config import QiraConfig, CameraConfig, ServerConfig
from server import Server

server = Server(qira_controller_config=QiraConfig, camera_recorder_config=CameraConfig, **ServerConfig)

server._athlete_map = {
    "2": ["Testy", "McTest"],
    "3": ["Johnny", "Test"],
    "4": ["Kevin", "McAttester"],
}

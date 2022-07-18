import requests

import config
from qira_controller import QiraController


class Server:

    def __init__(self):
        self._qira_controller = QiraController(

from time import sleep
from qira_controller import QiraController, Trampoline
from config import QiraConfig

qc = QiraController(
    QiraConfig.EXE_PATH,
    QiraConfig.WINDOW_TITLE,
    QiraConfig.ADDRESS,
    QiraConfig.WINDOW_SIZE,
    QiraConfig.WINDOW_POSITION,
    QiraConfig.TRAMPOLINE_SELECTOR_POSITION,
    QiraConfig.TRAMPOLINE_1_POSITION,
    QiraConfig.TRAMPOLINE_2_POSITION,
    QiraConfig.TRAMPOLINE_12_POSITION,
    QiraConfig.TRAMPOLINE_AUTO_POSITION,
)

def test_run(qc):
    qc.ready()
    qc.send_routine_meta('Testy', 'McTest')
    qc.start()
    sleep(10)
    qc.routine()
    sleep(15)
    qc.review()
    qc.ready()



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

def test_run(qc, tramp):
    print("Ready")
    qc.ready()
    print("Send routine meta")
    qc.send_routine_meta('Testy', 'McTest')
    print("Select trampoline")
    qc.select_trampoline(tramp)
    print("Start")
    qc.start()
    sleep(10)
    print("Routine")
    qc.routine()
    sleep(15)
    print("Review")
    qc.review()
    sleep(5)
    print("Ready")
    qc.ready()


def test_run_2(qc, tramp):
    print("Ready")
    qc.ready()
    print("Send routine meta Testy McTest")
    qc.send_routine_meta('Testy', 'McTest')
    print("Select trampoline")
    qc.select_trampoline(tramp)
    print("Start")
    qc.start()
    sleep(5)
    print("Routine")
    qc.routine()
    sleep(12)
    print("Review")
    qc.review()
    sleep(10)

    print("Ready")
    qc.ready()
    print("Send routine meta Fancy Test")
    qc.send_routine_meta('Fancy', 'Test')
    print("Select trampoline")
    qc.select_trampoline(tramp)
    print("Start")
    qc.start()
    sleep(5)
    print("Routine")
    qc.routine()
    sleep(12)
    print("Review")
    qc.review()
    sleep(10)

    print("Ready")
    qc.ready()


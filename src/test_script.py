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
    QiraConfig.DIAGNOSIS_STATE_COLOR
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


def test_run_2(qc, tramp1, tramp2):
    print("Ready")
    qc.ready()
    print("Send routine meta Testy McTest")
    qc.send_routine_meta('Testy', 'McTest')
    print("Select trampoline")
    qc.select_trampoline(tramp1)
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
    qc.select_trampoline(tramp2)
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

def test_remote(qc):

    def on_press(key):
        try:
            k = key.char
        except:
            k = key.name

        if k in [f'{i}' for i in range(10)]:
            atheles = {'1': ('Testy', 'McTest'), '2': ('Fancy', 'Tester')}
            qc.send_routine_meta(*athletes[k], timestamp=42)
        elif k == 'media_play_pause':
            qc.change_state()
        elif k == 'media_previous':
            qc.select_trampoline(Trampoline.ONE)
        elif k == 'media_next':
            qc.select_trampoline(Trampoline.TWO)


    listener = keyboard.Listener(on_press=on_press)
    listener.start()
    listener.join()


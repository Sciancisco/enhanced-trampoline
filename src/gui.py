from tkinter import Tk
import tkinter.ttk as ttk

from config import CameraConfig, QiraConfig, ServerConfig
from server import Server


root = Tk()
server = Server(qira_controller_config=QiraConfig, camera_recorder_config=CameraConfig, **ServerConfig)


def restart():
    server.stop()
    server.start()


def live_feed():
    print("TBD.")


def kill_all():
    server.stop()
    root.destroy()


frame = ttk.Frame(root, padding=10)
frame.grid()

ttk.Label(frame, text="Server").grid(column=0, row=0)
ttk.Button(frame, text="Start", command=server.start).grid(column=1, row=0)
ttk.Button(frame, text="Stop", command=server.stop).grid(column=2, row=0)
ttk.Button(frame, text="Restart", command=restart).grid(column=3, row=0)

ttk.Label(frame, text="Camera").grid(column=0, row=1)
ttk.Button(frame, text="Live feed", command=live_feed).grid(column=1, row=1)

root.title("INS enhanced trampoline")
root.protocol("WM_DELETE_WINDOW", kill_all)
root.mainloop()

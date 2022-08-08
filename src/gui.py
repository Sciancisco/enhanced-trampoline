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

ttk.Label(frame, text="Server").grid(0, 0)
ttk.Button(frame, text="Start", command=server.start).grid(1, 0)
ttk.Button(frame, text="Stop", command=server.stop).grid(2, 0)
ttk.Button(frame, text="Restart", command=restart).grid(3, 0)

ttk.Label(frame, text="Camera").grid(0, 1)
ttk.Button(frame, text="Live feed", command=live_feed).grid(1, 1)

ttk.Button(frame, text="Quit", command=kill_all).grid(2, 0)

root.mainloop()

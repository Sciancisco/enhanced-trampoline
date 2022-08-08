from threading import Event, Thread
import time
from tkinter import Tk
import tkinter.ttk as ttk

import cv2

from config import CameraConfig, QiraConfig, ServerConfig
from server import Server


root = Tk()
server = Server(qira_controller_config=QiraConfig, camera_recorder_config=CameraConfig, **ServerConfig)

live_feed_thread = None
live_feed_on = Event()


def restart():
    server.stop()
    server.start()


def live_feed_toggle():
    global live_feed_thread
    if live_feed_thread and live_feed_thread.is_alive():
        btn_live_feed.config(text="Start live feed")
        live_feed_on.unset()
    else:
        btn_live_feed.config(text="Stop live feed")
        live_feed_on.set()
        live_feed_thread = Thread(target=display_live_feed)
        live_feed_thread.start()


def display_live_feed():
    while live_feed_on.is_set():
        cv2.imshow(server.last_recorded_frame)
        time.sleep(1 / 30)

    cv2.destroyAllWindows()


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
btn_live_feed = ttk.Button(frame, text="Start live feed", command=live_feed_toggle).grid(column=1, row=1)

root.title("INS enhanced trampoline")
root.protocol("WM_DELETE_WINDOW", kill_all)
root.mainloop()

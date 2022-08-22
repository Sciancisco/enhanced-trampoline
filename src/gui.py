from threading import Event, Thread
import time
from tkinter import Tk
import tkinter.ttk as ttk

import cv2

from config import CameraConfig, QiraConfig, ServerConfig
from server import Server


root = Tk()


use_cam = True
server = None


def start_server():
    global server
    if server is None:
        server = Server(qira_controller_config=QiraConfig, camera_recorder_config=CameraConfig, use_cam=use_cam, **ServerConfig)
        server.start()


def stop_server():
    global server
    if server is not None:
        server.stop()
        server = None

def use_cam_toggle():
    global use_cam
    if use_cam:
        btn_use_cam.config(text="No")
        use_cam = False
    else:
        btn_use_cam.config(text="Yes")
        use_cam = True


def kill_all():
    stop_server()
    root.destroy()


frame = ttk.Frame(root, padding=10)
frame.grid()

ttk.Label(frame, text="Server").grid(column=0, row=0)
ttk.Button(frame, text="Start", command=start_server).grid(column=1, row=0)
ttk.Button(frame, text="Stop", command=stop_server).grid(column=2, row=0)
ttk.Label(frame, text="Use camera").grid(column=0, row=1)
btn_use_cam = ttk.Button(frame, text="Yes", command=use_cam_toggle)
btn_use_cam.grid(column=1, row=1)

root.title("Remote Qira")
root.protocol("WM_DELETE_WINDOW", kill_all)
root.mainloop()

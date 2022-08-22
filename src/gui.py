from threading import Event, Thread
import time
from tkinter import Tk, TopLevel, filedialog
import tkinter.ttk as ttk

import cv2

from _logging import get_console_logger
from config import CameraConfig, QiraConfig, ServerConfig
from server import Server


logger = get_console_logger(__name__)
root = Tk()


use_cam = True
server = None


def start_server():
    logger.info(f"Start server with camera set to '{use_cam}'.")
    global server
    if server is None:
        server = Server(
            qira_controller_config=QiraConfig, camera_recorder_config=CameraConfig, use_cam=use_cam, **ServerConfig
        )
        server.start()


def stop_server():
    logger.info("Stop server.")
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
    logger.info(f"Toggled camera to '{use_cam}'.")


def load_athlete_csv():
    logger.info("Load athletes.")
    global server
    filename = filedialog.askopenfilename(
        initialdir="/", title="Select file", filetypes=[("CSV", "*.csv"), ("All TXT files", "*.txt")]
    )
    try:
        server.load_athlete_csv(filename)
        logger.info("Loaded athletes.")
    except Exception as e:
        logger.exception(f"Error occured when loading '{filename}'.")
        popup = TopLevel(root)
        popup.grid()
        popup.title("Error!")
        ttk.Label(popup, text=f"Error occured when loading '{filename}': {e}").grid(column=0, row=0)


def kill_all():
    stop_server()
    root.destroy()
    logger.info("Quitted GUI.")


frame = ttk.Frame(root, padding=10)
frame.grid()

ttk.Label(frame, text="Server").grid(column=0, row=0)
ttk.Button(frame, text="Start", command=start_server).grid(column=1, row=0)
ttk.Button(frame, text="Stop", command=stop_server).grid(column=2, row=0)

ttk.Label(frame, text="Use camera").grid(column=0, row=1)
btn_use_cam = ttk.Button(frame, text="Yes", command=use_cam_toggle)
btn_use_cam.grid(column=1, row=1)

ttk.Label(frame, text="Athletes").grid(column=0, row=2)
ttk.Button(frame, text="Load athletes", command=load_athlete_csv).grid(column=1, row=2)

root.title("Remote Qira")
root.protocol("WM_DELETE_WINDOW", kill_all)

logger.info("Entered GUI.")
root.mainloop()

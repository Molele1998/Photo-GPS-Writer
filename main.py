# -*- coding: utf-8 -*-
import os
import sys

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    sys.path.insert(0, sys._MEIPASS)

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
from datetime import datetime, timezone
from photo_gps_app import PhotoGPSApp

def main():
    app = PhotoGPSApp()
    app.run()

if __name__ == "__main__":
    main()

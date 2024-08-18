import tkinter as tk
from tkinter import ttk

from bober.src.fe.base_fe import BaseUI


class BaseWindow(tk.Toplevel, BaseUI):
    def __init__(self, parent, title, session=None):
        super().__init__(parent)
        self.parent = parent
        self.session = session
        self.title(title)

        # Make this window modal
        self.transient(parent)

        # Set a default size
        self.geometry("1000x750")

        # Create a main frame to hold all widgets
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

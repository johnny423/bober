from tkinter import ttk

from bober.src.fe.base_ui import BaseUI


class BaseTab(ttk.Frame, BaseUI):
    def __init__(self, parent, session):
        super().__init__(parent)
        self.parent = parent
        self.session = session
        self.create_widgets()

    def create_widgets(self):
        # This method should be overridden by subclasses
        pass

    def reload_tab(self):
        pass

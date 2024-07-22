import tkinter as tk

from bober.src.fe.windows import utils
from bober.src.fe.windows.load_file_window import LoadFileWindow


class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Main Window")
        utils.create_button(self, "Load new file", self.open_load_file_window,)
        utils.create_button(self, "Find document", utils.dummy_button_command)
        utils.create_button(self, "Word index", utils.dummy_button_command)
        utils.create_button(self, "Find word by index", utils.dummy_button_command)
        utils.create_button(self, "Manage word groups", utils.dummy_button_command)
        utils.create_button(self, "Manage linguistic expressions", utils.dummy_button_command)
        utils.create_button(self, "Exit", self.destroy)

    def open_load_file_window(self):
        LoadFileWindow(self)

import tkinter as tk

from bober.src.fe.windows import utils
from bober.src.fe.windows.load_file_window import LoadFileWindow


class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Main Window")
        utils.add_button(self, "Load new file", self.open_load_file_window, 0, 0)
        utils.add_button(self, "Find document", utils.dummy_button_command, 1, 0)
        utils.add_button(self, "Word index", utils.dummy_button_command, 2, 0)
        utils.add_button(self, "Find word by index", utils.dummy_button_command, 3, 0)
        utils.add_button(self, "Manage word groups", utils.dummy_button_command, 4, 0)
        utils.add_button(self, "Manage linguistic expressions", utils.dummy_button_command, 5, 0)

        # Add a close button
        utils.add_button(self, "Exit", self.destroy, 6, 0)
        # close_button.pack(pady=10)

    def open_load_file_window(self):
        LoadFileWindow(self)

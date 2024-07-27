import tkinter as tk
from functools import partial

from bober.src.fe.windows.index_search_window import IndexSearchWindow
from bober.src.fe.windows.word_groups_window import WordGroupManager
from bober.src.fe.windows.word_index_window import WordIndexWindow
from bober.src.loader import load_single_file
from bober.src.fe.windows import utils
from bober.src.fe.windows.load_file_window import LoadFileWindow


class MainWindow(tk.Tk):
    def __init__(self, session):
        super().__init__()
        self.session = session
        self.title("Main Window")
        utils.create_button(self, "Load new file", self.open_load_file_window)
        utils.create_button(self, "Find document", utils.dummy_button_command)  # todo
        utils.create_button(self, "Word index", self.open_word_index)
        utils.create_button(self, "Find word by index", self.open_index_search)  # todo
        utils.create_button(self, "Manage word groups", self.open_word_group_manager)
        utils.create_button(self, "Manage linguistic expressions", utils.dummy_button_command)  # todo
        utils.create_button(self, "Exit", self.destroy)

    def open_load_file_window(self):
        def load_file_callback(*args):
            return load_single_file(self.session, *args)

        LoadFileWindow(self, load_file_callback)

    def open_word_index(self):
        WordIndexWindow(self, self.session)

    def open_word_group_manager(self):
        WordGroupManager(self, self.session)

    def open_index_search(self):
        IndexSearchWindow(self, self.session)


def launch_gui(session):
    app = MainWindow(session)
    app.mainloop()


if __name__ == "__main__":
    launch_gui(None)  # can raise an error downstream, only for dev/debug

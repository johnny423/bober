import tkinter as tk

from bober.src.fe import utils
from bober.src.fe.windows.index_search_window import IndexSearchWindow
from bober.src.fe.windows.load_file_window import LoadFileWindow
from bober.src.fe.windows.phrases_window import LinguisticPhraseManager
from bober.src.fe.windows.search_file_window import SearchFileWindow
from bober.src.fe.windows.word_groups_window import WordGroupManager
from bober.src.fe.windows.word_index_window import WordIndexWindow


class MainWindow(tk.Tk):
    def __init__(self, session):
        super().__init__()
        self.session = session
        self.title("Main Window")
        utils.create_button(
            self, "Load new file", lambda: LoadFileWindow(self, self.session)
        )
        utils.create_button(
            self, "Find document", lambda: SearchFileWindow(self, self.session)
        )
        utils.create_button(
            self, "Word index", lambda: WordIndexWindow(self, self.session)
        )
        utils.create_button(
            self,
            "Find word by index",
            lambda: IndexSearchWindow(self, self.session),
        )
        utils.create_button(
            self,
            "Manage word groups",
            lambda: WordGroupManager(self, self.session),
        )
        utils.create_button(
            self,
            "Manage linguistic expressions",
            lambda: LinguisticPhraseManager(self, self.session),
        )


def launch_gui(session):
    app = MainWindow(session)
    app.mainloop()


if __name__ == "__main__":
    launch_gui(None)  # can raise an error downstream, only for dev/debug

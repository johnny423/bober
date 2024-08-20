import tkinter as tk
from tkinter import ttk

from bober.src.fe.tabs.index_search_tab import (
    AbsPosSearchTab,
    RelativePosSearchTab,
)
from bober.src.fe.tabs.load_file_tab import LoadFileTab
from bober.src.fe.tabs.phrases_tab import PhrasesTab
from bober.src.fe.tabs.search_file_tab import SearchFileTab
from bober.src.fe.tabs.word_group_tab import WordGroupTab
from bober.src.fe.tabs.word_index_tab import WordIndexTab


class MainApplication(tk.Tk):
    def __init__(self, session):
        super().__init__()
        self.session = session
        self.title("RFC Explorer")
        self.geometry("1000x750")

        # Create the notebook (tab controller)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Create tabs
        self.create_tabs()

    def create_tabs(self):
        self.notebook.add(
            SearchFileTab(self.notebook, self.session), text="Search File"
        )

        self.notebook.add(
            WordIndexTab(self.notebook, self.session), text="Word Index"
        )

        self.notebook.add(
            AbsPosSearchTab(self.notebook, self.session),
            text="Absolute Position Search",
        )

        self.notebook.add(
            RelativePosSearchTab(self.notebook, self.session),
            text="Relative Position Search",
        )

        self.notebook.add(
            LoadFileTab(self.notebook, self.session), text="Load File"
        )

        self.notebook.add(
            WordGroupTab(self.notebook, self.session), text="Manage Groups"
        )

        self.notebook.add(
            PhrasesTab(self.notebook, self.session), text="Manage Phrases"
        )


def launch_gui(session):
    app = MainApplication(session)
    app.mainloop()


if __name__ == "__main__":
    launch_gui(None)  # can raise an error downstream, only for dev/debug

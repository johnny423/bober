import tkinter as tk
from tkinter import ttk

from loguru import logger

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

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.create_tabs()

    def create_tab(self, tab_cls, text):
        self.notebook.add(tab_cls(self.notebook, self.session), text=text)

    def create_tabs(self):
        tabs = [
            (SearchFileTab, "Search File"),
            (WordIndexTab, "Word Index"),
            (AbsPosSearchTab, "Absolute Position Search"),
            (RelativePosSearchTab, "Relative Position Search"),
            (LoadFileTab, "Load File"),
            (WordGroupTab, "Manage Groups"),
            (PhrasesTab, "Manage Phrases"),
        ]

        for tab_cls, text in tabs:
            self.create_tab(tab_cls, text)
            logger.info(f"Load tab '{text}' finished")


def launch_gui(session):
    app = MainApplication(session)
    app.mainloop()


if __name__ == "__main__":
    launch_gui(None)  # can raise an error downstream, only for dev/debug

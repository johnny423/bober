import tkinter as tk
from tkinter import filedialog, messagebox
from datetime import datetime

from sqlalchemy.orm import Session

from bober.src.fe.windows.utils import create_button, create_label, add_dict_display, highlight_token, ellipsis_around
from bober.src.search.words_index import query_word_index


class WordIndexWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("word index")

        # Make this window modal
        self.grab_set()
        self.transient(parent)

        self.title_entry = tk.Entry(self)
        self.title_entry.pack(pady=5)

        example_dict = get_word_occurrences(parent.session)
        add_dict_display(self, example_dict, "token", "bla")


def get_word_occurrences(session: Session) -> dict[str, dict[str, dict[str, str]]]:
    word_index = query_word_index(session)

    formatted_result = {}
    for token, word_data in word_index.items():
        formatted_token = f"{token} ({word_data.total_count} occurrences)"
        formatted_result[formatted_token] = {}

        for rfc_num, rfc_data in word_data.rfc_occurrences.items():
            formatted_title = f"{rfc_data.title} ({rfc_data.count} occurrences)"
            formatted_result[formatted_token][formatted_title] = {}

            for occurrence in rfc_data.occurrences:
                position_key = (f"section {occurrence.section_index}, "
                                f"word {occurrence.row} ; "  # todo: add the token index to parsing
                                f"page {occurrence.page}, row {occurrence.row}")

                # todo: add token position in the content so we can reach it easily
                shorten = highlight_token(
                    occurrence.context,
                    token,
                    50
                )
                formatted_result[formatted_token][formatted_title][position_key] = shorten

    return formatted_result

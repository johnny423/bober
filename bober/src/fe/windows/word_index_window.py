import tkinter as tk

from sqlalchemy.orm import Session

from bober.src.fe.windows.utils import add_dict_display, ellipsis_around
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
    for stem, word_data in word_index.items():
        formatted_token = f"{stem} ({word_data.total_count} occurrences)"
        formatted_result[formatted_token] = {}

        for rfc_num, rfc_data in word_data.rfc_occurrences.items():
            formatted_title = f"{rfc_data.title} ({rfc_data.count} occurrences)"
            formatted_result[formatted_token][formatted_title] = {}

            for occurrence in rfc_data.occurrences:
                position_key = (f"section {occurrence.section_index}, "
                                f"word {occurrence.index + 1} ; "
                                f"page {occurrence.page}, row {occurrence.row}")

                # todo: still have bugs with this
                shorten = ellipsis_around(
                    occurrence.context,
                    occurrence.position,
                    50
                )
                formatted_result[formatted_token][formatted_title][position_key] = shorten

    return formatted_result

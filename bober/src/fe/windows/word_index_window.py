import tkinter as tk
from tkinter import ttk

from sqlalchemy.orm import Session

from bober.src.fe.windows.rfc_window import RFCWindow
from bober.src.fe.windows.utils import ellipsis_around, add_dict_display, create_scroll_region
from bober.src.search.rfc_content import fetch_rfc_sections, rebuild_content
from bober.src.search.words_index import query_words_index, SortBy, SortOrder, WordIndex


class WordIndexWindow(tk.Toplevel):
    def __init__(self, parent, session: Session):
        super().__init__(parent)
        self.session = session
        self.title("Word Index")

        # Make this window modal
        self.grab_set()
        self.transient(parent)

        self.create_widgets()

        # Initial results display
        self.update_results()

    def create_widgets(self):
        # Token Groups Filter
        self.token_groups_label = tk.Label(self, text="Token Groups:")
        self.token_groups_label.pack(pady=5)
        self.token_groups_entry = tk.Entry(self)
        self.token_groups_entry.pack(pady=5)
        # RFC Titles Filter
        self.rfc_titles_label = tk.Label(self, text="RFC Titles:")
        self.rfc_titles_label.pack(pady=5)
        self.rfc_titles_entry = tk.Entry(self)
        self.rfc_titles_entry.pack(pady=5)
        # Partial Token Filter
        self.partial_token_label = tk.Label(self, text="Partial Token:")
        self.partial_token_label.pack(pady=5)
        self.partial_token_entry = tk.Entry(self)
        self.partial_token_entry.pack(pady=5)
        # Sort By Option
        self.sort_by_label = tk.Label(self, text="Sort By:")
        self.sort_by_label.pack(pady=5)
        self.sort_by_combobox = ttk.Combobox(self, values=list(SortBy))
        self.sort_by_combobox.set(SortBy.OCCURRENCES.value)
        self.sort_by_combobox.pack(pady=5)
        # Sort Order Option
        self.sort_order_label = tk.Label(self, text="Sort Order:")
        self.sort_order_label.pack(pady=5)
        self.sort_order_combobox = ttk.Combobox(self, values=list(SortOrder))
        self.sort_order_combobox.set(SortOrder.DESC.value)
        self.sort_order_combobox.pack(pady=5)
        # Results Display
        self.results_frame = tk.Frame(self)
        self.results_frame.pack(pady=5, fill=tk.BOTH, expand=True)
        # Bind entries and comboboxes to update results on change
        self.token_groups_entry.bind("<KeyRelease>", self.update_results)
        self.rfc_titles_entry.bind("<KeyRelease>", self.update_results)
        self.partial_token_entry.bind("<KeyRelease>", self.update_results)
        self.sort_by_combobox.bind("<<ComboboxSelected>>", self.update_results)
        self.sort_order_combobox.bind("<<ComboboxSelected>>", self.update_results)

    def update_results(self, event=None):
        # todo: would probably be better if we would fetch groups
        token_groups = self.token_groups_entry.get().split() or None
        rfc_title = self.rfc_titles_entry.get() or None
        partial_token = self.partial_token_entry.get() or None
        sort_by = SortBy(self.sort_by_combobox.get())
        sort_order = SortOrder(self.sort_order_combobox.get())

        # Get word occurrences based on current filters and sorting
        words_index = query_words_index(
            self.session,
            token_groups,
            rfc_title,
            partial_token,
            sort_by,
            sort_order
        )

        # clear and reload
        for child in self.results_frame.winfo_children():
            child.destroy()

        add_dict_display(
            self.results_frame,
            dictionary=self._setup_for_display(words_index),
            key_header="what?",  # todo: better
            value_header="the hell?",  # todo: better
            callback=self.do
        )

    @staticmethod
    def _setup_for_display(word_index: dict[str, WordIndex]) -> dict[str, dict[str, dict[str, str]]]:
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

                    shorten = ellipsis_around(
                        occurrence.context,
                        occurrence.start_position,
                        occurrence.end_position,
                        50
                    )

                    formatted_result[formatted_token][formatted_title][position_key] = (
                        shorten, rfc_num, word_data.token)

        return formatted_result

    def do(self, rfc, token):
        RFCWindow(self, self.session, int(rfc), token)

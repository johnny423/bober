from tkinter import ttk

from bober.src.fe.base_window import BaseWindow
from bober.src.fe.windows.rfc_window import RFCWindow
from bober.src.fe.windows.search_results import SearchResults
from bober.src.search.words_index import (
    SortBy,
    SortOrder,
    query_words_index,
)


class WordIndexWindow(BaseWindow):
    token_groups_entry: ttk.Entry
    rfc_titles_entry: ttk.Entry
    partial_token_entry: ttk.Entry
    sort_by_combobox: ttk.Combobox
    sort_order_combobox: ttk.Combobox
    results_frame: ttk.Frame

    def __init__(self, parent, session):
        super().__init__(parent, "Word Index", session)
        self.create_widgets()
        self.update_results()

    def create_widgets(self):
        self.token_groups_entry = self.create_entry(self.main_frame, "Token Groups:")
        self.rfc_titles_entry = self.create_entry(self.main_frame, "RFC Titles:")
        self.partial_token_entry = self.create_entry(self.main_frame, "Partial Token:")

        self.sort_by_combobox = self.create_combobox(self.main_frame, "Sort By:", list(SortBy))
        self.sort_by_combobox.set(SortBy.OCCURRENCES.value)

        self.sort_order_combobox = self.create_combobox(self.main_frame, "Sort Order:", list(SortOrder))
        self.sort_order_combobox.set(SortOrder.DESC.value)

# Create SearchResults instance
        columns = {
            "word": ("Word", 200),
            "rfc_title": ("RFC Title", 300),
            "occurrences": ("Occurrences", 100),
            "context": ("Context", 400)
        }
        self.search_results = SearchResults(self.main_frame, columns, self.open_rfc_window)

        # Bind entries and comboboxes to update results on change
        self.token_groups_entry.bind("<KeyRelease>", self.update_results)
        self.rfc_titles_entry.bind("<KeyRelease>", self.update_results)
        self.partial_token_entry.bind("<KeyRelease>", self.update_results)
        self.sort_by_combobox.bind("<<ComboboxSelected>>", self.update_results)
        self.sort_order_combobox.bind("<<ComboboxSelected>>", self.update_results)

    def update_results(self, event=None):
        token_groups = self.token_groups_entry.get().split() or None
        rfc_title = self.rfc_titles_entry.get() or None
        partial_token = self.partial_token_entry.get() or None
        sort_by = SortBy(self.sort_by_combobox.get())
        sort_order = SortOrder(self.sort_order_combobox.get())

        words_index = query_words_index(
            self.session,
            token_groups,
            rfc_title,
            partial_token,
            sort_by,
            sort_order,
        )

        self.display_search_results(words_index)

    def display_search_results(self, words_index):
        results = []
        for stem, word_data in words_index.items():
            for rfc_num, rfc_data in word_data.rfc_occurrences.items():
                for occurrence in rfc_data.occurrences:
                    results.append({
                        "word": stem,
                        "rfc_title": rfc_data.title,
                        "occurrences": rfc_data.count,
                        "context": occurrence.context,
                        "rfc_num": rfc_num,
                        "token": word_data.token,
                        "line_id": occurrence.line_id
                    })
        self.search_results.display_results(results)

    def open_rfc_window(self, values):
        rfc_num = int(values[4])  # Assuming rfc_num is the 5th value
        token = values[5]
        line_id = int(values[6])
        RFCWindow(self, self.session, rfc_num, token=token, line_id=line_id)

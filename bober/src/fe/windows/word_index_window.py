from tkinter import ttk

from bober.src.fe.base_window import BaseWindow
from bober.src.fe.windows.rfc_window import RFCWindow
from bober.src.fe.windows.utils import add_dict_display, ellipsis_around
from bober.src.search.words_index import SortBy, SortOrder, WordIndex, query_words_index


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

        self.results_frame = ttk.Frame(self.main_frame)
        self.results_frame.pack(pady=5, fill="both", expand=True)

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

        for child in self.results_frame.winfo_children():
            child.destroy()

        add_dict_display(
            self.results_frame,
            dictionary=self._setup_for_display(words_index),
            key_header="what?",  # todo: better
            value_header="the hell?",  # todo: better
            callback=self.load_rfc_window,
        )

    @staticmethod
    def _setup_for_display(
            word_index: dict[str, WordIndex]
    ) -> dict[str, dict[str, dict[str, str]]]:
        formatted_result = {}
        for stem, word_data in word_index.items():
            formatted_token = f"{stem} ({word_data.total_count} occurrences)"
            formatted_result[formatted_token] = {}

            for rfc_num, rfc_data in word_data.rfc_occurrences.items():
                formatted_title = f"{rfc_data.title} ({rfc_data.count} occurrences)"
                formatted_result[formatted_token][formatted_title] = {}

                for occurrence in rfc_data.occurrences:
                    position_key = (
                        f"section {occurrence.section_index}, "
                        f"word {occurrence.index + 1} ; "
                        f"page {occurrence.page}, row {occurrence.row}"
                    )

                    shorten = ellipsis_around(
                        occurrence.context,
                        occurrence.start_position,
                        occurrence.end_position,
                        50,
                    )

                    formatted_result[formatted_token][formatted_title][position_key] = (
                        shorten, rfc_num, word_data.token)

        return formatted_result

    def load_rfc_window(self, rfc, token):
        RFCWindow(self, self.session, int(rfc), token)

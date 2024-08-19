import tkinter as tk
from tkinter import ttk
from typing import Any

from bober.src.fe.tabs.base_tab import BaseTab
from bober.src.fe.utils import ellipsis_around
from bober.src.fe.windows.rfc_window import RFCWindow
from bober.src.search.words_index import (
    SortBy,
    SortOrder,
    query_words_index,
)


class WordIndexTab(BaseTab):

    def create_widgets(self):
        self.token_groups_entry = self.create_entry(self, "Token Groups:")
        self.rfc_titles_entry = self.create_entry(self, "RFC Titles:")
        self.partial_token_entry = self.create_entry(self, "Partial Token:")

        self.sort_by_combobox = self.create_combobox(
            self, "Sort By:", list(SortBy)
        )
        self.sort_by_combobox.set(SortBy.OCCURRENCES.value)

        self.sort_order_combobox = self.create_combobox(
            self, "Sort Order:", list(SortOrder)
        )
        self.sort_order_combobox.set(SortOrder.DESC.value)

        self.results_frame = ttk.Frame(self)
        self.results_frame.pack(pady=5, fill="both", expand=True)

        # Bind entries and comboboxes to update results on change
        self.token_groups_entry.bind("<KeyRelease>", self.update_results)
        self.rfc_titles_entry.bind("<KeyRelease>", self.update_results)
        self.partial_token_entry.bind("<KeyRelease>", self.update_results)
        self.sort_by_combobox.bind("<<ComboboxSelected>>", self.update_results)
        self.sort_order_combobox.bind(
            "<<ComboboxSelected>>", self.update_results
        )

        self.update_results()

    def update_results(self, event=None):

        for child in self.results_frame.winfo_children():
            child.destroy()

        frame = ttk.Frame(self.results_frame, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)

        self.tree = ttk.Treeview(
            frame, columns=("Value",), show="tree headings"
        )
        self.tree.heading("#0", text="word")
        self.tree.heading("Value", text="content")
        self.tree.pack(fill=tk.BOTH, expand=True)

        self.word_index = self._query_index()
        self.nodes = {}
        for stem, word_data in self.word_index.items():
            text = f"{stem} ({word_data.total_count} occurrences)"
            node = self.tree.insert('', 'end', text=text, open=False)
            self.tree.insert(node, 'end')

            self.nodes[node] = stem

        self.tree.bind('<<TreeviewOpen>>', self.open_node)
        self.tree.bind("<Double-1>", self.load_rfc_window)

    def _query_index(self):
        token_groups = self.token_groups_entry.get().split() or None
        rfc_title = self.rfc_titles_entry.get() or None
        partial_token = self.partial_token_entry.get() or None
        sort_by = SortBy(self.sort_by_combobox.get())
        sort_order = SortOrder(self.sort_order_combobox.get())

        return query_words_index(
            self.session,
            token_groups,
            rfc_title,
            partial_token,
            sort_by,
            sort_order,
        )

    def open_node(self, event=None):
        node = self.tree.focus()
        stem = self.nodes.pop(node, None)
        if not stem:
            # node is already opened
            return

        self.tree.delete(self.tree.get_children(node))
        display = self._to_display(self.word_index[stem])
        self._populate_tree(display, node)

    @staticmethod
    def _to_display(word_data):
        display = {}
        for rfc_num, rfc_data in word_data.rfc_occurrences.items():
            formatted_title = f"{rfc_data.title} ({rfc_data.count} occurrences)"
            display[formatted_title] = {}
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
                display[formatted_title][position_key] = (
                    shorten,
                    rfc_num,
                    word_data.token,
                    occurrence.abs_line,
                )
        return display

    def load_rfc_window(self, event):
        item = self.tree.identify('item', event.x, event.y)
        if item and 'leaf' in self.tree.item(item, 'tags'):
            values = self.tree.item(item, 'values')
            (_, rfc, token, abs_line) = values
            RFCWindow(
                self.winfo_toplevel(),
                self.session,
                int(rfc),
                token=token,
                abs_line=int(abs_line),
            )

    def _populate_tree(self, data: Any, parent: str = '') -> None:
        if isinstance(data, dict):
            for key, value in data.items():
                node = self.tree.insert(parent, 'end', text=str(key))
                self._populate_tree(value, node)
        else:
            node = self.tree.insert(parent, 'end', text='', values=data)
            self.tree.item(node, tags=('leaf',))

import datetime
import tkinter as tk
from contextlib import contextmanager
from tkinter import Label, ttk

from bober.src.fe.tabs.base_tab import BaseTab
from bober.src.fe.windows.rfc_window import RFCWindow
from bober.src.search.words_index import (
    SortBy,
    SortOrder,
    fetch_occurrences,
    fetch_rfc_occurrences,
    query_filtered_words,
)


@contextmanager
def time_me(name):
    start = datetime.datetime.now()
    yield
    end = datetime.datetime.now()
    delta = end - start
    print(f"->> [{start}] Time {name} {delta.total_seconds()}")


class WordIndexTab(BaseTab):
    def __init__(self, parent, session):
        super().__init__(parent, session)
        self.update_results()

    def create_widgets(self):
        # todo: load options from existing groups and update when group changes
        self.token_groups_entry = self.create_entry(self, "Token Groups:")

        # todo: load options from existing rfcs and update when added
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

        # Create a label to show the number of words displayed
        self.words_count_label = Label(self, text="")
        self.words_count_label.pack(pady=5)

        # Bind entries and comboboxes to update results on change
        self.token_groups_entry.bind("<KeyRelease>", self.update_results)
        self.rfc_titles_entry.bind("<KeyRelease>", self.update_results)
        self.partial_token_entry.bind("<KeyRelease>", self.update_results)
        self.sort_by_combobox.bind("<<ComboboxSelected>>", self.update_results)
        self.sort_order_combobox.bind(
            "<<ComboboxSelected>>", self.update_results
        )

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
        self.tree.bind('<<TreeviewOpen>>', self.open_node)
        self.tree.bind("<Double-1>", self.load_rfc_window)

        self.word_nodes = {}
        self.title_nodes = {}
        for stem, count in self._query_words():
            node = self.tree.insert('', 'end', text=f"{stem} ({count} occurrences)")
            self.tree.insert(node, 'end')
            self.word_nodes[node] = stem

    def _query_words(self):
        token_groups = self.token_groups_entry.get().split() or None
        rfc_title = self.rfc_titles_entry.get() or None
        partial_token = self.partial_token_entry.get() or None
        sort_by = SortBy(self.sort_by_combobox.get())
        sort_order = SortOrder(self.sort_order_combobox.get())

        return query_filtered_words(
            self.session,
            token_groups,
            rfc_title,
            partial_token,
            sort_by,
            sort_order,
        )

    def open_node(self, event=None):
        node = self.tree.focus()
        if stem := self.word_nodes.pop(node, None):
            self.tree.delete(self.tree.get_children(node))
            rfc_title = self.rfc_titles_entry.get() or None
            rfc_occurrences = fetch_rfc_occurrences(
                self.session, stem, rfc_title
            )

            for occurrence in rfc_occurrences:
                inner = self.tree.insert(
                    node, 'end', text=f"{occurrence.title} {occurrence.count}"
                )
                self.tree.insert(inner, 'end')
                self.title_nodes[inner] = (stem, occurrence.num)

            return

        if pair := self.title_nodes.pop(node, None):
            (stem, rfc_num) = pair
            self.tree.delete(self.tree.get_children(node))
            occurrences = fetch_occurrences(self.session, stem, rfc_num)
            for occurrence in occurrences:
                text = f"{str(occurrence.abs_pos)}; {str(occurrence.rel_pos)}; page {occurrence.page}"
                inner = self.tree.insert(node, 'end', text=text)
                self.tree.insert(
                    inner,
                    "end",
                    text='',
                    values=(
                        occurrence.context.shorten(50),
                        rfc_num,
                        stem,
                        occurrence.abs_pos.line,
                    ),
                    tags=("leaf",),
                )
            return

    def load_rfc_window(self, event):
        item = self.tree.identify('item', event.x, event.y)
        if item and 'leaf' in self.tree.item(item, 'tags'):
            values = self.tree.item(item, 'values')
            (_, rfc, token, abs_line) = values
            RFCWindow(
                self.winfo_toplevel(),
                self.session,
                int(rfc),
                stem=token,
                abs_line=int(abs_line),
            )

import tkinter as tk
from tkinter import Label, ttk

from bober.src.fe.event_system import EVENT_SYSTEM
from bober.src.fe.events import NEW_GROUP_EVENT, RFC_ADDED_EVENT
from bober.src.fe.tabs.base_tab import BaseTab
from bober.src.fe.windows.rfc_window import RFCWindow
from bober.src.search.rfc_content import get_absolute_positions
from bober.src.search.search_rfc import SearchRFCQuery, search_rfcs
from bober.src.search.words_index import (
    QueryFilteredWordsParams,
    SortBy,
    SortOrder,
    fetch_occurrences,
    fetch_rfc_occurrences,
    query_filtered_words,
)
from bober.src.word_groups.word_groups import list_groups


class WordIndexTab(BaseTab):
    def __init__(self, parent, session):
        super().__init__(parent, session)
        self.current_page = 1
        self.page_size = 50
        self.update_results()
        EVENT_SYSTEM.subscribe(NEW_GROUP_EVENT, self._update_groups)
        EVENT_SYSTEM.subscribe(RFC_ADDED_EVENT, self._update_rfcs)

    def _update_rfcs(self, event=None):
        rfcs = search_rfcs(self.session, SearchRFCQuery())
        self.rfc_titles_entry["values"] = [rfc.title for rfc in rfcs]

    def _update_groups(self, event=None):
        groups = list_groups(self.session)
        self.token_groups_entry["values"] = [
            group.group_name for group in groups
        ]

    def create_widgets(self):
        groups = list_groups(self.session)
        self.token_groups_entry = self.create_combobox(
            self, "Token Groups:", [group.group_name for group in groups]
        )

        rfcs = search_rfcs(self.session, SearchRFCQuery())
        self.rfc_titles_entry = self.create_combobox(
            self, "RFC Titles:", [rfc.title for rfc in rfcs]
        )

        self.partial_token_entry = self.create_entry(self, "Token/Stem:")

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

        # Add pagination controls
        self.pagination_frame = ttk.Frame(self)
        self.pagination_frame.pack(pady=5)

        self.prev_button = ttk.Button(
            self.pagination_frame, text="Previous", command=self.prev_page
        )
        self.prev_button.pack(side=tk.LEFT, padx=5)

        self.page_label = ttk.Label(self.pagination_frame, text="Page 1")
        self.page_label.pack(side=tk.LEFT, padx=5)

        self.next_button = ttk.Button(
            self.pagination_frame, text="Next", command=self.next_page
        )
        self.next_button.pack(side=tk.LEFT, padx=5)

        # Bind entries and comboboxes to update results on change
        self.token_groups_entry.bind(
            "<<ComboboxSelected>>", self.reset_and_update
        )
        self.token_groups_entry.bind("<KeyRelease>", self.reset_and_update)

        self.rfc_titles_entry.bind(
            "<<ComboboxSelected>>", self.reset_and_update
        )
        self.rfc_titles_entry.bind("<KeyRelease>", self.reset_and_update)

        self.partial_token_entry.bind("<KeyRelease>", self.reset_and_update)

        self.sort_by_combobox.bind(
            "<<ComboboxSelected>>", self.reset_and_update
        )
        self.sort_order_combobox.bind(
            "<<ComboboxSelected>>", self.reset_and_update
        )

    def reset_and_update(self, event=None):
        self.current_page = 1
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
        self.tree.bind('<<TreeviewOpen>>', self.open_node)
        self.tree.bind("<Double-1>", self.load_rfc_window)

        self.word_nodes = {}
        self.title_nodes = {}
        results = self._query_words()
        self.words_count_label.config(
            text=f"fetched {len(results.words)} tokens out of {results.total_count} matching"
        )
        for token, stem, count in results.words:
            node = self.tree.insert(
                '', 'end', text=f"{token} ({stem=} ; {count} occurrences)"
            )
            self.tree.insert(node, 'end')
            self.word_nodes[node] = token

        self.update_pagination_controls(results.total_count)

    def update_pagination_controls(self, total_count):
        total_pages = (total_count + self.page_size - 1) // self.page_size
        self.page_label.config(
            text=f"Page {self.current_page} of {total_pages}"
        )
        self.prev_button.config(
            state=tk.NORMAL if self.current_page > 1 else tk.DISABLED
        )
        self.next_button.config(
            state=tk.NORMAL if self.current_page < total_pages else tk.DISABLED
        )

    def prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.update_results()

    def next_page(self):
        self.current_page += 1
        self.update_results()

    def _query_words(self):
        params = QueryFilteredWordsParams(
            token_groups=self.token_groups_entry.get().split() or None,
            rfc_title=self.rfc_titles_entry.get() or None,
            partial_token=self.partial_token_entry.get() or None,
            sort_by=SortBy(self.sort_by_combobox.get()),
            sort_order=SortOrder(self.sort_order_combobox.get()),
            page=self.current_page,
            page_size=self.page_size,
        )

        return query_filtered_words(self.session, params)

    def open_node(self, event=None):
        node = self.tree.focus()
        if token := self.word_nodes.pop(node, None):
            self.tree.delete(self.tree.get_children(node))
            rfc_title = self.rfc_titles_entry.get() or None
            rfc_occurrences = fetch_rfc_occurrences(
                self.session, token, rfc_title
            )

            for occurrence in rfc_occurrences:
                inner = self.tree.insert(
                    node, 'end', text=f"{occurrence.title} {occurrence.count}"
                )
                self.tree.insert(inner, 'end')
                self.title_nodes[inner] = (token, occurrence.num)

            return

        if pair := self.title_nodes.pop(node, None):
            (token, rfc_num) = pair
            self.tree.delete(self.tree.get_children(node))
            occurrences = fetch_occurrences(self.session, token, rfc_num)
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
                        token,
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
            highlights = get_absolute_positions(self.session, rfc, token)
            RFCWindow(
                self.winfo_toplevel(),
                self.session,
                int(rfc),
                highlights=highlights,
                abs_line=int(abs_line),
            )

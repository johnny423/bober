import tkinter as tk
from tkinter import ttk

from bober.src.fe.events import RFC_ADDED_EVENT
from bober.src.fe.tabs.base_tab import BaseTab
from bober.src.fe.windows.rfc_window import RFCWindow
from bober.src.search.index_search import (
    AbsPositionQuery,
    Index2Criteria,
    SearchResult,
    abs_position_search,
    index_2_search,
)
from bober.src.search.search_rfc import SearchRFCQuery, search_rfcs


class IndexSearchTab(BaseTab):

    def __init__(self, parent, session):
        super().__init__(parent, session)
        self.winfo_toplevel().bind(RFC_ADDED_EVENT, self._update_rfcs)

    def create_rfc_dropdown(self, parent):
        frame = ttk.Frame(parent)
        frame.pack(fill="x", pady=5)

        ttk.Label(frame, text="RFC:", width=15).pack(side="left")
        rfc_dropdown = tk.StringVar()
        rfcs = search_rfcs(self.session, SearchRFCQuery())
        rfc_dropdown = ttk.Combobox(
            frame,
            textvariable=rfc_dropdown,
            values=[rfc.title for rfc in rfcs],
        )
        rfc_dropdown.pack(side="left", expand=True, fill="x")
        return rfc_dropdown

    def _update_rfcs(self, event=None):
        rfcs = search_rfcs(self.session, SearchRFCQuery())
        self.rfc_dropdown["values"] = [rfc.title for rfc in rfcs]

    def display_results(self, results: list[SearchResult]):
        self.tree.delete(*self.tree.get_children())
        for result in results:
            item = self.tree.insert(
                "",
                "end",
                values=(
                    result.word,
                    result.context,
                    result.stem,
                    result.rfc,
                    result.abs_line,
                ),
            )
            self.tree.item(item, tags=(item,))

        self.tree.bind("<Double-1>", self._on_item_click)

    def _on_item_click(self, event):
        item = self.tree.identify('item', event.x, event.y)
        (*_, stem, rfc, abs_line) = self.tree.item(item, 'values')
        RFCWindow(
            self.winfo_toplevel(),
            self.session,
            int(rfc),
            stem=stem,
            abs_line=int(abs_line),
        )


class AbsPositionSearch(IndexSearchTab):
    def create_widgets(self):
        input_frame = ttk.Frame(self, padding="10")
        input_frame.pack(fill="x")

        self.rfc_dropdown = self.create_rfc_dropdown(input_frame)
        self.line_entry = self.create_entry(input_frame, "Line:")
        self.column_entry = self.create_entry(input_frame, "Column:")

        results_frame = ttk.Frame(self, padding="10")
        results_frame.pack(fill="both", expand=True)
        self.tree = self.create_treeview(
            results_frame,
            columns=("Word", "Link for source"),
            headings=("Word", "Link for source"),
        )

        self.rfc_dropdown.bind("<<ComboboxSelected>>", self.search)
        self.line_entry.bind("<KeyRelease>", self.search)
        self.column_entry.bind("<KeyRelease>", self.search)

    def search(self, event=None):
        criteria = AbsPositionQuery(
            title=self.rfc_dropdown.get(),
            abs_line=(
                int(self.line_entry.get()) if self.line_entry.get() else None
            ),
            column=(
                int(self.column_entry.get())
                if self.column_entry.get()
                else None
            ),
        )
        results = abs_position_search(self.session, criteria)
        self.display_results(results)


class Index2SearchTab(IndexSearchTab):
    def create_widgets(self):
        input_frame = ttk.Frame(self, padding="10")
        input_frame.pack(fill="x")
        self.rfc_dropdown = self.create_rfc_dropdown(input_frame)
        self.section_entry = self.create_entry(input_frame, "section:")
        self.row_entry = self.create_entry(input_frame, "row:")
        self.position_entry = self.create_entry(input_frame, "position:")

        results_frame = ttk.Frame(self, padding="10")
        results_frame.pack(fill="both", expand=True)
        self.tree = self.create_treeview(
            results_frame,
            columns=("Word", "Link for source"),
            headings=("Word", "Link for source"),
        )

        self.rfc_dropdown.bind("<<ComboboxSelected>>", self.search)
        self.section_entry.bind("<KeyRelease>", self.search)
        self.row_entry.bind("<KeyRelease>", self.search)
        self.position_entry.bind("<KeyRelease>", self.search)

    def search(self, event=None):
        criteria = Index2Criteria(
            title=self.rfc_dropdown.get(),
            section=(
                int(self.section_entry.get())
                if self.section_entry.get()
                else None
            ),
            line_in_section=(
                int(self.row_entry.get()) if self.row_entry.get() else None
            ),
            position_in_line=(
                int(self.position_entry.get())
                if self.position_entry.get()
                else None
            ),
        )
        results = index_2_search(self.session, criteria)
        self.display_results(results)

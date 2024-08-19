import tkinter as tk
from tkinter import ttk

from bober.src.fe.tabs.base_tab import BaseTab
from bober.src.fe.windows.rfc_window import RFCWindow
from bober.src.search.index_search import (
    Index1Criteria,
    Index2Criteria,
    SearchResult,
    index_1_search,
    index_2_search,
)
from bober.src.search.search_rfc import SearchRFCQuery, search_rfcs


class IndexSearchTab(BaseTab):
    # todo: update when added
    def create_rfc_dropdown(self, parent):
        frame = ttk.Frame(parent)
        frame.pack(fill="x", pady=5)

        ttk.Label(frame, text="RFC:", width=15).pack(side="left")
        rfcs = search_rfcs(self.session, SearchRFCQuery())
        rfc_dropdown = tk.StringVar()
        rfc_dropdown = ttk.Combobox(
            frame,
            textvariable=rfc_dropdown,
            values=[rfc.title for rfc in rfcs],
        )
        rfc_dropdown.pack(side="left", expand=True, fill="x")
        return rfc_dropdown

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


class Index1SearchTab(IndexSearchTab):
    def create_widgets(self):
        input_frame = ttk.Frame(self, padding="10")
        input_frame.pack(fill="x")

        self.rfc_dropdown = self.create_rfc_dropdown(input_frame)
        self.page_entry = self.create_entry(input_frame, "Page:")
        self.row_entry = self.create_entry(input_frame, "Row:")
        self.position_entry = self.create_entry(input_frame, "Position:")

        results_frame = ttk.Frame(self, padding="10")
        results_frame.pack(fill="both", expand=True)
        self.tree = self.create_treeview(
            results_frame,
            columns=("Word", "Link for source"),
            headings=("Word", "Link for source"),
        )

        self.rfc_dropdown.bind("<<ComboboxSelected>>", self.search)
        self.page_entry.bind("<KeyRelease>", self.search)
        self.row_entry.bind("<KeyRelease>", self.search)
        self.position_entry.bind("<KeyRelease>", self.search)

    def search(self, event=None):
        criteria = Index1Criteria(
            title=self.rfc_dropdown.get(),
            page=(
                int(self.page_entry.get()) if self.page_entry.get() else None
            ),
            line_in_page=(
                int(self.row_entry.get()) if self.row_entry.get() else None
            ),
            position_in_line=(
                int(self.position_entry.get())
                if self.position_entry.get()
                else None
            ),
        )
        results = index_1_search(self.session, criteria)
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

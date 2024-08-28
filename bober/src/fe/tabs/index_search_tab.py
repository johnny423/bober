import tkinter as tk
from tkinter import ttk

from bober.src.fe.events import RFC_ADDED_EVENT
from bober.src.fe.tabs.base_tab import BaseTab
from bober.src.fe.windows.rfc_window import RFCWindow
from bober.src.search.index_search import (
    AbsPositionQuery,
    PaginatedResults,
    RelativePositionQuery,
    abs_position_search,
    relative_position_search,
)
from bober.src.search.rfc_content import get_absolute_positions
from bober.src.search.search_rfc import SearchRFCQuery, search_rfcs


class IndexSearchTab(BaseTab):
    def __init__(self, parent, session):
        super().__init__(parent, session)
        self.winfo_toplevel().bind(RFC_ADDED_EVENT, self._update_rfcs)
        self.current_page = 1
        self.page_size = 50
        self.update_pagination_controls(
            PaginatedResults(results=[], total_count=0, total_pages=0)
        )

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

    def display_results(self, paginated_results: PaginatedResults):
        self.tree.delete(*self.tree.get_children())
        for result in paginated_results.results:
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
        self.update_pagination_controls(paginated_results)

    def _on_item_click(self, event):
        item = self.tree.identify('item', event.x, event.y)
        (token, _, _, rfc, abs_line) = self.tree.item(item, 'values')
        highlights = get_absolute_positions(self.session, rfc, token)

        RFCWindow(
            self.winfo_toplevel(),
            self.session,
            int(rfc),
            highlights=highlights,
            abs_line=int(abs_line),
        )

    def create_pagination_controls(self, parent):
        frame = ttk.Frame(parent)
        frame.pack(fill="x", pady=5)

        self.prev_button = ttk.Button(
            frame, text="Previous", command=self.prev_page
        )
        self.prev_button.pack(side="left", padx=5)

        self.page_label = ttk.Label(frame, text="Page 1")
        self.page_label.pack(side="left", padx=5)

        self.next_button = ttk.Button(
            frame, text="Next", command=self.next_page
        )
        self.next_button.pack(side="left", padx=5)

    def update_pagination_controls(self, paginated_results: PaginatedResults):
        self.page_label.config(
            text=f"Page {self.current_page} of {paginated_results.total_pages}"
        )
        self.prev_button.config(
            state=tk.NORMAL if self.current_page > 1 else tk.DISABLED
        )
        self.next_button.config(
            state=(
                tk.NORMAL
                if self.current_page < paginated_results.total_pages
                else tk.DISABLED
            )
        )

    def prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.search()

    def next_page(self):
        self.current_page += 1
        self.search()

    def reset_pagination(self):
        self.current_page = 1


class AbsPosSearchTab(IndexSearchTab):
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

        self.create_pagination_controls(self)

        self.rfc_dropdown.bind("<<ComboboxSelected>>", self.reset_and_search)
        self.line_entry.bind("<KeyRelease>", self.reset_and_search)
        self.column_entry.bind("<KeyRelease>", self.reset_and_search)

    def reset_and_search(self, event=None):
        self.reset_pagination()
        self.search()

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
            page=self.current_page,
            page_size=self.page_size,
        )

        if not criteria:
            self.display_results(
                PaginatedResults(results=[], total_count=0, total_pages=0)
            )
            return

        results = abs_position_search(self.session, criteria)
        self.display_results(results)


class RelativePosSearchTab(IndexSearchTab):
    def create_widgets(self):
        input_frame = ttk.Frame(self, padding="10")
        input_frame.pack(fill="x")
        self.rfc_dropdown = self.create_rfc_dropdown(input_frame)
        self.section_entry = self.create_entry(input_frame, "Section:")
        self.line_entry = self.create_entry(input_frame, "Line:")
        self.word_entry = self.create_entry(input_frame, "Word:")

        results_frame = ttk.Frame(self, padding="10")
        results_frame.pack(fill="both", expand=True)
        self.tree = self.create_treeview(
            results_frame,
            columns=("Word", "Link for source"),
            headings=("Word", "Link for source"),
        )

        self.create_pagination_controls(self)

        self.rfc_dropdown.bind("<<ComboboxSelected>>", self.reset_and_search)
        self.section_entry.bind("<KeyRelease>", self.reset_and_search)
        self.line_entry.bind("<KeyRelease>", self.reset_and_search)
        self.word_entry.bind("<KeyRelease>", self.reset_and_search)

    def reset_and_search(self, event=None):
        self.reset_pagination()
        self.search()

    def search(self, event=None):
        criteria = RelativePositionQuery(
            title=self.rfc_dropdown.get(),
            section=(
                int(self.section_entry.get())
                if self.section_entry.get()
                else None
            ),
            line_in_section=(
                int(self.line_entry.get()) if self.line_entry.get() else None
            ),
            word_in_line=(
                int(self.word_entry.get()) if self.word_entry.get() else None
            ),
            page=self.current_page,
            page_size=self.page_size,
        )

        if not criteria:
            self.display_results(
                PaginatedResults(results=[], total_count=0, total_pages=0)
            )
            return

        results = relative_position_search(self.session, criteria)
        self.display_results(results)

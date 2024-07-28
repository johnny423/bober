import tkinter as tk
from tkinter import ttk

from sqlalchemy.orm import Session

from bober.src.search.index_search import (
    Index1Criteria,
    Index2Criteria,
    SearchResult,
    index_1_search,
    index_2_search,
)
from bober.src.search.search_rfc import SearchRFCQuery, search_rfcs


class IndexSearchWindow(tk.Toplevel):
    def __init__(self, master: tk.Tk, session: Session):
        super().__init__(master)

        self.title("Find word by index")
        self.session = session
        self.grab_set()
        self.transient(master)

        self.create_widgets()

    def create_widgets(self):
        # Create frames
        input_frame = ttk.Frame(self, padding="10")
        input_frame.pack(fill=tk.X)

        button_frame = ttk.Frame(self, padding="10")
        button_frame.pack(fill=tk.X)

        results_frame = ttk.Frame(self, padding="10")
        results_frame.pack(fill=tk.BOTH, expand=True)

        # Create input fields

        # Create RFC dropdown
        self.title_var = tk.StringVar()
        self.create_rfc_dropdown(input_frame)

        self.index_1_page_entry = self.create_entry(
            input_frame, "Index 1 page:"
        )
        self.index_1_row_entry = self.create_entry(input_frame, "Index 1 row:")
        self.index_1_position_entry = self.create_entry(
            input_frame, "Index 1 position:"
        )

        self.index_2_section_entry = self.create_entry(
            input_frame, "Index 2 section:"
        )
        self.index_2_row_entry = self.create_entry(input_frame, "Index 2 row:")
        self.index_2_position_entry = self.create_entry(
            input_frame, "Index 2 position:"
        )

        # Create buttons
        ttk.Button(
            button_frame,
            text="Search by index 1",
            command=self.search_by_index_1,
        ).pack(side=tk.LEFT, padx=5)
        ttk.Button(
            button_frame,
            text="Search by index 2",
            command=self.search_by_index_2,
        ).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Back", command=self.master.quit).pack(
            side=tk.LEFT, padx=5
        )

        # Create results table
        self.tree = ttk.Treeview(
            results_frame, columns=("Word", "Link for source"), show="headings"
        )
        self.tree.heading("Word", text="Word")
        self.tree.heading("Link for source", text="Link for source")
        self.tree.pack(fill=tk.BOTH, expand=True)

    def create_entry(self, parent: ttk.Frame, label: str) -> ttk.Entry:
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, pady=5)

        ttk.Label(frame, text=label, width=15).pack(side=tk.LEFT)
        entry = ttk.Entry(frame)
        entry.pack(side=tk.LEFT, expand=True, fill=tk.X)
        return entry

    def create_rfc_dropdown(self, parent: ttk.Frame):
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, pady=5)

        ttk.Label(frame, text="RFC:", width=15).pack(side=tk.LEFT)
        rfcs = search_rfcs(self.session, SearchRFCQuery())
        rfc_dropdown = ttk.Combobox(
            frame,
            textvariable=self.title_var,
            values=[rfc.title for rfc in rfcs],
        )
        rfc_dropdown.pack(side=tk.LEFT, expand=True, fill=tk.X)

    def display_results(self, results: list[SearchResult]):
        self.tree.delete(*self.tree.get_children())
        for result in results:
            self.tree.insert("", "end", values=(result.word, result.context))

    def search_by_index_1(self):
        criteria = Index1Criteria(
            title=self.title_var.get(),
            page=(
                int(self.index_1_page_entry.get())
                if self.index_1_page_entry.get()
                else None
            ),
            line=(
                int(self.index_1_row_entry.get())
                if self.index_1_row_entry.get()
                else None
            ),
            position=(
                int(self.index_1_position_entry.get())
                if self.index_1_position_entry.get()
                else None
            ),
        )
        results = index_1_search(self.session, criteria)
        self.display_results(results)

    def search_by_index_2(self):
        criteria = Index2Criteria(
            title=self.title_var.get(),
            section=(
                int(self.index_2_section_entry.get())
                if self.index_2_section_entry.get()
                else None
            ),
            line=(
                int(self.index_2_row_entry.get())
                if self.index_2_row_entry.get()
                else None
            ),
            position=(
                int(self.index_2_position_entry.get())
                if self.index_2_position_entry.get()
                else None
            ),
        )
        results = index_2_search(self.session, criteria)
        self.display_results(results)

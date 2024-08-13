import tkinter as tk
from tkinter import ttk

from bober.src.fe.base_window import BaseWindow
from bober.src.fe.windows.rfc_window import RFCWindow
from bober.src.fe.windows.search_results import SearchResults
from bober.src.search.index_search import (
    Index1Criteria,
    Index2Criteria,
    SearchResult,
    index_1_search,
    index_2_search,
)
from bober.src.search.search_rfc import SearchRFCQuery, search_rfcs


class IndexSearchWindow(BaseWindow):
    title_var: tk.StringVar
    index_1_page_entry: tk.Entry
    index_1_row_entry: tk.Entry
    index_1_position_entry: tk.Entry
    index_2_section_entry: tk.Entry
    index_2_row_entry: tk.Entry
    index_2_position_entry: tk.Entry
    search_results: SearchResults

    def __init__(self, parent, session):
        super().__init__(parent, "Find word by index", session)
        self.create_widgets()

    def create_widgets(self):
        # Create frames
        input_frame = ttk.Frame(self.main_frame, padding="10")
        input_frame.pack(fill="x")

        button_frame = ttk.Frame(self.main_frame, padding="10")
        button_frame.pack(fill="x")

        results_frame = ttk.Frame(self.main_frame, padding="10")
        results_frame.pack(fill="both", expand=True)

        # Create RFC dropdown
        self.title_var = self.create_rfc_dropdown(input_frame)
        self.index_1_page_entry = self.create_entry(input_frame, "Index 1 page:")
        self.index_1_row_entry = self.create_entry(input_frame, "Index 1 row:")
        self.index_1_position_entry = self.create_entry(input_frame, "Index 1 position:")
        self.index_2_section_entry = self.create_entry(input_frame, "Index 2 section:")
        self.index_2_row_entry = self.create_entry(input_frame, "Index 2 row:")
        self.index_2_position_entry = self.create_entry(input_frame, "Index 2 position:")

        # Create buttons
        self.create_button(button_frame, "Search by index 1", self.search_by_index_1)
        self.create_button(button_frame, "Search by index 2", self.search_by_index_2)
        self.create_button(button_frame, "Back", self.destroy)

        # Create results table
        columns = {
            "word": ("Word", 200),
            "context": ("Context", 400),
            "rfc": ("RFC", 100),
            "line_id": ("Line ID", 100)
        }
        self.search_results = SearchResults(self.main_frame, columns, self.open_rfc_window)

    def create_rfc_dropdown(self, parent):
        frame = ttk.Frame(parent)
        frame.pack(fill="x", pady=5)

        ttk.Label(frame, text="RFC:", width=15).pack(side="left")
        rfcs = search_rfcs(self.session, SearchRFCQuery())
        title_var = tk.StringVar()
        rfc_dropdown = ttk.Combobox(
            frame,
            textvariable=title_var,
            values=[rfc.title for rfc in rfcs],
        )
        rfc_dropdown.pack(side="left", expand=True, fill="x")
        return title_var

    def display_results(self, results: list[SearchResult]):
        formatted_results = [{
            "word": result.word,
            "context": result.context,
            "rfc": result.rfc,
            "line_id": result.line_id
        } for result in results]
        self.search_results.display_results(formatted_results)

    def open_rfc_window(self, values):
        rfc = int(values[2])
        line_id = int(values[3])
        RFCWindow(self, self.session, rfc, token=None, line_id=line_id)

    def search_by_index_1(self):
        criteria = Index1Criteria(
            title=self.title_var.get(),
            page=int(self.index_1_page_entry.get()) if self.index_1_page_entry.get() else None,
            line_in_page=int(self.index_1_row_entry.get()) if self.index_1_row_entry.get() else None,
            position_in_line=int(self.index_1_position_entry.get()) if self.index_1_position_entry.get() else None,
        )
        results = index_1_search(self.session, criteria)
        self.display_results(results)

    def search_by_index_2(self):
        criteria = Index2Criteria(
            title=self.title_var.get(),
            section=int(self.index_2_section_entry.get()) if self.index_2_section_entry.get() else None,
            line_in_section=int(self.index_2_row_entry.get()) if self.index_2_row_entry.get() else None,
            position_in_line=int(self.index_2_position_entry.get()) if self.index_2_position_entry.get() else None,
        )
        results = index_2_search(self.session, criteria)
        self.display_results(results)

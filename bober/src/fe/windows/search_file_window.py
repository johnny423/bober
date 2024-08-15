import datetime
import tkinter as tk
from tkinter import ttk

from tkcalendar import Calendar

from bober.src.fe.base_window import BaseWindow
from bober.src.fe.utils import create_label
from bober.src.fe.windows.rfc_window import RFCWindow
from bober.src.search.search_rfc import SearchRFCQuery, search_rfcs


class SearchFileWindow(BaseWindow):
    rfc_number_entry: tk.Entry
    title_entry: tk.Entry
    author_entry: tk.Entry
    contains_tokens: tk.Entry
    tree: ttk.Treeview
    scrollbar: ttk.Scrollbar

    def __init__(self, parent, session):
        super().__init__(parent, "Search File", session)
        self.create_widgets()

    def create_widgets(self):
        create_label(
            self, text="Authors:", placement='pack', placement_args={'pady': 5}
        )

        self.rfc_number_entry = self.create_entry(
            self.main_frame, "RFC Number:"
        )
        self.title_entry = self.create_entry(self.main_frame, "Title:")

        # Create a frame to hold both calendars
        calendar_frame = tk.Frame(self.main_frame)
        calendar_frame.pack(pady=5)

        # Create and pack the "Published After" calendar
        tk.Label(calendar_frame, text="Published After:").pack(
            side=tk.LEFT, padx=(0, 10)
        )
        self.published_after_cal = Calendar(
            calendar_frame, selectmode='day', year=1969, month=1, day=1
        )
        self.published_after_cal.pack(side=tk.LEFT, padx=(0, 20))

        today = datetime.date.today()
        # Create and pack the "Published Before" calendar
        tk.Label(calendar_frame, text="Published Before:").pack(
            side=tk.LEFT, padx=(0, 10)
        )
        self.published_before_cal = Calendar(
            calendar_frame,
            selectmode='day',
            year=today.year,
            month=today.month,
            day=today.day,
        )
        self.published_before_cal.pack(side=tk.LEFT)

        self.contains_tokens = self.create_entry(
            self.main_frame, "Contains tokens(space separated):"
        )

        # authors
        self.author_entry = self.create_entry(self.main_frame, "Authors:")

        # Create the Treeview widget for displaying search results
        self.tree = self._make_table(
            columns={
                "num": ("RFC Number", 100),
                "title": ("Title", 300),
                "published_at": ("Published At", 150),
                "authors": ("Authors", 250),
                "rank": ("Rank", 100),
            }
        )

        # Add scrollbar to the Treeview
        self.scrollbar = ttk.Scrollbar(
            self.main_frame, orient="vertical", command=self.tree.yview
        )
        self.tree.configure(yscrollcommand=self.scrollbar.set)

        # Pack the Treeview and scrollbar
        self.tree.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.rfc_number_entry.bind("<KeyRelease>", self.search_files)
        self.title_entry.bind("<KeyRelease>", self.search_files)
        self.published_after_cal.bind("<<CalendarSelected>>", self.search_files)
        self.published_before_cal.bind(
            "<<CalendarSelected>>", self.search_files
        )
        self.contains_tokens.bind("<KeyRelease>", self.search_files)
        self.author_entry.bind("<KeyRelease>", self.search_files)

        self.search_files()

    def _make_table(self, columns: dict[str, tuple[str, int]]) -> ttk.Treeview:
        tree = ttk.Treeview(
            self.main_frame, columns=list(columns.keys()), show="headings"
        )
        for col, (text, width) in columns.items():
            tree.heading(col, text=text)
            tree.column(col, width=width)

        return tree

    def search_files(self, event=None):
        rfc_num = self.rfc_number_entry.get()
        title = self.title_entry.get()
        published_after = self.published_after_cal.selection_get()
        published_before = self.published_before_cal.selection_get()
        tokens = self.contains_tokens.get().split()
        authors = [s.strip() for s in self.author_entry.get().split(',')]

        search_query = SearchRFCQuery(
            num=rfc_num or None,
            title=title or None,
            date_range=(published_after, published_before),
            authors=authors or None,
            tokens=tokens or None,
        )
        filtered_rfcs = search_rfcs(self.session, search_query)
        self.display_search_results(filtered_rfcs)

    def display_search_results(self, filtered_rfcs):
        # Clear previous results
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Insert new results
        for rfc in filtered_rfcs:
            item = self.tree.insert(
                "",
                "end",
                values=(
                    rfc.num,
                    rfc.title,
                    rfc.published_at.strftime("%Y-%m-%d"),
                    ", ".join(rfc.authors),
                    rfc.rank,
                ),
            )
            self.tree.item(item, tags=(item,))

        self.tree.bind("<Double-1>", self._on_item_click)

    def _on_item_click(self, event):
        item = self.tree.identify('item', event.x, event.y)
        (rfc, *_) = self.tree.item(item, 'values')
        RFCWindow(self, self.session, int(rfc))

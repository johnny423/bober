import tkinter as tk
from datetime import datetime
from tkinter import ttk

from bober.src.fe.base_window import BaseWindow
from bober.src.fe.windows.rfc_window import RFCWindow
from bober.src.fe.utils import convert_to_datetime, create_label
from bober.src.search.search_rfc import SearchRFCQuery, search_rfcs


class SearchFileWindow(BaseWindow):
    rfc_number_entry: tk.Entry
    title_entry: tk.Entry
    published_after_entry: tk.Entry
    published_before_entry: tk.Entry
    author_entry: tk.Entry
    contains_tokens: tk.Entry
    authors_listbox: tk.Listbox
    tree: ttk.Treeview
    scrollbar: ttk.Scrollbar

    def __init__(self, parent, session):
        super().__init__(parent, "Search File", session)
        self.create_widgets()

    def create_widgets(self):
        create_label(self, text="Authors:", placement='pack', placement_args={'pady': 5})

        # todo: bad display
        self.rfc_number_entry = self.create_entry(self.main_frame, "RFC Number (TODO - not working right now):")
        self.title_entry = self.create_entry(self.main_frame, "Title:")
        self.published_after_entry = self.create_entry(self.main_frame, "Published after (YYYY/MM/DD):")
        self.published_before_entry = self.create_entry(self.main_frame, "Published before (YYYY/MM/DD):")
        self.author_entry = self.create_entry(self.main_frame, "Authors:")
        self.contains_tokens = self.create_entry(self.main_frame, "Contains tokens(space separated):")

        self.create_button(self.main_frame, "Add Author", self.add_author)

        self.authors_listbox = self.create_listbox(self.main_frame, height=5, width=40)

        self.create_button(self.main_frame, "Remove Selected Author", self.remove_author)
        self.create_button(self.main_frame, "Search files", self.search_files)

        # Create the Treeview widget for displaying search results
        columns = {
            "num": ("RFC Number", 100),
            "title": ("Title", 300),
            "published_at": ("Published At", 150),
            "authors": ("Authors", 250)
        }
        self.tree = self._make_table(columns)

        # Add scrollbar to the Treeview
        self.scrollbar = ttk.Scrollbar(self.main_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.scrollbar.set)

        # Pack the Treeview and scrollbar
        self.tree.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.create_button(self.main_frame, "Cancel", self.destroy)

    def _make_table(self, columns: dict[str, tuple[str, int]]) -> ttk.Treeview:
        tree = ttk.Treeview(self.main_frame, columns=list(columns.keys()), show="headings")
        for col, (text, width) in columns.items():
            tree.heading(col, text=text)
            tree.column(col, width=width)

        return tree

    def add_author(self):
        author = self.author_entry.get().strip()
        if author:
            self.authors_listbox.insert("end", author)
            self.author_entry.delete(0, "end")
        else:
            self.show_warning("Please enter an author name.")

    def remove_author(self):
        selected = self.authors_listbox.curselection()
        if selected:
            self.authors_listbox.delete(selected)
        else:
            self.show_warning("Please select an author to remove.")

    def search_files(self):
        rfc_num = self.rfc_number_entry.get()
        title = self.title_entry.get()
        published_after = self.published_after_entry.get()
        published_before = self.published_before_entry.get()
        tokens = self.contains_tokens.get().split()
        authors = list(self.authors_listbox.get(0, "end"))

        # todo: calender selection
        if published_after:
            if not (date_range_min := convert_to_datetime(published_after)):
                self.show_error('Published after (should be YYYY/MM/DD)')
                return
        else:
            date_range_min = datetime.min
        if published_before:
            if not (date_range_max := convert_to_datetime(published_before)):
                self.show_error('Published before (should be YYYY/MM/DD)')
                return
        else:
            date_range_max = datetime.max

        search_query = SearchRFCQuery(
            num=rfc_num or None,
            title=title or None,
            date_range=(date_range_min, date_range_max),
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
            item = self.tree.insert("", "end", values=(
                rfc.num,
                rfc.title,
                rfc.published_at.strftime("%Y-%m-%d"),
                ", ".join(rfc.authors),
            ))
            self.tree.item(item, tags=(item,))

        self.tree.bind("<Double-1>", self._on_item_click)

    def _on_item_click(self, event):
        item = self.tree.identify('item', event.x, event.y)
        (rfc, *_) = self.tree.item(item, 'values')
        RFCWindow(self, self.session, int(rfc))

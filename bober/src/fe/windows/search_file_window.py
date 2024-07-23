import tkinter as tk
from tkinter import filedialog, messagebox
from datetime import datetime

from bober.src.fe.windows.utils import create_button, create_label


class SearchFileWindow(tk.Toplevel):
    def __init__(self, parent, search_files_callback):
        super().__init__(parent)
        self.title("Search File")
        # self.geometry("400x500")

        # Make this window modal
        self.grab_set()
        self.transient(parent)

        self.parent = parent
        self.search_files_callback = search_files_callback

        create_label(self, text="Filters to apply (fill relevant):", placement='pack', placement_args={'pady': 5})

        # Metadata input fields
        create_label(self, text="RFC Number (TODO - not working right now):", placement='pack', placement_args={'pady': 5})  # todo support this filter
        self.rfc_number_entry = tk.Entry(self)
        self.rfc_number_entry.pack(pady=5)

        create_label(self, text="Title:", placement='pack', placement_args={'pady': 5})
        self.title_entry = tk.Entry(self)
        self.title_entry.pack(pady=5)

        create_label(self, text="Published after (YYYY/MM/DD):", placement='pack', placement_args={'pady': 5})
        self.published_after_entry = tk.Entry(self)
        self.published_after_entry.pack(pady=5)

        create_label(self, text="Published before (YYYY/MM/DD):", placement='pack', placement_args={'pady': 5})
        self.published_before_entry = tk.Entry(self)
        self.published_before_entry.pack(pady=5)

        create_label(self, text="Authors:", placement='pack', placement_args={'pady': 5})
        self.author_entry = tk.Entry(self)
        self.author_entry.pack(pady=5)

        create_label(self, text="Contains tokens(space separated):", placement='pack', placement_args={'pady': 5})
        self.contains_tokens = tk.Entry(self)
        self.contains_tokens.pack(pady=5)

        create_button(
            self,
            text="Add Author",
            command=self.add_author,
            placement='pack',
            placement_args={'pady': 5}
        )

        self.authors_listbox = tk.Listbox(self, height=5, width=40)
        self.authors_listbox.pack(pady=5)

        create_button(
            self,
            text="Remove Selected Author",
            command=self.remove_author,
            placement='pack',
            placement_args={'pady': 5}
        )

        create_button(
            self,
            text="Search files",
            command=self.search_files,
            placement='pack',
            placement_args={'pady': 10}
        )

        create_button(
            self,
            text="Cancel",
            command=self.destroy,
            bg="lightgray",
            placement='pack',
            placement_args={'pady': 5}
        )

    # todo remove boiler palate code copied from load file window
    def add_author(self):
        author = self.author_entry.get().strip()
        if author:
            self.authors_listbox.insert(tk.END, author)
            self.author_entry.delete(0, tk.END)
        else:
            messagebox.showwarning("Warning", "Please enter an author name.", parent=self)

    def remove_author(self):
        selected = self.authors_listbox.curselection()
        if selected:
            self.authors_listbox.delete(selected)
        else:
            messagebox.showwarning("Warning", "Please select an author to remove.", parent=self)

    @staticmethod
    def validate_date(date_string):
        try:
            datetime.strptime(date_string, "%Y/%m/%d")
            return True
        except ValueError:
            return False

    def search_files(self):
        rfc_num = self.rfc_number_entry.get()
        title = self.title_entry.get()
        published_after = self.published_after_entry.get()
        published_before = self.published_before_entry.get()
        tokens = self.contains_tokens.get().split()
        authors = list(self.authors_listbox.get(0, tk.END))
        
        # if not any([  # todo add back if needed
        #     rfc_num,
        #     title,
        #     published_at,
        #     self.authors_listbox.size() == 0,
        # ]):
        #     messagebox.showerror("Error", 'Fill at least one filter', parent=self)
        #     return

        authors: list[str] | None = None
        date_range: tuple[datetime, datetime] | None = None
        title: str | None = None
        tokens: list[str] | None = None
        filters = {
            "title": title,
            "date_range": published_at,
            "authors": list(self.authors_listbox.get(0, tk.END))
            "authors": list(self.authors_listbox.get(0, tk.END))
        }
        self.search_files_callback(filters)
        self.destroy()

    def destroy(self):
        self.grab_release()
        super().destroy()

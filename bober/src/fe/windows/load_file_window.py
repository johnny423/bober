import tkinter as tk
from tkinter import filedialog

from bober.src.fe.base_window import BaseWindow
from bober.src.fe.utils import convert_to_datetime
from bober.src.rfc_ingest.load_from_file import load_single_file


class LoadFileWindow(BaseWindow):
    file_label: tk.Label
    rfc_number_entry: tk.Entry
    title_entry: tk.Entry
    published_at_entry: tk.Entry
    author_entry: tk.Entry
    authors_listbox: tk.Listbox

    def __init__(self, parent, session):
        super().__init__(parent, "Load File", session)
        self.filepath = ""
        self.create_widgets()

    def create_widgets(self):
        self.create_button(self.main_frame, "Browse", self.browse_file)

        self.file_label = tk.Label(self.main_frame, text="No file selected")
        self.file_label.pack(pady=5)

        self.rfc_number_entry = self.create_entry(self.main_frame, "RFC Number:")
        self.title_entry = self.create_entry(self.main_frame, "Title:")
        self.published_at_entry = self.create_entry(self.main_frame, "Published at (YYYY/MM/DD):")
        self.author_entry = self.create_entry(self.main_frame, "Authors:")

        self.create_button(self.main_frame, "Add Author", self.add_author)

        self.authors_listbox = self.create_listbox(self.main_frame)

        self.create_button(self.main_frame, "Remove Selected Author", self.remove_author)
        self.create_button(self.main_frame, "Load File", self.load_file)
        self.create_button(self.main_frame, "Cancel", self.destroy)

    def browse_file(self):
        self.filepath = filedialog.askopenfilename(
            title="Select a file",
            filetypes=(("All files", "*.*"),),
            parent=self,
        )
        if self.filepath:
            self.file_label.config(text=f"Selected file: {self.filepath}")

    def add_author(self):
        author = self.author_entry.get().strip()
        if author:
            self.authors_listbox.insert(tk.END, author)
            self.author_entry.delete(0, tk.END)
        else:
            self.show_warning("Please enter an author name.")

    def remove_author(self):
        selected = self.authors_listbox.curselection()
        if selected:
            self.authors_listbox.delete(selected)
        else:
            self.show_warning("Please select an author to remove.")

    def load_file(self):
        missing_fields = []
        invalid_fields = []

        if not self.filepath:
            missing_fields.append("File")

        rfc_num = self.rfc_number_entry.get()
        if not rfc_num:
            missing_fields.append("RFC Number")
        elif not rfc_num.isdigit():
            invalid_fields.append("RFC Number must be an integer")

        title = self.title_entry.get()
        if not title:
            missing_fields.append("Title")

        published_at = self.published_at_entry.get()
        if not published_at:
            missing_fields.append("Published at")
        elif not convert_to_datetime(published_at):
            invalid_fields.append("Published at (should be YYYY/MM/DD)")

        if self.authors_listbox.size() == 0:
            missing_fields.append("Authors")

        if missing_fields or invalid_fields:
            error_message = ""
            if missing_fields:
                error_message += f"Please fill in the following fields: {', '.join(missing_fields)}\n"
            if invalid_fields:
                error_message += f"Invalid format for: {', '.join(invalid_fields)}"
            self.show_error(error_message.strip())
            return

        metadata = {
            "num": rfc_num,
            "title": title,
            "publish_at": published_at,
            "authors": list(self.authors_listbox.get(0, tk.END)),
        }
        load_single_file(self.session, self.filepath, metadata)
        self.destroy()

import datetime
import tkinter as tk
from tkinter import filedialog, ttk

from tkcalendar import Calendar

from bober.src.fe.tabs.base_tab import BaseTab
from bober.src.rfc_ingest.load_from_file import load_single_file


class LoadFileTab(BaseTab):
    def __init__(self, parent, session):
        super().__init__(parent, session)
        self.filepath = ""

    def create_widgets(self):
        # Create frames
        input_frame = ttk.Frame(self, padding="10")
        input_frame.pack(fill="x")

        button_frame = ttk.Frame(self, padding="10")
        button_frame.pack(fill="x")

        # File selection
        self.create_button(input_frame, "Browse", self.browse_file)
        self.file_label = ttk.Label(input_frame, text="No file selected")
        self.file_label.pack(pady=5)

        # Input fields
        self.rfc_number_entry = self.create_entry(input_frame, "RFC Number:")
        self.title_entry = self.create_entry(input_frame, "Title:")
        self.author_entry = self.create_entry(input_frame, "Authors:")

        # Calendar
        today = datetime.date.today()
        label_frame = ttk.Frame(input_frame)
        label_frame.pack(fill=tk.X, pady=(5, 0))
        ttk.Label(label_frame, text="Published at:", anchor=tk.W).pack(
            side=tk.LEFT, padx=(0, 10), fill=tk.X
        )
        calendar_frame = ttk.Frame(input_frame)
        calendar_frame.pack(pady=(0, 5))
        self.published_at_cal = Calendar(
            calendar_frame,
            selectmode='day',
            year=today.year,
            month=today.month,
            day=today.day,
        )
        self.published_at_cal.pack(expand=True)

        # Load button
        self.create_button(button_frame, "Load File", self.load_file)

    def browse_file(self):
        self.filepath = filedialog.askopenfilename(
            title="Select a file",
            filetypes=(("All files", "*.*"),),
            parent=self.winfo_toplevel(),
        )
        if self.filepath:
            self.file_label.config(text=f"Selected file: {self.filepath}")

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

        published_at = self.published_at_cal.selection_get()

        authors = [s.strip() for s in self.author_entry.get().split(',')]
        if len(authors) == 0:
            missing_fields.append("Authors")

        if missing_fields or invalid_fields:
            error_message = ""
            if missing_fields:
                error_message += f"Please fill in the following fields: {', '.join(missing_fields)}\n"
            if invalid_fields:
                error_message += (
                    f"Invalid format for: {', '.join(invalid_fields)}"
                )
            self.show_error(error_message.strip())
            return

        metadata = {
            "num": rfc_num,
            "title": title,
            "publish_at": published_at,
            "authors": authors,
        }
        load_single_file(self.session, self.filepath, metadata)
        self.clear_fields()

    def clear_fields(self):
        self.filepath = ""
        self.file_label.config(text="No file selected")
        self.rfc_number_entry.delete(0, tk.END)
        self.title_entry.delete(0, tk.END)
        self.author_entry.delete(0, tk.END)
        today = datetime.date.today()
        self.published_at_cal.selection_set(today)

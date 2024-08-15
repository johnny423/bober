import datetime
import tkinter as tk
from tkinter import filedialog

from tkcalendar import Calendar

from bober.src.fe.base_window import BaseWindow
from bober.src.rfc_ingest.load_from_file import load_single_file


class LoadFileWindow(BaseWindow):
    file_label: tk.Label
    rfc_number_entry: tk.Entry
    title_entry: tk.Entry
    published_at_cal: Calendar
    author_entry: tk.Entry

    def __init__(self, parent, session):
        super().__init__(parent, "Load File", session)
        self.filepath = ""
        self.create_widgets()

    def create_widgets(self):
        self.create_button(self.main_frame, "Browse", self.browse_file)
        self.file_label = tk.Label(self.main_frame, text="No file selected")
        self.file_label.pack(pady=5)
        self.rfc_number_entry = self.create_entry(
            self.main_frame, "RFC Number:"
        )
        self.title_entry = self.create_entry(self.main_frame, "Title:")
        self.author_entry = self.create_entry(self.main_frame, "Authors:")
        today = datetime.date.today()

        # Create a frame for the calendar label
        label_frame = tk.Frame(self.main_frame)
        label_frame.pack(fill=tk.X, pady=(5, 0))

        tk.Label(label_frame, text="Published at:", anchor=tk.W).pack(
            side=tk.LEFT, padx=(0, 10), fill=tk.X
        )

        # Create a separate frame for the calendar to keep it centered
        calendar_frame = tk.Frame(self.main_frame)
        calendar_frame.pack(pady=(0, 5))

        self.published_at_cal = Calendar(
            calendar_frame,
            selectmode='day',
            year=today.year,
            month=today.month,
            day=today.day,
        )
        self.published_at_cal.pack(expand=True)

        self.create_button(self.main_frame, "Load File", self.load_file)

    def browse_file(self):
        self.filepath = filedialog.askopenfilename(
            title="Select a file",
            filetypes=(("All files", "*.*"),),
            parent=self,
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
        self.destroy()

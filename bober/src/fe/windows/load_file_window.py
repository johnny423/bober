import tkinter as tk
from tkinter import filedialog, messagebox
from datetime import datetime

from bober.src.fe.windows.utils import create_button, create_label


def loaded_file_callback_mock(*args):
    print('printing args')
    for arg in args:
        print(arg)
    print('done printing args')


class LoadFileWindow(tk.Toplevel):
    def __init__(self, parent, file_loaded_callback=loaded_file_callback_mock):
        super().__init__(parent)
        self.title("Load File")
        # self.geometry("400x500")

        # Make this window modal
        self.grab_set()
        self.transient(parent)

        self.parent = parent
        self.file_loaded_callback = file_loaded_callback

        self.filepath = ""

        create_label(self, text="Select a file to load:", placement='pack', placement_args={'pady': 10})

        create_button(
            self,
            text="Browse",
            command=self.browse_file,
            placement='pack',
            placement_args={'pady': 5}
        )

        self.file_label = create_label(self, text="No file selected", placement='pack', placement_args={'pady': 5})

        # Metadata input fields
        create_label(self, text="RFC Number:", placement='pack', placement_args={'pady': 5})
        self.rfc_number_entry = tk.Entry(self)
        self.rfc_number_entry.pack(pady=5)

        create_label(self, text="Title:", placement='pack', placement_args={'pady': 5})
        self.title_entry = tk.Entry(self)
        self.title_entry.pack(pady=5)

        create_label(self, text="Published at (DD/MM/YYYY):", placement='pack', placement_args={'pady': 5})
        self.published_at_entry = tk.Entry(self)
        self.published_at_entry.pack(pady=5)

        create_label(self, text="Authors:", placement='pack', placement_args={'pady': 5})
        self.author_entry = tk.Entry(self)
        self.author_entry.pack(pady=5)

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
            text="Load File",
            command=self.load_file,
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

    def browse_file(self):
        self.filepath = filedialog.askopenfilename(
            title="Select a file",
            filetypes=(("All files", "*.*"),),
            parent=self  # Specify the parent window
        )
        if self.filepath:
            self.file_label.config(text=f"Selected file: {self.filepath}")

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

    def validate_date(self, date_string):
        try:
            datetime.strptime(date_string, "%d/%m/%Y")
            return True
        except ValueError:
            return False

    def load_file(self):
        missing_fields = []
        invalid_fields = []

        if not self.filepath:
            missing_fields.append("File")
        if not self.rfc_number_entry.get():
            missing_fields.append("RFC Number")
        if not self.title_entry.get():
            missing_fields.append("Title")

        published_at = self.published_at_entry.get()
        if not published_at:
            missing_fields.append("Published at")
        elif not self.validate_date(published_at):
            invalid_fields.append("Published at (should be DD/MM/YYYY)")

        if self.authors_listbox.size() == 0:
            missing_fields.append("Authors")

        if missing_fields or invalid_fields:
            error_message = ""
            if missing_fields:
                error_message += f"Please fill in the following fields: {', '.join(missing_fields)}\n"
            if invalid_fields:
                error_message += f"Invalid format for: {', '.join(invalid_fields)}"
            messagebox.showerror("Error", error_message.strip(), parent=self)
            return

        metadata = {
            "rfc_number": self.rfc_number_entry.get(),
            "title": self.title_entry.get(),
            "published_at": published_at,
            "authors": list(self.authors_listbox.get(0, tk.END))
        }

        self.file_loaded_callback(self.filepath, metadata)
        self.destroy()

    def destroy(self):
        self.grab_release()
        super().destroy()

import tkinter as tk
from tkinter import messagebox, ttk


class BaseWindow(tk.Toplevel):
    def __init__(self, parent, title, session=None):
        super().__init__(parent)
        self.parent = parent
        self.session = session
        self.title(title)

        # Make this window modal
        self.transient(parent)

        # Set a default size
        self.geometry("1000x750")

        # Create a main frame to hold all widgets
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

    def create_entry(self, parent, label_text) -> ttk.Entry:
        """Create a labeled entry widget."""
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, pady=5)

        ttk.Label(frame, text=label_text, width=15).pack(side=tk.LEFT)
        entry = ttk.Entry(frame)
        entry.pack(side=tk.LEFT, expand=True, fill=tk.X)
        return entry

    def create_combobox(self, parent, label_text, values) -> ttk.Combobox:
        """Create a labeled combobox widget."""
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, pady=5)

        ttk.Label(frame, text=label_text, width=15).pack(side=tk.LEFT)
        combobox = ttk.Combobox(frame, values=values)
        combobox.pack(side=tk.LEFT, expand=True, fill=tk.X)
        return combobox

    def create_button(self, parent, text, command) -> ttk.Button:
        """Create a button widget."""
        button = ttk.Button(parent, text=text, command=command)
        button.pack(pady=10)
        return button

    def create_listbox(self, parent) -> tk.Listbox:
        """Create a listbox widget that fills the entire parent."""
        listbox = tk.Listbox(parent)
        listbox.pack(fill=tk.BOTH, expand=True)
        return listbox

    def create_treeview(self, parent, columns, headings) -> ttk.Treeview:
        """Create a treeview widget with scrollbar."""
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True)

        tree = ttk.Treeview(frame, columns=columns, show="headings")
        for col, heading in zip(columns, headings):
            tree.heading(col, text=heading)
            tree.column(col, width=100)  # Default width, can be adjusted

        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        return tree

    def show_info(self, message: str) -> None:
        messagebox.showinfo("Info", message, parent=self)

    def show_error(self, message: str) -> None:
        messagebox.showerror("Error", message, parent=self)

    def show_warning(self, message: str) -> None:
        messagebox.showwarning("Warning", message, parent=self)

    def destroy(self) -> None:
        """Override destroy to release grab."""
        self.grab_release()
        super().destroy()

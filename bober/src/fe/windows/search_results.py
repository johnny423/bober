import json
import tkinter as tk
from tkinter import filedialog, ttk


class SearchResults:
    def __init__(self, parent_frame, columns, on_item_click):
        self.parent_frame = parent_frame
        self.on_item_click = on_item_click

        # Create main frame
        self.main_frame = ttk.Frame(self.parent_frame)
        self.main_frame.pack(fill="both", expand=True)

        # Create Treeview
        self.tree = ttk.Treeview(self.main_frame, columns=list(columns.keys()), show="headings")
        for col, (text, width) in columns.items():
            self.tree.heading(col, text=text)
            self.tree.column(col, width=width)

        # Add scrollbar
        self.scrollbar = ttk.Scrollbar(self.main_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.scrollbar.set)

        # Create export button
        self.export_button = ttk.Button(self.main_frame, text="Export Results", command=self.export_results)

        # Pack widgets
        self.tree.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        self.export_button.pack(side="bottom", pady=5)

        # Bind double-click event
        self.tree.bind("<Double-1>", self._handle_item_click)

        self.results = []

    def display_results(self, results):
        self.results = results
        self.tree.delete(*self.tree.get_children())
        for result in results:
            values = tuple(str(result[col]) for col in self.tree['columns'])
            item = self.tree.insert("", "end", values=values)
            self.tree.item(item, tags=(item,))

    def _handle_item_click(self, event):
        item = self.tree.identify('item', event.x, event.y)
        if item:
            values = self.tree.item(item, 'values')
            self.on_item_click(values)

    def export_results(self):
        if not self.results:
            tk.messagebox.showinfo("Export", "No results to export.")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    json.dump(self.results, f, indent=2)
                tk.messagebox.showinfo("Export Successful", f"Results exported to {file_path}")
            except Exception as e:
                tk.messagebox.showerror("Export Failed", f"An error occurred: {str(e)}")

    def export_to_json(self):
        return json.dumps(self.results, indent=2)

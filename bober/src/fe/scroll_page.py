import tkinter as tk
from tkinter import Menu, TclError, scrolledtext, ttk
from typing import List, Optional

from bober.src.search.rfc_content import AbsPosition


class LineNumberedText:
    def __init__(self, parent: tk.Widget, initial_text: str, highlights: Optional[List] = None):
        self.frame = ttk.Frame(parent, padding=10)
        self.frame.pack(fill=tk.BOTH, expand=True)

        self.text_frame = ttk.Frame(self.frame)
        self.text_frame.pack(fill=tk.BOTH, expand=True)

        self.line_numbers = tk.Text(self.text_frame, width=4, padx=4, pady=4, bg='lightgray', state='disabled')
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)

        self.text_area = scrolledtext.ScrolledText(
            self.text_frame, wrap=tk.NONE, width=60, height=15, padx=4, pady=4
        )
        self.text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.text_area.insert(tk.END, initial_text)
        self.m = Menu(self.text_area, tearoff=0)
        self.m.add_command(label="save as phrase", command=self.save_phrase_popup)
        self.text_area.bind("<Button-3>", self.command_popup)

        self.h_scrollbar = ttk.Scrollbar(
            self.frame, orient=tk.HORIZONTAL, command=self.text_area.xview
        )
        self.h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.text_area.config(xscrollcommand=self.h_scrollbar.set)

        if highlights:
            self.text_area.tag_config('highlight', background='yellow')
            for highlight in highlights:
                start_idx = f"{highlight.line}.{highlight.start}"
                end_idx = f"{start_idx}+{highlight.length}c"
                self.text_area.tag_add('highlight', start_idx, end_idx)

    def save_phrase_popup(self):
        try:
            selected_text = self.text_area.get(tk.SEL_FIRST, tk.SEL_LAST)
        except TclError:
            tk.messagebox.showerror("Error", "No text selected!")
            return

        def _on_submit():
            phrase_name = name_entry.get()
            if phrase_name:
                print(f"saving!!! {phrase_name} {selected_text}")
                popup.destroy()
            else:
                tk.messagebox.showerror("Error", "Phrase name cannot be empty!")

        popup = tk.Toplevel(self.frame)
        popup.title("Save Phrase")

        tk.Label(popup, text="Enter phrase name:").pack(pady=5)
        name_entry = tk.Entry(popup)
        name_entry.pack(pady=5)

        submit_button = tk.Button(popup, text="Save", command=_on_submit)
        submit_button.pack(pady=10)

    def command_popup(self, event):
        try:
            self.m.tk_popup(event.x_root, event.y_root)
        finally:
            self.m.grab_release()

    def scroll_to_line(self, line_number: int):
        self.text_area.see(f"{line_number}.0")

def create_scroll_region(
        parent: tk.Widget, initial_text: str, highlights: None | list[AbsPosition] = None
) -> LineNumberedText:
    return LineNumberedText(parent, initial_text, highlights)

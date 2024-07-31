import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
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

        self.update_line_numbers()

    def scroll_to_line(self, line_number: int):
        self.text_area.see(f"{line_number}.0")

    # todo: not working
    def update_line_numbers(self, *args):
        self.line_numbers.config(state='normal')
        self.line_numbers.delete('1.0', tk.END)
        num_lines = self.text_area.get('1.0', tk.END).count('\n')
        line_numbers_text = '\n'.join(str(i) for i in range(1, num_lines + 1))
        self.line_numbers.insert('1.0', line_numbers_text)
        self.line_numbers.config(state='disabled')
        self.line_numbers.yview_moveto(self.text_area.yview()[0])


def create_scroll_region(
        parent: tk.Widget, initial_text: str, highlights: None | list[AbsPosition] = None
) -> LineNumberedText:
    return LineNumberedText(parent, initial_text, highlights)

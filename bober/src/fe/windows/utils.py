import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext


def add_button(parent, text, command, row, column):
    button = ttk.Button(parent, text=text, command=command)
    button.grid(row=row, column=column, padx=5, pady=5)
    return button


def add_input_field(parent, label_text, row, column):
    label = ttk.Label(parent, text=label_text)
    label.grid(row=row, column=column, padx=5, pady=5)
    entry = ttk.Entry(parent, width=30)
    entry.grid(row=row, column=column+1, padx=5, pady=5)
    return entry


def create_scroll_region(parent, initial_text, row, column, highlight_strings=None):
    if highlight_strings is None:
        highlight_strings = []
    frame = ttk.Frame(parent, padding="10 10 10 10")
    frame.grid(row=row, column=column, sticky=(tk.W, tk.E, tk.N, tk.S))

    text_area = scrolledtext.ScrolledText(frame, wrap=tk.NONE, width=60, height=15)
    text_area.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    text_area.insert(tk.END, initial_text)
    frame.columnconfigure(0, weight=1)
    frame.rowconfigure(0, weight=1)

    # Configure the tag for yellow background
    text_area.tag_config('highlight', background='yellow')

    def highlight_text():
        for string in highlight_strings:
            start_idx = '1.0'
            while True:
                start_idx = text_area.search(string, start_idx, tk.END)
                if not start_idx:
                    break
                end_idx = f"{start_idx}+{len(string)}c"
                text_area.tag_add('highlight', start_idx, end_idx)
                start_idx = end_idx

    # Call the highlight function to highlight all occurrences of the strings
    highlight_text()

    # Add a horizontal scrollbar
    h_scrollbar = ttk.Scrollbar(frame, orient=tk.HORIZONTAL, command=text_area.xview)
    h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
    text_area['xscrollcommand'] = h_scrollbar.set

    return text_area


def add_dict_display(parent, dictionary, row, column, col1text, col2text):
    frame = ttk.Frame(parent, padding="10 10 10 10")
    frame.grid(row=row, column=column, sticky=(tk.W, tk.E, tk.N, tk.S))
    tree = ttk.Treeview(frame, columns=("Value",), show="tree headings")
    tree.heading("#0", text=col1text)
    tree.heading("Value", text=col2text)
    tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    frame.columnconfigure(0, weight=1)
    frame.rowconfigure(0, weight=1)

    def display_dict(tree, dictionary, parent=''):
        for key, value in dictionary.items():
            if isinstance(value, dict):
                node = tree.insert(parent, 'end', text=str(key))
                display_dict(tree, value, node)
            elif hasattr(value, '__iter__') and not isinstance(value, (str, bytes)):
                node = tree.insert(parent, 'end', text=str(key))
                for item in value:
                    tree.insert(node, 'end', text="", values=(str(item),))
            else:
                tree.insert(parent, 'end', text=str(key), values=(str(value),))

    display_dict(tree, dictionary)
    return tree


def dummy_button_command():
    print('dummy command for button executed')

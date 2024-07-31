import tkinter as tk
from collections import namedtuple
from datetime import datetime
from tkinter import scrolledtext, ttk
from typing import Any, Callable

from bober.src.search.rfc_content import AbsPosition


def create_button(
        parent, text, command, placement='pack', placement_args=None, **kwargs
):
    """
    Create, configure, and place a button with default styling and the given parameters.

    :param parent: The parent widget
    :param text: Text to display on the button
    :param command: Function to call when the button is clicked
    :param placement: Method to use for placing the button ('pack' or 'grid')
    :param placement_args: Dictionary of arguments for the placement method
    :param kwargs: Additional keyword arguments for the Button constructor
    :return: tk.Button object
    """
    default_config = {
        'bg': 'lightblue',
        'fg': 'black',
        'padx': 10,
        'pady': 5,
        'font': ('Arial', 10),
        'relief': tk.RAISED,
    }

    default_config.update(kwargs)

    button = tk.Button(parent, text=text, command=command, **default_config)

    if placement == 'pack':
        pack_args = placement_args or {'pady': 10}
        button.pack(**pack_args)
    elif placement == 'grid':
        grid_args = placement_args or {}
        button.grid(**grid_args)
    else:
        raise ValueError("Placement must be either 'pack' or 'grid'")

    return button


def create_label(parent, text, placement='pack', placement_args=None, **kwargs):
    """
    Create, configure, and place a label with default styling and the given parameters.

    :param parent: The parent widget
    :param text: Text to display on the label
    :param placement: Method to use for placing the label ('pack' or 'grid')
    :param placement_args: Dictionary of arguments for the placement method
    :param kwargs: Additional keyword arguments for the Label constructor
    :return: tk.Label object
    """
    default_config = {
        'fg': 'black',
        'font': ('Arial', 10),
        'wraplength': 350,  # Default wrap length
    }

    default_config.update(kwargs)

    label = tk.Label(parent, text=text, **default_config)

    if placement == 'pack':
        pack_args = placement_args or {'pady': 5}
        label.pack(**pack_args)
    elif placement == 'grid':
        grid_args = placement_args or {}
        label.grid(**grid_args)
    else:
        raise ValueError("Placement must be either 'pack' or 'grid'")

    return label


def create_scroll_region(
        parent: tk.Widget, initial_text: str, highlights: list[AbsPosition] | None = None
) -> scrolledtext.ScrolledText:
    """
    Create and return a ScrolledText widget with highlighting capabilities.

    Args:
        parent (tk.Widget): The parent widget.
        initial_text (str): The initial text to display in the widget.
        to_highlight (Optional[List[str]]): Strings to highlight in the text.

    Returns:
        scrolledtext.ScrolledText: The created ScrolledText widget.
    """
    frame = ttk.Frame(parent, padding=10)
    frame.pack(fill=tk.BOTH, expand=True)

    text_area = scrolledtext.ScrolledText(
        frame, wrap=tk.NONE, width=60, height=15
    )
    text_area.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
    text_area.insert(tk.END, initial_text)

    # Add a horizontal scrollbar
    h_scrollbar = ttk.Scrollbar(
        frame, orient=tk.HORIZONTAL, command=text_area.xview
    )
    h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
    text_area.config(xscrollcommand=h_scrollbar.set)

    # Highlight specified strings

    if highlights:
        text_area.tag_config('highlight', background='yellow')
        for highlight in highlights:
            start_idx = f"{highlight.line}.{highlight.start}"
            end_idx = f"{start_idx}+{highlight.length}c"
            text_area.tag_add('highlight', start_idx, end_idx)

    return frame


#
# def highlight_strings(
#         text_area: scrolledtext.ScrolledText, to_highlight: list[str]
# ):
#     text_area.tag_config('highlight', background='yellow')
#
#     for string in to_highlight:
#         start_idx = '1.0'
#         while start_idx := text_area.search(string, start_idx, tk.END):
#             end_idx = f"{start_idx}+{len(string)}c"
#             text_area.tag_add('highlight', start_idx, end_idx)
#             start_idx = end_idx


Leaf = namedtuple("Leaf", ("value", "metadata"))
Tree = dict[str, Leaf] | dict[str, "Tree"]


def add_dict_display(
        parent: tk.Widget,
        dictionary: Tree,
        key_header: str,
        value_header: str,
        callback: None | Callable = None,
):
    frame = ttk.Frame(parent, padding=10)
    frame.pack(fill=tk.BOTH, expand=True)

    tree = ttk.Treeview(frame, columns=("Value",), show="tree headings")
    tree.heading("#0", text=key_header)
    tree.heading("Value", text=value_header)
    tree.pack(fill=tk.BOTH, expand=True)

    _populate_tree(tree, dictionary)

    if callback:
        tree.bind(
            "<Double-1>", lambda event: _on_item_click(event, tree, callback)
        )


def _populate_tree(
        tree: ttk.Treeview, data: Tree | Leaf, parent: str = ''
) -> None:
    if isinstance(data, dict):
        for key, value in data.items():
            node = tree.insert(parent, 'end', text=str(key))
            _populate_tree(tree, value, node)
    else:
        node = tree.insert(parent, 'end', text='', values=data)
        tree.item(node, tags=('leaf',))
        # tree.item(node, values=(data.metadata,))


def _on_item_click(event, tree: ttk.Treeview, callback: Callable[[Any], None]):
    item = tree.identify('item', event.x, event.y)
    if item and 'leaf' in tree.item(item, 'tags'):
        values = tree.item(item, 'values')
        if values:
            callback(*values[1:])


def ellipsis_around(
        text: str, start_position: int, end_position: int, length: int
) -> str:
    """
    Create a substring of 'text' centered around the range from 'start_position' to 'end_position'
    with given 'length', adding ellipses where text is truncated and highlighting the given range.

    Args:
    text (str): The original text.
    start_position (int): The start position of the range to highlight (0-indexed).
    end_position (int): The end position of the range to highlight (0-indexed).
    length (int): The desired length of the output string, including ellipses.

    Returns:
    str: The shortened text with ellipses and highlighted range.

    Examples:
    >>> ellipsis_around("This is a long piece of text that we want to shorten.", 10, 15, 30)
    '...is a long [piece] of text th...'

    >>> ellipsis_around("Short text", 6, 10, 20)
    'Short [text]'

    >>> ellipsis_around("Another example of a long string for ellipsis", 8, 15, 25)
    '...er [example of] a lon...'

    >>> ellipsis_around("Start of the text", 0, 5, 15)
    '[Start] of the...'

    >>> ellipsis_around("End of the text", 11, 15, 15)
    '...of [the text]'

    >>> ellipsis_around("Very short", 5, 10, 10)
    'Very [short]'

    >>> ellipsis_around("Exactly twenty chars.", 8, 14, 20)
    'Exactly [twenty] chars.'
    """
    if len(text) <= length:
        return (
                text[:start_position]
                + f"[{text[start_position:end_position]}]"
                + text[end_position:]
        )

    length = max(
        length, 7
    )  # Ensure minimum length for ellipses, content, and brackets
    highlight_length = end_position - start_position
    available_length = (
            length - 5 - highlight_length
    )  # Subtract 5 for ellipses and brackets

    left_context = (available_length) // 2

    start = max(0, min(start_position - left_context, len(text) - length + 5))
    end = min(len(text), start + length - 5)

    result = ""
    if start > 0:
        result += "..."

    result += text[start:start_position]
    result += f"[{text[start_position:end_position]}]"
    result += text[end_position:end]

    if end < len(text):
        result += "..."

    return result


def convert_to_datetime(date_string):
    try:
        return datetime.strptime(date_string, "%Y/%m/%d")
    except ValueError:
        return False

import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
from typing import Any


def add_button(parent, text, command, row, column):  # todo remove
    button = ttk.Button(parent, text=text, command=command)
    button.grid(row=row, column=column, padx=5, pady=5)
    return button


def create_button(parent, text, command, placement='pack', placement_args=None, **kwargs):
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


def callback_mock(*args):
    print('printing args')
    for arg in args:
        print(arg)
    print('done printing args')


def add_input_field(parent, label_text, row, column):  # todo remove
    label = ttk.Label(parent, text=label_text)
    label.grid(row=row, column=column, padx=5, pady=5)
    entry = ttk.Entry(parent, width=30)
    entry.grid(row=row, column=column + 1, padx=5, pady=5)
    return entry


def create_scroll_region(
        parent: tk.Widget,
        initial_text: str,
        to_highlight: list[str] | None = None
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

    text_area = scrolledtext.ScrolledText(frame, wrap=tk.NONE, width=60, height=15)
    text_area.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
    text_area.insert(tk.END, initial_text)

    # Add a horizontal scrollbar
    h_scrollbar = ttk.Scrollbar(frame, orient=tk.HORIZONTAL, command=text_area.xview)
    h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
    text_area.config(xscrollcommand=h_scrollbar.set)

    # Highlight specified strings
    if to_highlight:
        highlight_strings(text_area, to_highlight)

    return text_area


def highlight_strings(text_area: scrolledtext.ScrolledText, to_highlight: list[str]):
    text_area.tag_config('highlight', background='yellow')

    for string in to_highlight:
        start_idx = '1.0'
        while start_idx := text_area.search(string, start_idx, tk.END):
            end_idx = f"{start_idx}+{len(string)}c"
            text_area.tag_add('highlight', start_idx, end_idx)
            start_idx = end_idx


def add_dict_display(parent: tk.Widget, dictionary: dict[Any, Any], key_header: str, value_header: str) -> ttk.Treeview:
    """
    Create and return a Treeview widget displaying a dictionary.

    Args:
        parent (tk.Widget): The parent widget.
        dictionary (Dict[Any, Any]): The dictionary to display.
        key_header (str): The header text for the key column.
        value_header (str): The header text for the value column.

    Returns:
        ttk.Treeview: The created Treeview widget.
    """
    frame = ttk.Frame(parent, padding=10)
    frame.pack(fill=tk.BOTH, expand=True)

    tree = ttk.Treeview(frame, columns=("Value",), show="tree headings")
    tree.heading("#0", text=key_header)
    tree.heading("Value", text=value_header)
    tree.pack(fill=tk.BOTH, expand=True)

    _populate_tree(tree, dictionary)
    return tree


def _populate_tree(tree: ttk.Treeview, data: Any, parent: str = '') -> None:
    """
    Recursively populate the Treeview with dictionary data.

    Args:
        tree (ttk.Treeview): The Treeview to populate.
        data (Any): The data to add to the Treeview.
        parent (str): The parent node identifier.
    """
    if isinstance(data, dict):
        for key, value in data.items():
            node = tree.insert(parent, 'end', text=str(key))
            _populate_tree(tree, value, node)
    elif isinstance(data, (list, tuple)):
        for item in data:
            _populate_tree(tree, item, parent)
    else:
        tree.insert(parent, 'end', text='', values=(str(data),))


def dummy_button_command():
    print('dummy command for button executed')


def ellipsis_around(text: str, position: int, length: int) -> str:
    """
    Create a substring of 'text' centered around 'position' with given 'length',
    adding ellipses where text is truncated.

    Args:
    text (str): The original text.
    position (int): The position to center around (0-indexed).
    length (int): The desired length of the output string, including ellipses.

    Returns:
    str: The shortened text with ellipses.

        Examples:
    >>> ellipsis_around("This is a long piece of text that we want to shorten.", 20, 20)
    '...piece of text th...'

    >>> ellipsis_around("Short text", 5, 20)
    'Short text'

    >>> ellipsis_around("Another example of a long string for ellipsis", 12, 15)
    '...example of...'

    >>> ellipsis_around("Start of the text", 0, 10)
    'Start of...'

    >>> ellipsis_around("End of the text", 13, 10)
    '...the text'

    >>> ellipsis_around("Very short", 4, 5)
    'short'

    >>> ellipsis_around("Exactly twenty chars.", 10, 20)
    'Exactly twenty chars.'
    """
    if len(text) <= length:
        return text

    length = max(length, 5)  # Ensure minimum length for ellipses and content
    half_length = (length - 3) // 2  # Subtract 3 for potential ellipses

    start = max(0, min(position - half_length, len(text) - length + 3))
    end = start + length - 3

    if start == 0:
        return f"{text[:end]}..."
    if end >= len(text):
        return f"...{text[-(length - 3):]}"
    return f"...{text[start:end]}..."


def highlight_token(text: str, token: str, length: int) -> str | None:
    start = text.find(token)
    if start == -1:
        return None

    mid_position = start + len(token) // 2
    result = ellipsis_around(text, mid_position, length)

    start_in_result = result.find(token)
    if start_in_result != -1:
        end_in_result = start_in_result + len(token)
        return f"{result[:start_in_result]}*{result[start_in_result:end_in_result]}*{result[end_in_result:]}"

    return result

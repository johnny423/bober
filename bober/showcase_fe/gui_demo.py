import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
from PIL import ImageGrab

text_area = None

with open('rfc_1103.txt', 'r') as f:
    INITIAL_TEXT = f.read()


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


def button1_action():
    text_area.insert(tk.END, "Button 1 clicked!\n")


def button2_action():
    text_area.insert(tk.END, "Button 2 clicked!\n")


def main_menu_window(root, frame_inputs):
    root.title("Main menu")
    add_button(frame_inputs, "Load new file", button1_action, 0, 0)
    add_button(frame_inputs, "Find document", button1_action, 1, 0)
    add_button(frame_inputs, "Word index", button1_action, 2, 0)
    add_button(frame_inputs, "Find word by index", button1_action, 3, 0)
    add_button(frame_inputs, "Manage word groups", button1_action, 4, 0)
    add_button(frame_inputs, "Manage linguistic expressions", button1_action, 5, 0)


def demo_window(root, frame_inputs):
    root.title("Demo window")
    # Add input fields
    input1 = add_input_field(frame_inputs, "Input 1:", 0, 0)
    input2 = add_input_field(frame_inputs, "Input 2:", 1, 0)
    input3 = add_input_field(frame_inputs, "Input 3:", 2, 0)

    # Add buttons
    button1 = add_button(frame_inputs, "Button 1", button1_action, 3, 0)
    button2 = add_button(frame_inputs, "Button 2", button2_action, 3, 1)

    # Add scrollable text area
    global text_area
    text_area = create_scroll_region(root, INITIAL_TEXT, 1, 0)


def load_new_file_window(root, frame_inputs):
    root.title("Load new file")

    add_input_field(frame_inputs, "RFC number:", 1, 0)
    add_input_field(frame_inputs, "Title:", 2, 0)
    add_input_field(frame_inputs, "Author:", 3, 0)
    add_input_field(frame_inputs, "Publish date:", 4, 0)
    add_button(frame_inputs, "Browse files...", button1_action, 5, 0)


def find_document_window(root, frame_inputs):
    root.title("Find document")
    add_input_field(frame_inputs, "Filter by title:", 0, 0)
    add_input_field(frame_inputs, "Filter by RFC ID:", 1, 0)
    add_input_field(frame_inputs, "Filter by author:", 2, 0)
    add_input_field(frame_inputs, "Filter by publish date:", 3, 0)
    add_input_field(frame_inputs, "Filter by content keywords:", 4, 0)
    add_button(frame_inputs, "Search with filters", button1_action, 5, 0)
    add_button(frame_inputs, "Show all documents", button1_action, 5, 1)
    # Add dictionary display region
    example_dict = {
        'Title 1': {
            'word 1': 'context of word 1 + link to document',
            'word 2': 'context of word 2 + link to document',
            'word 3': 'context of word 3 + link to document',
        },
        'Title 2': {
            'word 1': 'context of word 1 + link to document',
            'word 2': 'context of word 2 + link to document',
        },
    }
    dict_display = add_dict_display(root, example_dict, 6, 0, 'Word occurrence', 'Link for source')


def find_word_window(root, frame_inputs):
    root.title("Find word")
    add_input_field(frame_inputs, "Filter by title:", 0, 0)
    add_input_field(frame_inputs, "Filter by word groups:", 1, 0)
    add_input_field(frame_inputs, "Filter by regex:", 2, 0)
    add_button(frame_inputs, "Search with filters", button1_action, 3, 0)
    add_button(frame_inputs, "Show all words", button1_action, 3, 1)
    # Add dictionary display region
    example_dict = {
        'Word 1 (3 occurrences)': {
            'title 1 (2 occurrences)': {
                'section 3, word 17 ; page 2,row 25': 'context of word 1 + link to document',
                'section 7, word 17 ; page 3 row 12': 'context of word 1 + link to document',
            },
            'title 2 (1 occurrences)': {
                'section 2, word 7 in ; page 2 row 14': 'context of word 1 + link to document'
            },
        },
        'Word 2 (1 occurrences)': {
            'title 3 (1 occurrences)': {
                'section 17, word 3 in ; page 9, row 56': 'context of word 2 + link to document'
            },
        },
    }
    dict_display = add_dict_display(root, example_dict, 5, 0, 'Word index', 'Link for source')


def find_word_by_index_window(root, frame_inputs):
    root.title("Find word by index")
    add_input_field(frame_inputs, "Title name:", 0, 0)
    add_input_field(frame_inputs, "Index 1 page:", 1, 0)
    add_input_field(frame_inputs, "Index 1 row:", 2, 0)
    add_input_field(frame_inputs, "Index 2 section:", 3, 0)
    add_input_field(frame_inputs, "Index 2 word:", 4, 0)
    add_button(frame_inputs, "Search by index 1", button1_action, 5, 0)
    add_button(frame_inputs, "Search by index 2", button1_action, 5, 1)
    example_dict = {
        'Word 1': 'context of word 1 + link to document',
        'Word 2': 'context of word 2 + link to document',
        'Word 3': 'context of word 3 + link to document',
        'Word 4': 'context of word 4 + link to document',
        'Word 5': 'context of word 5 + link to document',
        'Word 6': 'context of word 6 + link to document',
        'Word 7': 'context of word 7 + link to document',
    }
    dict_display = add_dict_display(root, example_dict, 6, 0, 'Word', 'Link for source')


def new_word_group_window(root, frame_inputs):  # maybe no need for this
    root.title("New group")
    add_input_field(frame_inputs, "New group name:", 0, 0)
    add_input_field(frame_inputs, "Words to add:", 1, 0)


def word_groups_window(root, frame_inputs):
    root.title("Manage word groups")
    add_input_field(frame_inputs, "Group name:", 0, 0)
    add_input_field(frame_inputs, "Words to add:", 1, 0)
    add_button(frame_inputs, "Create new group", button1_action, 2, 0)
    add_button(frame_inputs, "Add words to group", button1_action, 2, 1)
    add_button(frame_inputs, "Show words for group", button1_action, 2, 2)


def linguistic_expression_window(root, frame_inputs):
    root.title("Manage linguistic expressions")
    add_input_field(frame_inputs, "Expression:", 0, 0)
    add_button(frame_inputs, "Show expression occurrences", button1_action, 2, 0)


def display_doc_window(root, frame_inputs):
    with open('rfc_1103.txt', 'r') as f:
        content = f.read()
    # Add scrollable text area
    global text_area
    text_area = create_scroll_region(root, content, 1, 0, highlight_strings=['method of encapsulating', 'the'])



def capture_screenshot(widget, file_path):
    x = widget.winfo_rootx()
    y = widget.winfo_rooty() - 25
    width = x + widget.winfo_width()
    height = y + widget.winfo_height()
    ImageGrab.grab().crop((x, y, width, height)).save(file_path, "JPEG")


def main():
    # Create the main window
    root = tk.Tk()
    # Create a frame for the input fields
    frame_inputs = ttk.Frame(root, padding="10 10 10 10")
    frame_inputs.grid(row=0, column=0, sticky=(tk.W, tk.E))

    # ------------------ call a function here ------------------------------
    # demo_window(root, frame_inputs)
    # main_menu_window(root, frame_inputs)
    # load_new_file_window(root, frame_inputs)
    # find_document_window(root, frame_inputs)
    find_word_window(root, frame_inputs)
    # find_word_by_index_window(root, frame_inputs)
    # word_groups_window(root, frame_inputs)
    # linguistic_expression_window(root, frame_inputs)
    # display_doc_window(root, frame_inputs)

    # ------------------ end of call a function section ------------------------------

    add_button(frame_inputs, "exit", button1_action, 10, 0)
    # add_button(frame_inputs, "back", button1_action, 10, 0)
    # Capture screenshot after a short delay to ensure the window is fully rendered
    # root.after(200, capture_screenshot, root, filename)
    # Configure the grid to expand properly
    root.columnconfigure(0, weight=1)
    root.rowconfigure(1, weight=1)
    # Run the application
    root.mainloop()


if __name__ == '__main__':
    main()

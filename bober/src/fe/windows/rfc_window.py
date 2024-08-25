import tkinter as tk
from tkinter import Menu, TclError, scrolledtext, simpledialog, ttk

from sqlalchemy.orm import Session

from bober.src.fe.handlers import (
    add_words_to_group,
    create_word_group,
    save_new_phrase,
)
from bober.src.fe.windows.base_window import BaseWindow
from bober.src.parsing.line_parser import get_words_for_line
from bober.src.search.positions import AbsPosition
from bober.src.search.rfc_content import (
    load_rfc_content,
)
from bober.src.search.search_rfc import SearchRFCQuery, search_rfcs
from bober.src.word_groups.word_groups import (
    list_groups,
)


class RFCWindow(BaseWindow):
    def __init__(
        self,
        parent,
        session: Session,
        rfc: int,
        highlights: None | list[AbsPosition] = None,
        abs_line: None | int = None,
    ):
        [meta] = search_rfcs(session, SearchRFCQuery(num=rfc))

        super().__init__(parent, meta.title or "<nameless rfc>", session)
        content = load_rfc_content(self.session, rfc)

        self.create_scroll_region(content, highlights)

        self.file_statistical_data_str = self.get_statistical_data(content)
        self.create_statistical_data_region()
        self.fill_statistical_data_region()

        if abs_line:
            self.scroll_to_line(abs_line)

    @staticmethod
    def get_statistical_data(content):
        word_count = 0
        word_character_count = 0
        non_whitespace_character_count = 0
        total_character_count = 0
        for line in content.split('\n'):
            total_character_count += len(line)
            non_whitespace_character_count += len(
                [char for char in line if not char.isspace()]
            )
            words = get_words_for_line(line)
            word_count += len(words)
            word_character_count += sum([len(word) for word in words])

        return (
            f'Word count: {word_count}; Word character count: {word_character_count}; '
            f'Non-whitespace characters: {non_whitespace_character_count}; '
            f'Total characters: {total_character_count}'
        )

    def create_scroll_region(
        self, initial_text: str, highlights: None | list[AbsPosition] = None
    ):
        self.frame = ttk.Frame(self.main_frame, padding=10)
        self.frame.pack(fill=tk.BOTH, expand=True)

        self.text_frame = ttk.Frame(self.frame)
        self.text_frame.pack(fill=tk.BOTH, expand=True)

        self.line_numbers = tk.Text(
            self.text_frame,
            width=4,
            padx=4,
            pady=4,
            bg='lightgray',
            state='disabled',
        )
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)

        self.text_area = scrolledtext.ScrolledText(
            self.text_frame, wrap=tk.NONE, width=60, height=15, padx=4, pady=4
        )
        self.text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.text_area.insert(tk.END, initial_text)

        self.m = Menu(self.text_area, tearoff=0)
        self.m.add_command(
            label="save as phrase", command=self.save_phrase_popup
        )
        self.m.add_command(
            label="Save word to group", command=self.save_word_to_group_popup
        )
        self.m.add_command(
            label="Show statistical data",
            command=self.show_statistical_data_selection,
        )
        self.text_area.bind("<Button-3>", self.command_popup)

        self.winfo_toplevel().bind("<Button-1>", self.hide_menu)

        self.h_scrollbar = ttk.Scrollbar(
            self.frame, orient=tk.HORIZONTAL, command=self.text_area.xview
        )
        self.h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.text_area.config(xscrollcommand=self.h_scrollbar.set)

        if highlights:
            self.text_area.tag_config('highlight', background='yellow')
            for highlight in highlights:
                start_idx = f"{highlight.line}.{highlight.column}"
                end_idx = f"{start_idx}+{highlight.length}c"
                self.text_area.tag_add('highlight', start_idx, end_idx)

    def create_statistical_data_region(self):
        # Create a new frame for the statistical data section
        self.stats_frame = ttk.Frame(self.frame)
        self.stats_frame.pack(side=tk.BOTTOM, fill=tk.X)

        # Add a label and a text area for the statistical data
        self.stats_label = ttk.Label(self.stats_frame, text="Statistical Data:")
        self.stats_label.pack(side=tk.LEFT, padx=5, pady=5)

        self.stats_text = scrolledtext.ScrolledText(
            self.stats_frame, wrap=tk.NONE, width=60, height=5, padx=4, pady=4
        )
        self.stats_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    def fill_statistical_data_region(self, selection_statistical_data=None):
        self.stats_text.delete('1.0', tk.END)
        statistical_data_str = f'File stats: {self.file_statistical_data_str}\n'
        if selection_statistical_data:
            statistical_data_str += (
                f'Selected section stats: {selection_statistical_data}\n'
            )
        self.stats_text.insert(tk.END, statistical_data_str)

    def save_word_to_group_popup(self):
        try:
            selected_word = self.text_area.get(
                tk.SEL_FIRST, tk.SEL_LAST
            ).strip()
        except TclError:
            self.show_error("No word selected!")
            return

        if not selected_word:
            self.show_error("No word selected!")
            return

        # Check if the selected text is a single word
        if len(selected_word.split()) != 1:
            self.show_error("Please select only one word to add to a group!")
            return

        # Get list of existing groups
        existing_groups = [
            group.group_name for group in list_groups(self.session)
        ]

        # Create a popup to choose between existing group or new group
        choice = simpledialog.askstring(
            "Save Word to Group",
            f"Enter an existing group name or a new group name for '{selected_word}':\n\nExisting groups: {', '.join(existing_groups)}",
            parent=self.frame,
        )

        if not choice:
            return  # User cancelled

        if choice in existing_groups:
            add_words_to_group(
                self.parent, self.session, choice, [selected_word]
            )
            self.show_info(
                f"Word '{selected_word}' added to existing group '{choice}'"
            )
            return

        # new group case
        create_word_group(self.parent, self.session, choice, [selected_word])
        self.show_info(f"Word '{selected_word}' added to new group '{choice}'")

    def show_statistical_data_selection(self):
        try:
            selected_text = self.text_area.get(tk.SEL_FIRST, tk.SEL_LAST)
        except TclError:
            self.show_error("No text selected!")
            return
        if not selected_text:
            self.show_error("No text selected!")
            return

        selection_statistical_data = self.get_statistical_data(selected_text)
        self.fill_statistical_data_region(selection_statistical_data)

    def save_phrase_popup(self):
        try:
            selected_text = self.text_area.get(tk.SEL_FIRST, tk.SEL_LAST)
        except TclError:
            self.show_error("No text selected!")
            return

        if len(selected_text.split()) == 1:
            self.show_error("Please select more than one word for a phrase!")
            return

        def _on_submit():
            phrase_name = name_entry.get()
            if phrase_name:
                save_new_phrase(
                    self.parent, self.session, phrase_name, phrase=selected_text
                )
                popup.destroy()
            else:
                self.show_error("Phrase name cannot be empty!")

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

    def hide_menu(self, event):
        if self.m.winfo_ismapped():
            self.m.unpost()

    def scroll_to_line(self, line_number: int):
        self.text_area.see(f"{line_number}.0")

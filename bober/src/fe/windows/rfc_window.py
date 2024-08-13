import tkinter as tk
from tkinter import Menu, TclError, scrolledtext, ttk
from tkinter import simpledialog

from sqlalchemy.orm import Session

from bober.src.fe.base_window import BaseWindow
from bober.src.phrases.phrases import save_new_phrase
from bober.src.search.rfc_content import (
    get_absolute_line,
    get_absolute_positions,
    load_rfc_content,
)
from bober.src.search.search_rfc import SearchRFCQuery, search_rfcs
from bober.src.word_groups.word_groups import add_words_to_group, create_word_group, list_groups


class RFCWindow(BaseWindow):
    def __init__(
            self,
            parent,
            session: Session,
            rfc: int,
            token: None | str = None,
            line_id: None | int = None,
    ):
        [meta] = search_rfcs(session, SearchRFCQuery(num=rfc))

        super().__init__(parent, meta.title or "<nameless rfc>", session)
        content = load_rfc_content(self.session, rfc)

        highlights = None
        if token:
            highlights = get_absolute_positions(session, rfc, token)

        self.create_scroll_region(content, highlights)

        if line_id:
            line = get_absolute_line(session, rfc, line_id)
            self.scroll_to_line(line)

    def create_scroll_region(self, initial_text: str, highlights: None | list = None):
        self.frame = ttk.Frame(self.main_frame, padding=10)
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
        self.m.add_command(label="Save word to group", command=self.save_word_to_group_popup)
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

    def save_word_to_group_popup(self):
        try:
            selected_word = self.text_area.get(tk.SEL_FIRST, tk.SEL_LAST).strip()
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
        existing_groups = [group.group_name for group in list_groups(self.session)]

        # Create a popup to choose between existing group or new group
        choice = simpledialog.askstring(
            "Save Word to Group",
            f"Enter an existing group name or a new group name for '{selected_word}':\n\nExisting groups: {', '.join(existing_groups)}",
            parent=self.frame
        )

        if not choice:
            return  # User cancelled

        # Check if it's a new group or existing group
        if choice in existing_groups:
            add_words_to_group(self.session, choice, [selected_word])
            self.show_info(f"Word '{selected_word}' added to existing group '{choice}'")
        else:
            create_word_group(self.session, choice, [selected_word])
            self.show_info(f"Word '{selected_word}' added to new group '{choice}'")

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
                save_new_phrase(self.session, phrase_name, phrase=selected_text)
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

    def scroll_to_line(self, line_number: int):
        self.text_area.see(f"{line_number}.0")

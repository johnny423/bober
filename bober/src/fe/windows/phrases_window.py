import tkinter as tk
from tkinter import ttk

from bober.src.db_models import Phrase
from bober.src.fe.base_window import BaseWindow
from bober.src.phrases.phrases import find_phrase_occurrences, save_new_phrase


# todo: doesn't look good
class LinguisticPhraseManager(BaseWindow):
    phrase_name_entry: ttk.Entry
    phrase_entry: ttk.Entry
    phrases_tree: ttk.Treeview
    occurrences_list: tk.Listbox

    def __init__(self, parent, session):
        super().__init__(parent, "Linguistic Phrase Manager", session)
        self.create_widgets()
        self.load_phrases()

    def create_widgets(self):
        left_frame = ttk.Frame(self.main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        self.phrase_name_entry = self.create_entry(left_frame, "Phrase Name:")
        self.phrase_entry = self.create_entry(left_frame, "Phrase:")
        self.create_button(left_frame, "Create Phrase", self.create_phrase)

        right_frame = ttk.Frame(self.main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.phrases_tree = self.create_treeview(
            left_frame,
            columns=("phrase_name", "phrase_content"),
            headings=("Phrase Name", "Phrase Content")
        )
        self.phrases_tree.bind("<<TreeviewSelect>>", self.on_phrase_select)
        self.occurrences_list = self.create_listbox(right_frame)

    def create_phrase(self):
        phrase_name = self.phrase_name_entry.get().strip()
        phrase_content = self.phrase_entry.get().strip()

        if not phrase_name or not phrase_content:
            self.show_warning("Please enter both a phrase name and content.")
            return

        try:
            save_new_phrase(self.session, phrase_name, phrase_content)
            self.phrase_name_entry.delete(0, tk.END)
            self.phrase_entry.delete(0, tk.END)
            self.load_phrases()
        except ValueError as e:
            self.show_error(str(e))

    def search_occurrences(self):
        selected_items = self.phrases_tree.selection()
        if not selected_items:
            self.show_warning("Please select a phrase.")
            return

        phrase_name = self.phrases_tree.item(selected_items[0])['values'][0]

        try:
            occurrences = find_phrase_occurrences(self.session, phrase_name)
            self.occurrences_list.delete(0, tk.END)
            for occurrence in occurrences:
                self.occurrences_list.insert(tk.END, f"RFC {occurrence.rfc_title}: {occurrence.section_index}")
        except ValueError as e:
            self.show_error(str(e))

    def load_phrases(self):
        self.phrases_tree.delete(*self.phrases_tree.get_children())
        phrases = self.session.query(Phrase).all()
        for phrase in phrases:
            self.phrases_tree.insert("", "end", values=(phrase.phrase_name, phrase.content))

    def on_phrase_select(self, event=None):
        self.occurrences_list.delete(0, tk.END)
        self.search_occurrences()

import tkinter as tk
from tkinter import ttk

from bober.src.db_models import Phrase
from bober.src.fe.base_window import BaseWindow
from bober.src.fe.windows.rfc_window import RFCWindow
from bober.src.phrases.phrases import find_phrase_occurrences, save_new_phrase


class LinguisticPhraseManager(BaseWindow):
    phrase_name_entry: ttk.Entry
    phrase_entry: ttk.Entry
    phrases_tree: ttk.Treeview
    occurrences_list: tk.Listbox
    occurrences_id_mapping: dict

    def __init__(self, parent, session):
        super().__init__(parent, "Linguistic Phrase Manager", session)
        self.create_widgets()
        self.load_phrases()
        self.occurrences_id_mapping = {}

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
            headings=("Phrase Name", "Phrase Content"),
        )
        self.phrases_tree.bind("<Button-1>", self.on_phrase_select)
        self.occurrences_list = self.create_listbox(right_frame)
        self.occurrences_list.bind('<Double-1>', self.on_occurrence_select)

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

    def search_occurrences(self, phrase_name):
        try:
            occurrences = find_phrase_occurrences(self.session, phrase_name)
            self.occurrences_list.delete(0, tk.END)
            self.occurrences_id_mapping.clear()
            for i, occurrence in enumerate(occurrences, start=1):
                text = f"{i}: RFC \"{occurrence.rfc_title}\"; section {occurrence.section_index}"
                self.occurrences_list.insert(tk.END, text)
                self.occurrences_id_mapping[str(i)] = occurrence
        except ValueError as e:
            self.show_error(str(e))

    def load_phrases(self):
        self.phrases_tree.delete(*self.phrases_tree.get_children())
        phrases = self.session.query(Phrase).all()
        for phrase in phrases:
            self.phrases_tree.insert(
                "", "end", values=(phrase.phrase_name, phrase.content)
            )

    def on_phrase_select(self, event):
        self.occurrences_list.delete(0, tk.END)
        region = self.phrases_tree.identify('region', event.x, event.y)
        if region != "cell":
            return
        item_id = self.phrases_tree.identify_row(event.y)
        phrase_name = self.phrases_tree.item(item_id)['values'][0]
        self.search_occurrences(phrase_name)

    def on_occurrence_select(self, event=None):
        if not self.occurrences_list.curselection():
            return

        index = self.occurrences_list.curselection()[0]
        display_text = self.occurrences_list.get(index)
        item_id = display_text.split(":")[0].strip()
        selected_occurrence = self.occurrences_id_mapping[item_id]
        rfc_window = RFCWindow(
            self,
            self.session,
            selected_occurrence.rfc_num,
            token=None,
            abs_line=selected_occurrence.abs_line_number,
        )  # todo make phrase highligh
        rfc_window.protocol(
            "WM_DELETE_WINDOW",
            lambda: (rfc_window.destroy(), self.load_phrases()),
        )

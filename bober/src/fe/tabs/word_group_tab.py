import tkinter as tk
from tkinter import ttk

from bober.src.fe.event_system import EVENT_SYSTEM
from bober.src.fe.events import GROUP_UPDATED_EVENT, NEW_GROUP_EVENT
from bober.src.fe.handlers import (
    add_words_to_group,
    create_word_group,
    remove_words_from_group,
)
from bober.src.fe.tabs.base_tab import BaseTab
from bober.src.word_groups.word_groups import (
    list_groups,
    list_words_in_group,
)


class WordGroupTab(BaseTab):
    group_name_entry: ttk.Entry
    word_entry: ttk.Entry
    groups_tree: ttk.Treeview
    words_list: tk.Listbox

    def __init__(self, parent, session):
        super().__init__(parent, session)
        self.load_word_groups()

    def create_widgets(self):
        # Left frame for creating and managing groups
        left_frame = ttk.Frame(self)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        self.group_name_entry = self.create_entry(left_frame, "Group Name:")
        self.create_button(left_frame, "Create Group", self.create_group)

        self.word_entry = self.create_entry(left_frame, "Word:")
        self.create_button(
            left_frame, "Add Word to Group", self.add_word_to_group
        )
        self.create_button(
            left_frame, "Remove Word from Group", self.remove_word_from_group
        )

        # Right frame for displaying groups and words
        right_frame = ttk.Frame(self)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.groups_tree = self.create_treeview(
            right_frame, columns=("group_name",), headings=("Word Groups",)
        )
        self.groups_tree.bind("<<TreeviewSelect>>", self.on_group_select)
        self.words_list = self.create_listbox(right_frame)
        EVENT_SYSTEM.subscribe(NEW_GROUP_EVENT, self.load_word_groups)
        EVENT_SYSTEM.subscribe(GROUP_UPDATED_EVENT, self.on_group_select)

    def create_group(self):
        group_name = self.group_name_entry.get().strip().lower()
        if group_name:
            create_word_group(self.session, group_name, [])
            self.group_name_entry.delete(0, tk.END)
        else:
            self.show_warning("Please enter a group name.")

    def add_word_to_group(self):
        selected_items = self.groups_tree.selection()
        if not selected_items:
            self.show_warning("Please select a group.")
            return

        word = self.word_entry.get().strip().lower()
        if not word:
            self.show_warning("Please enter a word.")
            return

        group_name = self.groups_tree.item(selected_items[0])['values'][0]
        try:
            add_words_to_group(self.session, group_name, [word])
        except ValueError as e:
            self.show_error(e)
        else:
            self.word_entry.delete(0, tk.END)

    def remove_word_from_group(self):
        selected_items = self.groups_tree.selection()
        if not selected_items:
            self.show_warning("Please select a group.")
            return

        selected_words = self.words_list.curselection()
        if not selected_words:
            self.show_warning("Please select a word to remove.")
            return

        group_name = self.groups_tree.item(selected_items[0])['values'][0]
        word = self.words_list.get(selected_words[0])

        try:
            remove_words_from_group(self.session, group_name, [word])
        except Exception as e:
            self.show_error(str(e))

    def load_word_groups(self, event=None):
        self.groups_tree.delete(*self.groups_tree.get_children())
        groups = list_groups(self.session)
        for group in groups:
            self.groups_tree.insert("", "end", values=(group.group_name,))

    def on_group_select(self, event=None):
        selected_items = self.groups_tree.selection()
        if selected_items:
            group_name = self.groups_tree.item(selected_items[0])['values'][0]
            words = list_words_in_group(self.session, group_name)

            self.words_list.delete(0, tk.END)
            for word in words:
                self.words_list.insert(tk.END, word)

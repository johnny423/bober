import tkinter as tk
from tkinter import messagebox, ttk

from bober.src.word_groups.word_groups import (
    add_words_to_group,
    create_word_group,
    list_groups,
    remove_words_from_group,
)


class WordGroupManager(tk.Toplevel):
    def __init__(self, parent, session):
        super().__init__(parent)
        self.session = session

        self.title("Word Group Manager")
        self.geometry("800x600")

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=3)
        self.rowconfigure(0, weight=1)

        self.create_widgets()

    def create_widgets(self):
        self.columnconfigure(0, weight=1)

        self.columnconfigure(1, weight=3)
        self.rowconfigure(0, weight=1)

        # Left frame for inputs and buttons
        left_frame = ttk.Frame(self)
        left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # Group name entry
        self.group_name_label = ttk.Label(left_frame, text="Group Name:")
        self.group_name_label.grid(row=0, column=0, pady=5, sticky="w")
        self.group_name_entry = ttk.Entry(left_frame)
        self.group_name_entry.grid(row=1, column=0, pady=5, sticky="ew")

        # Words entry
        self.words_label = ttk.Label(
            left_frame, text="Words (comma-separated):"
        )
        self.words_label.grid(row=2, column=0, pady=5, sticky="w")
        self.words_entry = ttk.Entry(left_frame)
        self.words_entry.grid(row=3, column=0, pady=5, sticky="ew")

        # Buttons
        self.create_group_button = ttk.Button(
            left_frame, text="Create Group", command=self.create_group
        )
        self.create_group_button.grid(row=4, column=0, pady=5, sticky="ew")

        self.add_words_button = ttk.Button(
            left_frame, text="Add Words", command=self.add_words
        )
        self.add_words_button.grid(row=5, column=0, pady=5, sticky="ew")

        self.remove_words_button = ttk.Button(
            left_frame, text="Remove Words", command=self.remove_words
        )
        self.remove_words_button.grid(row=6, column=0, pady=5, sticky="ew")

        # Configure left_frame grid
        left_frame.columnconfigure(0, weight=1)

        # Right frame for treeview
        right_frame = ttk.Frame(self)
        right_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        # Treeview
        self.tree = ttk.Treeview(
            right_frame, columns=('Words'), show='tree headings'
        )
        self.tree.heading('Words', text='Words')
        self.tree.grid(row=0, column=0, sticky="nsew")

        # Scrollbar for treeview
        scrollbar = ttk.Scrollbar(
            right_frame, orient="vertical", command=self.tree.yview
        )
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Configure right_frame grid
        right_frame.columnconfigure(0, weight=1)
        right_frame.rowconfigure(0, weight=1)

        # Initial population of treeview
        self.refresh_groups()

    def setup_database_events(self):
        # @event.listens_for(TokenGroup, 'after_insert')
        # @event.listens_for(TokenGroup, 'after_update')
        # @event.listens_for(TokenGroup, 'after_delete')
        # @event.listens_for(TokenToGroup, 'after_insert')
        # @event.listens_for(TokenToGroup, 'after_update')
        # @event.listens_for(TokenToGroup, 'after_delete')
        # def receive_after_change(mapper, connection, target):
        #     self.after(100, self.refresh_groups)  # Schedule refresh after 100ms
        ...

    def create_group(self):
        group_name = self.group_name_entry.get()
        words = [word.strip() for word in self.words_entry.get().split(',')]

        try:
            create_word_group(self.session, group_name, words)
            # messagebox.showinfo("Success", f"Group '{group_name}' created successfully.")
            self.refresh_groups()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def add_words(self):
        group_name = self.group_name_entry.get()
        words = [word.strip() for word in self.words_entry.get().split(',')]

        try:
            add_words_to_group(self.session, group_name, words)
            # messagebox.showinfo("Success", f"Words added to group '{group_name}' successfully.")
            self.refresh_groups()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def remove_words(self):
        group_name = self.group_name_entry.get()
        words = [word.strip() for word in self.words_entry.get().split(',')]

        try:
            remove_words_from_group(self.session, group_name, words)
            # messagebox.showinfo("Success", f"Words removed from group '{group_name}' successfully.")
            self.refresh_groups()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def refresh_groups(self):
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        for group in list_groups(self.session):
            group_item = self.tree.insert('', 'end', text=group.group_name)
            word_list = ', '.join([word.token.token for word in group.tokens])
            self.tree.set(group_item, 'Words', word_list)

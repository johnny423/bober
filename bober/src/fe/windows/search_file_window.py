import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime

from bober.src.fe.windows.utils import create_button, create_label, convert_to_datetime, add_dict_display
from bober.src.search.search_rfc import SearchRFCQuery, search_rfcs


class SearchFileWindow(tk.Toplevel):
    def __init__(self, parent, session):
        super().__init__(parent)
        self.title("Search File")
        # self.geometry("400x500")

        # Make this window modal
        self.grab_set()
        self.transient(parent)

        self.parent = parent
        self.session = session

        create_label(self, text="Filters to apply (fill relevant):", placement='pack', placement_args={'pady': 5})

        # Metadata input fields
        create_label(self, text="RFC Number (TODO - not working right now):", placement='pack', placement_args={'pady': 5})  # todo support this filter
        self.rfc_number_entry = tk.Entry(self)
        self.rfc_number_entry.pack(pady=5)

        create_label(self, text="Title:", placement='pack', placement_args={'pady': 5})
        self.title_entry = tk.Entry(self)
        self.title_entry.pack(pady=5)

        create_label(self, text="Published after (YYYY/MM/DD):", placement='pack', placement_args={'pady': 5})
        self.published_after_entry = tk.Entry(self)
        self.published_after_entry.pack(pady=5)

        create_label(self, text="Published before (YYYY/MM/DD):", placement='pack', placement_args={'pady': 5})
        self.published_before_entry = tk.Entry(self)
        self.published_before_entry.pack(pady=5)

        create_label(self, text="Authors:", placement='pack', placement_args={'pady': 5})
        self.author_entry = tk.Entry(self)
        self.author_entry.pack(pady=5)

        create_label(self, text="Contains tokens(space separated):", placement='pack', placement_args={'pady': 5})
        self.contains_tokens = tk.Entry(self)
        self.contains_tokens.pack(pady=5)

        create_button(
            self,
            text="Add Author",
            command=self.add_author,
            placement='pack',
            placement_args={'pady': 5}
        )

        self.authors_listbox = tk.Listbox(self, height=5, width=40)
        self.authors_listbox.pack(pady=5)

        create_button(
            self,
            text="Remove Selected Author",
            command=self.remove_author,
            placement='pack',
            placement_args={'pady': 5}
        )

        create_button(
            self,
            text="Search files",
            command=self.search_files,
            placement='pack',
            placement_args={'pady': 10}
        )

        # Create the Treeview widget for displaying search results
        self.tree = ttk.Treeview(self, columns=("num", "title", "published_at", "authors", "open_file"),
                                 show="headings")
        self.tree.heading("num", text="RFC Number")
        self.tree.heading("title", text="Title")
        self.tree.heading("published_at", text="Published At")
        self.tree.heading("authors", text="Authors")
        self.tree.heading("open_file", text="Open File")

        self.tree.column("num", width=100)
        self.tree.column("title", width=300)
        self.tree.column("published_at", width=150)
        self.tree.column("authors", width=250)
        self.tree.column("open_file", width=100)

        # Add scrollbar to the Treeview
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.scrollbar.set)

        # Pack the Treeview and scrollbar
        self.tree.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        create_button(
            self,
            text="Cancel",
            command=self.destroy,
            bg="lightgray",
            placement='pack',
            placement_args={'pady': 5}
        )

    # todo remove boiler palate code copied from load file window
    def add_author(self):
        author = self.author_entry.get().strip()
        if author:
            self.authors_listbox.insert(tk.END, author)
            self.author_entry.delete(0, tk.END)
        else:
            messagebox.showwarning("Warning", "Please enter an author name.", parent=self)

    def remove_author(self):
        selected = self.authors_listbox.curselection()
        if selected:
            self.authors_listbox.delete(selected)
        else:
            messagebox.showwarning("Warning", "Please select an author to remove.", parent=self)

    def search_files(self):
        rfc_num = self.rfc_number_entry.get()
        title = self.title_entry.get()
        published_after = self.published_after_entry.get()
        published_before = self.published_before_entry.get()
        tokens = self.contains_tokens.get().split()
        authors = list(self.authors_listbox.get(0, tk.END))

        if published_after:
            if not (date_range_min := convert_to_datetime(published_after)):
                messagebox.showerror("Error", 'Published after (should be YYYY/MM/DD)', parent=self)
                return
        else:
            date_range_min = datetime.min
        if published_before:
            if not (date_range_max := convert_to_datetime(published_before)):
                messagebox.showerror("Error", 'Published before (should be YYYY/MM/DD)', parent=self)
                return
        else:
            date_range_max = datetime.max

        # if not any([  # todo add back if needed
        #     rfc_num,
        #     title,
        #     published_at,
        #     self.authors_listbox.size() == 0,
        # ]):
        #     messagebox.showerror("Error", 'Fill at least one filter', parent=self)
        #     return

        search_query = SearchRFCQuery(
            title=title or None,
            date_range=(date_range_min, date_range_max),
            authors=authors or None,
            tokens=tokens or None,
        )
        filtered_rfcs = search_rfcs(self.session, search_query)
        print(f'Found {len(filtered_rfcs)} rfcs')  # todo remove
        self.display_search_results(filtered_rfcs)

    def display_search_results(self, filtered_rfcs):
        # Clear previous results
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Insert new results
        for rfc in filtered_rfcs:
            item = self.tree.insert("", "end", values=(
                rfc.num,
                rfc.title,
                rfc.published_at.strftime("%Y-%m-%d"),
                ", ".join(rfc.authors),
                ""  # Leave this empty, we'll place a button here
            ))

            # Create a button for the "Open file" column
            open_button = tk.Button(self.tree, text="Open", command=lambda num=rfc.num: self.open_file(num))
            self.tree.set(item, "open_file", "")
            self.tree.item(item, tags=(item,))
            self.tree.tag_bind(item, "<<TreeviewSelect>>",
                               lambda event, btn=open_button, itemid=item: self.place_button(event, btn, itemid))

    def place_button(self, event, button, item):
        selection = self.tree.selection()
        if selection and item == selection[0]:
            bbox = self.tree.bbox(item, "open_file")
            if bbox:
                button.place(x=bbox[0], y=bbox[1], width=bbox[2], height=bbox[3])
        else:
            button.place_forget()

    def open_file(self, rfc_num):
        print(f"Open file clicked for RFC number: {rfc_num}")

    def destroy(self):
        self.grab_release()
        super().destroy()

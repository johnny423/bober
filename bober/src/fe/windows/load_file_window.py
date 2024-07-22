import tkinter as tk


class LoadFileWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Load File")
        self.geometry("300x200")  # Set a default size

        # Add some content to the window
        label = tk.Label(self, text="This is the Load File window")
        label.pack(pady=20)

        # Add a close button
        close_button = tk.Button(self, text="Close", command=self.destroy)
        # close_button.pack(pady=10)


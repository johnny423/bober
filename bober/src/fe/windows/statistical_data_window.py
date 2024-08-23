import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
from sqlalchemy.orm import Session
from typing import Optional
from bober.src.fe.windows.base_window import BaseWindow
from bober.src.parsing.statistical_analysis import StringStatisticsManager


class StatisticalDataWindow(BaseWindow):
    def __init__(
            self,
            parent: tk.Tk,
            title: str,
            stats_manager: StringStatisticsManager,
            session: Optional[Session] = None
    ):
        super().__init__(parent, title, session, "500x200")
        self.stats_manager = stats_manager
        self.create_widgets()

    def create_widgets(self):
        label = ttk.Label(self.main_frame, text="Select a statistic type to display:", font=("Arial", 12))
        label.pack(pady=(10, 5))

        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(pady=10)

        word_button = ttk.Button(button_frame, text="Words", command=lambda: self.display_stats(self.stats_manager.get_word_stats()))
        word_button.pack(side=tk.LEFT, padx=5)

        char_button = ttk.Button(button_frame, text="Word Characters", command=lambda: self.display_stats(self.stats_manager.get_word_char_stats()))
        char_button.pack(side=tk.LEFT, padx=5)

        custom_button = ttk.Button(button_frame, text="Non white characters", command=lambda: self.display_stats(self.stats_manager.get_non_white_char_stats()))
        custom_button.pack(side=tk.LEFT, padx=5)

        custom_button = ttk.Button(button_frame, text="All characters", command=lambda: self.display_stats(self.stats_manager.get_all_char_stats()))
        custom_button.pack(side=tk.LEFT, padx=5)

        # Create scrolled text widget
        self.text_area = scrolledtext.ScrolledText(self.main_frame, wrap=tk.WORD, width=60, height=20)
        self.text_area.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        self.display_stats(self.stats_manager.get_word_stats())

    def display_stats(self, stats):
        self.text_area.delete('1.0', tk.END)  # Clear previous content
        self.text_area.insert(tk.END, stats)

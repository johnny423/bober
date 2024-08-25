from collections import defaultdict

from bober.src.parsing.line_parser import get_words_for_line


class StringStatistics:
    def __init__(self, input_string, line_to_page_mapping, split_function, split_description):
        self.split_description = split_description
        self.total_items = 0
        self.max_items_line = 0
        self.min_items_line = float('inf')
        items_per_page = defaultdict(int)
        line_count = 0

        lines = input_string.split('\n')
        starting_line = min(line_to_page_mapping.keys())
        for i, line in enumerate(lines):
            items = split_function(line)
            item_count = len(items)
            if not item_count:
                continue

            self.total_items += item_count
            self.max_items_line = max(self.max_items_line, item_count)
            self.min_items_line = min(self.min_items_line, item_count)
            page_number = line_to_page_mapping[starting_line + i]
            items_per_page[page_number] += item_count
            line_count += 1

        self.avg_items_per_line = (
            self.total_items / line_count if line_count > 0 else 0
        )
        self.avg_items_page = (
            self.total_items / len(items_per_page) if len(items_per_page) > 0 else 0
        )
        self.min_items_page = min(items_per_page.values()) if len(items_per_page) > 0 else 0
        self.max_items_page = max(items_per_page.values()) if len(items_per_page) > 0 else 0

    def __str__(self):
        return (
            f"Split type: {self.split_description}\n"
            f"Total items: {self.total_items}\n"
            f"Maximum items in a line: {self.max_items_line}\n"
            f"Maximum items in a page: {self.max_items_page}\n"
            f"Minimum items in a line: {self.min_items_line}\n"
            f"Minimum items in a page: {self.min_items_page}\n"
            f"Average items per line: {self.avg_items_per_line:.2f}\n"
            f"Average items per page: {self.avg_items_page:.2f}\n"
        )


class StringStatisticsManager:
    def __init__(self, input_string, line_to_page_mapping):
        self.input_string = input_string
        self.line_to_page_mapping = line_to_page_mapping
        self.word_stats = None
        self.word_char_stats = None
        self.non_white_char_stats = None
        self.all_char_stats = None

    def get_word_stats(self):
        if not self.word_stats:
            self.word_stats = StringStatistics(
                input_string=self.input_string,
                line_to_page_mapping=self.line_to_page_mapping,
                split_function=get_words_for_line,
                split_description="Words",
            )
        return str(self.word_stats)

    def get_word_char_stats(self):
        if not self.word_char_stats:
            self.word_char_stats = StringStatistics(
                input_string=self.input_string,
                line_to_page_mapping=self.line_to_page_mapping,
                split_function=lambda line: [
                    char for word in get_words_for_line(line) for char in word
                ],
                split_description="Word characters",
            )
        return str(self.word_char_stats)

    def get_non_white_char_stats(self):
        if not self.non_white_char_stats:
            self.non_white_char_stats = StringStatistics(
                input_string=self.input_string,
                line_to_page_mapping=self.line_to_page_mapping,
                split_function=lambda line: [
                    char for char in line if not char.isspace()
                ],
                split_description="Non white characters",
            )
        return str(self.non_white_char_stats)

    def get_all_char_stats(self):
        if not self.all_char_stats:
            self.all_char_stats = StringStatistics(
                input_string=self.input_string,
                line_to_page_mapping=self.line_to_page_mapping,
                split_function=lambda line: list(line),
                split_description="All characters",
            )
        return str(self.all_char_stats)

from bober.src.parsing.line_parser import get_words_for_line


class StringStatistics:
    def __init__(self, input_string, split_function, split_description):
        self.split_description = split_description
        self.total_items = 0
        self.max_items = 0
        self.min_items = float('inf')
        self.avg_items = 0
        self.line_count = 0

        lines = input_string.split('\n')
        for line in lines:
            items = split_function(line)
            item_count = len(items)

            self.total_items += item_count
            self.max_items = max(self.max_items, item_count)
            self.min_items = min(self.min_items, item_count)
            self.line_count += 1

        self.avg_items = (
            self.total_items / self.line_count if self.line_count > 0 else 0
        )

    def __str__(self):
        return (
            f"Split type: {self.split_description}\n"
            f"Total items: {self.total_items}\n"
            f"Maximum items in a line: {self.max_items}\n"
            f"Minimum items in a line: {self.min_items}\n"
            f"Average items per line: {self.avg_items:.2f}"
        )


class StringStatisticsManager:  # todo maybe add page stats as well
    def __init__(self, input_string):
        self.input_string = input_string
        self.word_stats = None
        self.word_char_stats = None
        self.non_white_char_stats = None
        self.all_char_stats = None

    def get_word_stats(self):
        if not self.word_stats:
            self.word_stats = StringStatistics(
                input_string=self.input_string,
                split_function=get_words_for_line,
                split_description="Words",
            )
        return str(self.word_stats)

    def get_word_char_stats(self):
        if not self.word_char_stats:
            self.word_char_stats = StringStatistics(
                input_string=self.input_string,
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
                split_function=lambda line: list(line),
                split_description="All characters",
            )
        return str(self.all_char_stats)

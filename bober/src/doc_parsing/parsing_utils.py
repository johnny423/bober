from typing import List

# todo general question: do we interpret a different capitalization of the same word as the same word? Need to address

# todo had to remove pyproject.toml to run, need to debug


def parse_by_word_position(text: str) -> List[List[str]]:
    """
    Split a text into words in lines
    :param text: Input text, may contain multiple lines
    :return: A list of lines, each line is a list of separate words, no white spaces
    """
    lines = text.splitlines()
    return [split_line(line, ' ,.!?') for line in lines]


def split_line(line: str, delimiters: str) -> List[str]:
    """
    Split a line of text into it's individual words
    :param line: input string, expected to not have newline characters
    :param delimiters: string containing all characters to be used as delimiters
    :return: list of words without whitespaces and other delimiters
    """
    # todo decide how to handle punctuation, currently it is being dropped
    for char in delimiters:
        line = line.replace(char, ' ')
    split_text = line.split(' ')
    filtered_split = [s.strip() for s in split_text if s.strip()]
    return filtered_split

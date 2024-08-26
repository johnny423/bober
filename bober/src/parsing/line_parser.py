import re
from typing import List

from bober.src.parsing.parsed_types import ParsedLine, ParsedToken


def get_words_for_line(line: str) -> List[str]:
    words = re.findall(r'\b\w+\b', line)
    return words


def parse_line(line: str, abs_num: int) -> ParsedLine:
    stripped = line.lstrip()
    words = get_words_for_line(line)

    tokens = []
    current_position = 0
    for word in words:
        if not any(char.isalnum() for char in word):
            # skip words without numeric or alpha
            continue

        start = stripped.index(word, current_position)
        token = ParsedToken(
            word=word,
            start=start,
        )
        tokens.append(token)
        current_position = start + len(word)

    return ParsedLine(
        absolute_line=abs_num,
        text=stripped,
        indentation=(len(line) - len(stripped)),
        tokens=tokens,
    )

import re

from bober.src.parsing.parsed_types import ParsedLine, ParsedToken


def parse_line(line: str) -> ParsedLine:
    striped = line.strip()
    words = re.findall(r'\b\w+\b', striped)

    tokens = []
    current_position = 0
    for word in words:
        start = striped.index(word, current_position)
        token = ParsedToken(
            word=word,
            start=start,
        )
        tokens.append(token)
        current_position = start + len(word)

    return ParsedLine(
        text=striped,
        indentation=(len(line) - len(striped)),
        tokens=tokens,
    )

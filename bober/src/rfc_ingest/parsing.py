import re
import string
from typing import Iterator, Iterable

from pydantic import BaseModel

from bober.src.db_models import TokenPosition, RfcSection
import nltk
from nltk.stem import PorterStemmer

nltk.download("punkt")
STEMMER = PorterStemmer()


class Paragraph(BaseModel):
    lines: list[str]
    row_start: int
    indentation: int
    page: int


def parse_content(
        rfc_num: int, content: str
) -> Iterator[tuple[str, TokenPosition]]:
    for section_index, paragraph in enumerate(into_paragraphs(content)):
        section = RfcSection(
            rfc_num=rfc_num,
            index=section_index,
            content="\n".join(paragraph.lines),
            row_start=paragraph.row_start,
            row_end=paragraph.row_start + len(paragraph.lines),
            indentation=paragraph.indentation,
        )

        line_start_index = 0
        for line_num, line in enumerate(paragraph.lines, 0):
            for index, (token, position) in enumerate(tokenize(line)):
                pos = TokenPosition(
                    rfc_num=rfc_num,
                    page=paragraph.page,
                    row=paragraph.row_start + line_num,
                    section=section,
                    position=line_start_index + position,
                    index=index,
                )
                yield token, pos

            line_start_index += len(line)


def tokenize(line: str) -> Iterable[tuple[str, int]]:
    # Remove punctuation
    without_punc = line.translate(str.maketrans("", "", string.punctuation))
    tokens = nltk.word_tokenize(without_punc)

    # Find positions of each token
    token_positions = []
    current_pos = 0
    for token in tokens:
        pos = line.find(token, current_pos)
        token_positions.append((token, pos))
        current_pos = pos + len(token)

    return token_positions


def into_paragraphs(text: str) -> Iterator[Paragraph]:
    lines = text.splitlines()

    current_paragraph = []
    start_row = None
    current_indentation = None
    current_page = 1
    page_end_pattern = re.compile(r'(?:(?:\S+\s+)?\S+\s+)?\[Page \d+\]\s*$')

    for i, line in enumerate(lines, 1):
        stripped_line = line.strip()
        if stripped_line:
            if not current_paragraph:
                start_row = i
                current_indentation = len(line) - len(line.lstrip())
            current_paragraph.append(line)

            # Check if this line is a page ending
            if page_end_pattern.search(line):
                if current_paragraph:
                    yield Paragraph(
                        lines=current_paragraph,
                        row_start=start_row,
                        indentation=current_indentation,
                        page=current_page,
                    )

                    current_paragraph = []
                    start_row = None
                    current_indentation = None
                current_page += 1

        elif current_paragraph:
            yield Paragraph(
                lines=current_paragraph,
                row_start=start_row,
                indentation=current_indentation,
                page=current_page,
            )

            current_paragraph = []
            start_row = None
            current_indentation = None

    if current_paragraph:
        yield Paragraph(
            lines=current_paragraph,
            row_start=start_row,
            indentation=current_indentation,
            page=current_page,
        )


if __name__ == '__main__':
    line = "Hello, world! This is a test."
    for t, i in tokenize(line):
        print(line[i:].startswith(t))

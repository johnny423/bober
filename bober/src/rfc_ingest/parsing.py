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
    for index, paragraph in enumerate(into_paragraphs(content)):
        section = RfcSection(
            rfc_num=rfc_num,
            index=index,
            content="\n".join(paragraph.lines),
            row_start=paragraph.row_start,
            row_end=paragraph.row_start + len(paragraph.lines),
            indentation=paragraph.indentation,
        )

        for line_num, line in enumerate(paragraph.lines, 0):
            for token in tokenize(line):
                pos = TokenPosition(
                    rfc_num=rfc_num,
                    page=paragraph.page,
                    row=paragraph.row_start + line_num,
                    section=section,
                )
                yield token, pos


def tokenize(line: str) -> Iterable[str]:
    without_punc = line.translate(str.maketrans("", "", string.punctuation))
    return nltk.word_tokenize(without_punc)


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

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
                token_position = line_start_index + line_num + position
                pos = TokenPosition(
                    rfc_num=rfc_num,
                    page=paragraph.page,
                    row=paragraph.row_start + line_num,
                    section=section,
                    start_position=token_position,
                    end_position=token_position + len(token),
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
            current_paragraph.append(stripped_line)

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
    line = """
    
   When we consider using graphics stations or other sophisticated
   terminals under the control of a remote HOST, the problem becomes more
   severe. We must look for some method which allows us to use our most
   sophisticated equipment as much as possible as if we were connected
   directly to the remote computer.

Error Checking

   The point is made by Jeff Rulifson at SRI that error checking at major
   software interfaces is always a good thing. He points to some
   experience at SRI where it has saved much dispute and wasted effort.
   On these grounds, we would like to see some HOST to HOST checking.
   Besides checking the software interface, it would also check the
   HOST-IMP transmission hardware.  (BB&N claims the HOST-IMP hardware
   will be as reliable as the internal registers of the HOST.  We believe

"""
    for t, i in parse_content(1, line):
        position = i.start_position
        if not i.section.content[position:].startswith(t):
            print(t, "=>", f"'{i.section.content[position: position + 50]}'")

import json
import os
import re
from collections import defaultdict
from pathlib import Path
from typing import Iterator

from pydantic import BaseModel
from sqlalchemy.orm import Session

from bober.src.db_models import Rfc, Author, RfcSection, TokenPosition, Token


class Section(BaseModel):
    lines: list[str]
    row_start: int
    indentation: int
    page: int


def load_examples(session: Session):
    tokens = defaultdict(list)

    with open("examples/examples.json") as f:
        d = json.load(f)

    rfcs = []
    for xx in d:
        number = int(xx["num"])
        content = Path(f"examples/{number}.txt").read_text()

        for index, paragraph in enumerate(into_paragraphs(content)):
            section = RfcSection(
                rfc_num=number,
                index=index,
                content="\n".join(paragraph.lines),
                row_start=paragraph.row_start,
                row_end=paragraph.row_start + len(paragraph.lines),
                indentation=paragraph.indentation,
            )

            for line_num, line in enumerate(paragraph.lines, 0):
                for token in re.findall(r'\b\w+\b', line.lower()):
                    pos = TokenPosition(
                        rfc_num=number,
                        page=paragraph.page,
                        row=paragraph.row_start + line_num,
                        section=section,
                    )
                    tokens[token].append(pos)

        rfc = Rfc(
            num=number,
            title=xx["title"],
            published_at=xx["publish_at"],
            authors=[Author(author_name=name) for name in xx["authors"]],
        )

        rfcs.append(rfc)

    tzs = []
    for token, poses in tokens.items():
        token = Token(token=token, stem=token, token_positions=poses)
        tzs.append(token)

    session.add_all(rfcs)
    session.add_all(tzs)
    session.commit()


def into_paragraphs(text: str) -> Iterator[Section]:
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
                    yield Section(
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
            yield Section(
                lines=current_paragraph,
                row_start=start_row,
                indentation=current_indentation,
                page=current_page,
            )

            current_paragraph = []
            start_row = None
            current_indentation = None

    if current_paragraph:
        yield Section(
            lines=current_paragraph,
            row_start=start_row,
            indentation=current_indentation,
            page=current_page,
        )

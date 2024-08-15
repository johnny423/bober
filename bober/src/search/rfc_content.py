from itertools import repeat

from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from bober.src.db_models import RfcLine, RfcSection, Token, TokenPosition


class AbsPosition(BaseModel):
    """
    This is a position of a word in the whole text
        @line - the line count in the whole file (starting from 1)
        @start - the index of the word within the given line
        @length - the amount of characters after the starting position
    """

    line: int
    start: int
    length: int


def load_rfc_content(session: Session, rfc_num: int) -> str | None:
    sections = (
        session.query(RfcSection)
        .options(selectinload(RfcSection.lines))
        .filter(RfcSection.rfc_num == rfc_num)
        .order_by(RfcSection.index)
        .all()
    )
    if not sections:
        return None

    curr_page = 1
    curr_line = 1  # counting lines in page starts from 1
    raw_lines = []

    section: RfcSection
    for section in sections:
        if curr_page != section.page:
            curr_page = section.page
            curr_line = 1  # counting lines in page starts from 1

        empty_lines_count = section.row_start - curr_line
        raw_lines.extend(repeat("", empty_lines_count))
        curr_line = section.row_start

        line: RfcLine
        for line in section.lines:
            raw_line = " " * line.indentation + line.line
            raw_lines.append(raw_line)
            curr_line += 1

    return "\n".join(raw_lines)


def get_absolute_line(
    session: Session, rfc_num: int, line_id: int
) -> None | int:
    query = (
        session.query(
            (RfcLine.abs_line_number).label(
                'line'
            )
        )
        .join(RfcSection, RfcSection.id == RfcLine.section_id)
        .filter(RfcSection.rfc_num == rfc_num)
        .filter(RfcLine.id == line_id)
    )
    res = query.one_or_none()
    if res:
        return res.line
    return None


def get_absolute_positions(
    session: Session, rfc_num: int, stem: str
) -> list[AbsPosition]:
    query = (
        session.query(
            RfcLine.indentation,
            TokenPosition.start_position,
            TokenPosition.end_position,
            (RfcLine.abs_line_number).label(
                'line'
            ),
        )
        .join(TokenPosition, TokenPosition.line_id == RfcLine.id)
        .join(Token, Token.id == TokenPosition.token_id)
        .join(RfcSection, RfcSection.id == RfcLine.section_id)
        .filter(Token.stem == stem)
        .filter(RfcSection.rfc_num == rfc_num)
    )
    abs_pos = []
    for pos in query.all():
        abs_position = AbsPosition(
            line=pos.line,
            start=pos.indentation + pos.start_position,
            length=pos.end_position - pos.start_position,
        )
        abs_pos.append(abs_position)
    return abs_pos

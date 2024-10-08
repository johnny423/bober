from itertools import repeat
from typing import Dict

from sqlalchemy import and_
from sqlalchemy.orm import Session, selectinload

from bober.src.db_models import RfcLine, RfcSection, Token, TokenPosition
from bober.src.search.positions import AbsPosition


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


def get_absolute_positions(
    session: Session, rfc_num: int, token: str
) -> list[AbsPosition]:
    query = (
        session.query(
            RfcLine.indentation,
            TokenPosition.start_position,
            TokenPosition.end_position,
            (RfcLine.abs_line_number).label('line'),
        )
        .join(TokenPosition, TokenPosition.line_id == RfcLine.id)
        .join(Token, Token.id == TokenPosition.token_id)
        .join(RfcSection, RfcSection.id == RfcLine.section_id)
        .filter(Token.token == token)
        .filter(RfcSection.rfc_num == rfc_num)
    )
    abs_pos = []
    for pos in query.all():
        abs_position = AbsPosition(
            line=pos.line,
            column=pos.indentation + pos.start_position,
            length=pos.end_position - pos.start_position,
        )
        abs_pos.append(abs_position)
    return abs_pos


def get_pages_for_line_numbers(
    session: Session, rfc_num: int, start_line: int, end_line: int
) -> Dict[int, int]:
    result = {}

    # Query the RfcLine and RfcSection tables
    lines = (
        session.query(RfcLine.abs_line_number, RfcSection.page)
        .join(RfcSection, RfcLine.section_id == RfcSection.id)
        .filter(
            and_(
                RfcSection.rfc_num == rfc_num,
                RfcLine.abs_line_number >= start_line,
                RfcLine.abs_line_number <= end_line,
            )
        )
        .order_by(RfcLine.abs_line_number)
        .all()
    )

    # Process the results
    for line_number, page in lines:
        result[line_number] = page

    return result

from itertools import repeat

from pydantic import BaseModel
from sqlalchemy import func, literal, select
from sqlalchemy.orm import Session, selectinload

from bober.src.db_models import RfcLine, RfcSection, TokenPosition, Token


class AbsPosition(BaseModel):
    """
    todo:
    """
    start: int
    end: int


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


def get_absolute_position(session: Session, rfc_num: int, token: str):
    abs_line_query = get_section_absolute_line_query(rfc_num).subquery()
    query = (
        session.query(
            RfcLine.indentation,
            TokenPosition.start_position,
            TokenPosition.end_position,
            (RfcLine.line_number + abs_line_query.c.absolute_start_line).label('absolute_line_number')
        )
        .join(TokenPosition, TokenPosition.line_id == RfcLine.id)
        .join(Token, Token.id == TokenPosition.token_id)
        .join(RfcSection, RfcSection.id == RfcLine.section_id)
        .join(abs_line_query, RfcSection.id == abs_line_query.c.id)
        .filter(Token.token == token)
        .filter(RfcSection.rfc_num == rfc_num)
    )
    abs_pos = query.all()
    return abs_pos


def get_section_absolute_line_query(rfc_num: int):
    page_lines = (
        select(
            RfcSection.page,
            func.max(RfcSection.row_end).label('page_line_count')
        )
        .where(RfcSection.rfc_num == rfc_num)
        .group_by(RfcSection.page)
        .subquery()
    )

    cumulative_lines = (
        select(
            page_lines.c.page,
            page_lines.c.page_line_count,
            func.sum(page_lines.c.page_line_count).over(
                order_by=page_lines.c.page,
                rows=(None, -1)
            ).label('previous_lines')
        )
        .select_from(page_lines)
        .subquery()
    )

    query = (
        select(
            RfcSection.id,
            (func.coalesce(cumulative_lines.c.previous_lines, 0) + RfcSection.row_start).label('absolute_start_line')
        ).options(selectinload(RfcSection.lines))
        .select_from(RfcSection)
        .join(cumulative_lines, RfcSection.page == cumulative_lines.c.page)
        .where(RfcSection.rfc_num == rfc_num)
        .order_by(RfcSection.page, RfcSection.row_start)
    )

    return query

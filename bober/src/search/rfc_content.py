from itertools import repeat

from sqlalchemy.orm import Session, selectinload

from bober.src.db_models import RfcLine, RfcSection


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

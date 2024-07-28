from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from bober.src.db_models import RfcLine, RfcSection


class RFCSection(BaseModel):
    content: str
    row_start: int
    row_end: int
    indentation: int


def rebuild_content(sections: list[RFCSection]) -> str:
    if not sections:
        return ""

    sorted_sections = sorted(sections, key=lambda s: s.row_start)

    result = []
    current_row = 1
    max_row = max(section.row_end for section in sorted_sections)

    for section in sorted_sections:
        # Fill in any gaps between sections
        result.extend([""] * (section.row_start - current_row))

        # Add the section content with proper indentation
        indent = " " * section.indentation
        result.extend(indent + line for line in section.content.splitlines())

        current_row = section.row_end + 1

    result.extend([""] * (max_row - current_row + 1))
    return "\n".join(result)


def fetch_rfc_sections(session: Session, rfc_num: int) -> list[RFCSection]:
    results = (
        session.query(
            RfcSection.id,
            func.min(RfcLine.id).label('row_start'),
            func.max(RfcLine.id).label('row_end'),
            func.min(RfcLine.indentation).label('indentation'),
            func.group_concat(RfcLine.line, '\n').label('content'),
        )
        .join(RfcSection.lines)
        .filter(RfcSection.rfc_num == rfc_num)
        .group_by(RfcSection.id)
        .order_by(RfcSection.index)
    )

    output = []
    for row in results:
        section = RFCSection(
            content=row.content,
            row_start=row.row_start,
            row_end=row.row_end,
            indentation=row.indentation,
        )
        output.append(section)

    return output

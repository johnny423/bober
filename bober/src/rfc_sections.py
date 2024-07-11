from sqlalchemy.orm import Session

from bober.src.db_models import RfcSection
from bober.src.rfc_content import RFCSection


def fetch_rfc_sections(session: Session, rfc_num: int) -> list[RFCSection]:
    results = (
        session.query(RfcSection)
        .filter(RfcSection.rfc_num == rfc_num)
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

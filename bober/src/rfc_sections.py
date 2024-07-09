from bober.src.db_models import RfcSection
from bober.src.dtos import RFCSection


def fetch_rfc_sections(session, rfc_num) -> list[RFCSection]:
    results = (
        session.query(RfcSection.content)
        .filter(RfcSection.rfc_num in rfc_num)
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

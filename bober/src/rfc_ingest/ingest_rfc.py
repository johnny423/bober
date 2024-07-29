import datetime
from collections import defaultdict

from sqlalchemy import select
from sqlalchemy.orm import Session

from bober.src.db_models import Rfc, RfcLine, RfcSection, Token, TokenPosition
from bober.src.parsing.parsed_types import ParsedDocument, ParsedToken


def ingest_rfc(
    session: Session,
    rfc_num: int,
    rfc_title: str,
    rfc_published_at: datetime.date,
    parsed_doc: ParsedDocument,
) -> Rfc:
    # Create or get the Rfc object
    rfc = session.execute(
        select(Rfc).where(Rfc.num == rfc_num)
    ).scalar_one_or_none()
    if not rfc:
        rfc = Rfc(num=rfc_num, title=rfc_title, published_at=rfc_published_at)
        session.add(rfc)

    # Collect all unique tokens
    parsed_tokens: dict[str, ParsedToken] = {}
    token_positions = defaultdict(list)

    for section_index, parsed_section in enumerate(parsed_doc.sections):
        section = RfcSection(
            rfc=rfc,
            index=section_index,
            page=parsed_section.page,
            row_start=parsed_section.page_line,
            row_end=parsed_section.page_line + len(parsed_section.lines) - 1,
        )
        session.add(section)

        for line_num, parsed_line in parsed_section.lines.values():
            line = RfcLine(
                section=section,
                index=line_num,
                line=parsed_line.text,
                indentation=parsed_line.indentation,
            )
            session.add(line)

            for token_index, parsed_token in enumerate(parsed_line.tokens):
                parsed_tokens[parsed_token.word] = parsed_token
                token_positions[parsed_token.word].append(
                    TokenPosition(
                        line=line,
                        start_position=parsed_token.start,
                        end_position=parsed_token.end,
                        index=token_index,
                    )
                )

    # tokens
    query_existing_tokens = session.execute(
        select(Token).where(Token.token.in_(parsed_tokens.keys()))
    )
    existing_tokens = {
        token.token: token for token in query_existing_tokens.scalars()
    }

    new_tokens = []
    for parsed_token in parsed_tokens.values():
        if parsed_token.word not in existing_tokens:
            new_token = Token(token=parsed_token.word, stem=parsed_token.stem)
            new_tokens.append(new_token)
            existing_tokens[parsed_token.word] = new_token

    session.add_all(new_tokens)
    session.flush()  # This will assign ids to the new tokens

    # positions
    for tokens, positions in token_positions.items():
        token = existing_tokens[tokens]
        for position in positions:
            position.token = token

        session.add_all(positions)

    session.flush()
    return rfc

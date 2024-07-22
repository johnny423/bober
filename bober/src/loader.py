import json
from collections import defaultdict
from pathlib import Path

from sqlalchemy.orm import Session

from bober.src.db_models import Rfc, Author, Token
from bober.src.rfc_ingest.parsing import parse_content, STEMMER


def load_examples(session: Session):
    tokens = defaultdict(list)

    example_dir_path = Path("examples")
    with open(example_dir_path / "examples.json") as f:
        rfcs_metadata = json.load(f)

    rfcs = []
    for rfc_metadata in rfcs_metadata:
        rfc_num = int(rfc_metadata["num"])
        content = (example_dir_path / f"{rfc_num}.txt").read_text()

        for token, position in parse_content(rfc_num, content):
            tokens[token].append(position)

        rfc = Rfc(
            num=rfc_num,
            title=rfc_metadata["title"],
            published_at=rfc_metadata["publish_at"],
            authors=[
                Author(author_name=name) for name in rfc_metadata["authors"]
            ],
        )

        rfcs.append(rfc)

    tzs = []
    for token, poses in tokens.items():
        stem = STEMMER.stem(token)
        token = Token(token=token, stem=stem, token_positions=poses)
        tzs.append(token)

    session.add_all(rfcs)
    session.add_all(tzs)
    session.commit()

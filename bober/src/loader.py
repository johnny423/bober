import json
from pathlib import Path

from sqlalchemy.orm import Session

from bober.src.rfc_ingest.load_from_file import load_single_file


def load_examples(session: Session):
    example_dir_path = Path("../resources/examples")
    with open(example_dir_path / "examples.json") as f:
        rfcs_metadata = json.load(f)

    for rfc_metadata in rfcs_metadata:
        rfc_num = int(rfc_metadata["num"])
        file_path = example_dir_path / f"{rfc_num}.txt"
        load_single_file(session, file_path, rfc_metadata)

from sqlalchemy.orm import Session

from bober.src.fe.events import (
    GROUP_UPDATED_EVENT,
    NEW_GROUP_EVENT,
    NEW_PHRASE_EVENT,
    RFC_ADDED_EVENT,
)
from bober.src.phrases.phrases import save_new_phrase as _save_new_phrase
from bober.src.rfc_ingest.load_from_file import RFCMetadata, load_single_file
from bober.src.word_groups.word_groups import (
    add_words_to_group as _add_words_to_groups,
)
from bober.src.word_groups.word_groups import (
    create_word_group as _create_word_group,
)
from bober.src.word_groups.word_groups import (
    remove_words_from_group as _remove_words_from_group,
)


def save_new_phrase(widget, session, phrase_name, phrase):
    _save_new_phrase(session, phrase_name, phrase)
    widget.event_generate(NEW_PHRASE_EVENT, when="tail")


def create_word_group(
    widget, session: Session, group_name: str, words: list[str]
):
    _create_word_group(session, group_name, words)
    widget.event_generate(NEW_GROUP_EVENT, when="tail")


def add_words_to_group(
    widget, session: Session, group_name: str, words: list[str]
):
    _add_words_to_groups(session, group_name, words)
    widget.event_generate(GROUP_UPDATED_EVENT, when="tail")


def remove_words_from_group(
    widget, session: Session, group_name: str, words: list[str]
):
    _remove_words_from_group(session, group_name, words)
    widget.event_generate(GROUP_UPDATED_EVENT, when="tail")


def add_rfc(
    widget, session: Session, file_path: str, rfc_metadata: RFCMetadata
):
    load_single_file(session, file_path, rfc_metadata)
    widget.event_generate(RFC_ADDED_EVENT, when="tail")

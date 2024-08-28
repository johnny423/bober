from sqlalchemy.orm import Session

from bober.src.fe.event_system import EVENT_SYSTEM
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


def save_new_phrase(session, phrase_name, phrase):
    _save_new_phrase(session, phrase_name, phrase)
    EVENT_SYSTEM.publish(NEW_PHRASE_EVENT)


def create_word_group(
    session: Session, group_name: str, words: list[str]
):
    _create_word_group(session, group_name, words)
    EVENT_SYSTEM.publish(NEW_GROUP_EVENT)


def add_words_to_group(
    session: Session, group_name: str, words: list[str]
):
    _add_words_to_groups(session, group_name, words)
    EVENT_SYSTEM.publish(GROUP_UPDATED_EVENT)


def remove_words_from_group(
    session: Session, group_name: str, words: list[str]
):
    _remove_words_from_group(session, group_name, words)
    EVENT_SYSTEM.publish(GROUP_UPDATED_EVENT)


def add_rfc(
   session: Session, file_path: str, rfc_metadata: RFCMetadata
):
    load_single_file(session, file_path, rfc_metadata)
    EVENT_SYSTEM.publish(RFC_ADDED_EVENT)

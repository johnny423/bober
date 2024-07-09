from typing import List

import pytest

from bober.src.doc_parsing import parsing_utils

WORDS_AND_SPLITS = (
    (
        'The sun, shining brightly, cast warm rays across the tranquil, azure sea!',
        [
            'The',
            'sun',
            'shining',
            'brightly',
            'cast',
            'warm',
            'rays',
            'across',
            'the',
            'tranquil',
            'azure',
            'sea',
        ],
    ),
    (
        'Birds chirped ,melodiously! filling. the crisp',
        ['Birds', 'chirped', 'melodiously', 'filling', 'the', 'crisp'],
    ),
)


@pytest.mark.parametrize('input_line,split_line', WORDS_AND_SPLITS)
def test_split_line(input_line: str, split_line: List[str]) -> None:
    assert parsing_utils.split_line(input_line, ' ,.!') == split_line


def test_parse_by_word_position() -> None:
    full_text = '\n'.join([word for word, _ in WORDS_AND_SPLITS])
    expected_split_text = [split_word for _, split_word in WORDS_AND_SPLITS]
    assert (
        parsing_utils.parse_by_word_position(full_text) == expected_split_text
    )

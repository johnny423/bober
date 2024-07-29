from nltk import PorterStemmer
from pydantic import BaseModel

STEMMER = PorterStemmer()


class ParsedToken(BaseModel):
    word: str
    start: int

    @property
    def stem(self) -> str:
        return STEMMER.stem(self.word)

    @property
    def end(self) -> int:
        return self.start + len(self.word)


class ParsedLine(BaseModel):
    text: str
    indentation: int
    tokens: list[ParsedToken]


class ParsedSection(BaseModel):
    page: int
    page_line: int
    lines: dict[int, ParsedLine]


class ParsedDocument(BaseModel):
    sections: list[ParsedSection]

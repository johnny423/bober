from datetime import datetime

from pydantic import BaseModel

from bober.src.rfc_content import rebuild_content


class SearchRFCQuery(BaseModel):
    authors: list[str] | None = None
    date_range: tuple[datetime, datetime] | None = None
    title: str | None = None
    tokens: list[str] | None = None


class RFCMeta(BaseModel):
    num: int
    title: str
    published_at: datetime
    authors: list[str]


class RFCSection(BaseModel):
    content: str
    row_start: int
    row_end: int
    indentation: int


class RFC(RFCMeta):
    sections: list[RFCSection]

    @property
    def content(self) -> str:
        return rebuild_content(self.sections)

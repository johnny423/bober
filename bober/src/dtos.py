from datetime import datetime

from pydantic import BaseModel

from bober.src.rfc_content import rebuild_content, RFCSection


class RFCMeta(BaseModel):
    num: int
    title: str
    published_at: datetime
    authors: list[str]


class RFC(RFCMeta):
    sections: list[RFCSection]

    @property
    def content(self) -> str:
        return rebuild_content(self.sections)

import tkinter as tk

from sqlalchemy.orm import Session

from bober.src.fe.windows.utils import (
    create_scroll_region,
)
from bober.src.search.rfc_content import fetch_rfc_sections, rebuild_content


# todo: support scroll to specific section
class RFCWindow(tk.Toplevel):
    def __init__(self, parent, session: Session, rfc, token=None):
        super().__init__(parent)
        self.session = session
        self.title("")

        # Make this window modal
        self.grab_set()
        self.transient(parent)

        sections = fetch_rfc_sections(self.session, rfc)
        content = rebuild_content(
            sections,
        )

        # todo: improve highlights
        create_scroll_region(self, content, [token] if token else None)

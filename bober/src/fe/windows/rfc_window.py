import tkinter as tk

from sqlalchemy.orm import Session

from bober.src.fe.windows.utils import (
    create_scroll_region,
)
from bober.src.search.rfc_content import load_rfc_content


# todo: support scroll to specific section
class RFCWindow(tk.Toplevel):
    def __init__(self, parent, session: Session, rfc, token=None):
        super().__init__(parent)
        self.session = session
        self.title("")

        # Make this window modal
        self.grab_set()
        self.transient(parent)

        content = load_rfc_content(self.session, rfc)
        # todo: improve highlights
        create_scroll_region(self, content, [token] if token else None)

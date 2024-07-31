from sqlalchemy.orm import Session

from bober.src.fe.base_window import BaseWindow
from bober.src.fe.windows.utils import (
    create_scroll_region,
)
from bober.src.search.rfc_content import load_rfc_content, get_absolute_position


# todo: looks bad currently
# todo: support scroll to specific section
class RFCWindow(BaseWindow):
    def __init__(self, parent, session: Session, rfc, token=None):
        super().__init__(parent, "File", session)  # todo: rename to actual file name
        content = load_rfc_content(self.session, rfc)

        highlights = None
        if token:
            highlights = get_absolute_position(session, rfc, token)

        create_scroll_region(self, content, highlights)

from sqlalchemy.orm import Session

from bober.src.fe.base_window import BaseWindow
from bober.src.fe.scroll_page import create_scroll_region

from bober.src.search.rfc_content import load_rfc_content, get_absolute_positions, get_absolute_line


# todo: looks bad currently
# todo: support scroll to specific section
class RFCWindow(BaseWindow):
    def __init__(
            self,
            parent,
            session: Session,
            rfc: int,
            token: None | str = None,
            line_id: None | int = None,
    ):
        super().__init__(parent, "File", session)  # todo: rename to actual file name
        content = load_rfc_content(self.session, rfc)

        highlights = None
        if token:
            highlights = get_absolute_positions(session, rfc, token)

        page = create_scroll_region(self, content, highlights)
        if line_id:
            line = get_absolute_line(session, rfc, line_id)
            page.scroll_to_line(line)

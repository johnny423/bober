from sqlalchemy.orm import Session

from bober.src.fe.base_window import BaseWindow
from bober.src.fe.scroll_page import create_scroll_region
from bober.src.search.rfc_content import (
    get_absolute_line,
    get_absolute_positions,
    load_rfc_content,
)
from bober.src.search.search_rfc import SearchRFCQuery, search_rfcs


class RFCWindow(BaseWindow):
    def __init__(
            self,
            parent,
            session: Session,
            rfc: int,
            token: None | str = None,
            line_id: None | int = None,
    ):
        [meta] = search_rfcs(session, SearchRFCQuery(num=rfc))

        super().__init__(parent, meta.title or "<nameless rfc>", session)
        content = load_rfc_content(self.session, rfc)

        highlights = None
        if token:
            highlights = get_absolute_positions(session, rfc, token)

        page = create_scroll_region(self.main_frame, content, highlights)
        if line_id:
            line = get_absolute_line(session, rfc, line_id)
            page.scroll_to_line(line)

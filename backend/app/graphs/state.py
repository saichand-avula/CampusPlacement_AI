from graphs.schemas import EOIFields
from typing import TypedDict
class mystate(TypedDict):
    thread_id: str
    deadline: str
    jd_path: str
    jd_text: str
    raw_links: list[str]
    eoi_fields: EOIFields

from graphs.schemas import EOIFields
from typing import TypedDict


class mystate(TypedDict):
    user_id: str
    thread_id: str
    deadline: str
    jd_path: str
    jd_text: str
    raw_links: list[str]
    eoi_fields: EOIFields
    form_template_name: str
    additional_form_requirements: str
    form_fields: dict[str, str]
    form_link:str
    form_sheet_link:str
    form_drive_link:str
    
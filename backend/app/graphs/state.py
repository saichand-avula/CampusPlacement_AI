from graphs.schemas import EOIFields
from typing import TypedDict, Optional


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
    form_fields: list          # list of FormField dicts: {label, field_type, required, options}
    form_link: str
    form_sheet_link: str
    form_drive_link: str

    # User-provided overrides (from assistant state initial_* fields)
    # These take priority over JD-extracted values in eoi_fields.
    preset_company_name: Optional[str]
    preset_job_title: Optional[list[str]]
    preset_employment_type: Optional[str]
    preset_work_location: Optional[str]
    preset_stipend: Optional[str]
    preset_ctc: Optional[str]
    preset_duration: Optional[str]
    preset_eligibility: Optional[str]
    preset_branches: Optional[str]
    preset_company_website: Optional[str]
    preset_linkedin_link: Optional[str]
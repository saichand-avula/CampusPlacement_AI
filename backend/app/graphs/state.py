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

    # ── User-provided overrides (from assistant state initial_* fields) ─────────
    # These take priority over JD-extracted values in eoi_fields.
    # Fields marked "extractor-only" (job_description, about_company) have no preset.

    # Company info
    preset_company_name: Optional[str]
    preset_company_website: Optional[str]
    preset_linkedin_url: Optional[str]
    preset_address: Optional[str]

    # Job details
    preset_job_designation: Optional[list[str]]
    preset_employment_type: Optional[str]
    preset_work_location: Optional[str]

    # Eligibility (3 sub-fields)
    preset_eligibility_cgpa: Optional[str]
    preset_eligibility_backlogs: Optional[str]
    preset_eligibility_other: Optional[str]

    # Branches
    preset_applicable_branches: Optional[str]

    # Compensation
    preset_stipend: Optional[str]
    preset_ctc: Optional[str]

    # Process / Benefits (strict — only set if explicitly mentioned)
    preset_selection_process: Optional[list[str]]
    preset_bond: Optional[str]
    preset_slp_duration: Optional[str]
    preset_other_benefits: Optional[str]

    # Assignment
    preset_assignment_required: Optional[bool]
    preset_assignment_link: Optional[str]
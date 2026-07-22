from pydantic import BaseModel, Field
from typing import Optional, Literal


class EOIFields(BaseModel):
    # ── Company Info ────────────────────────────────────────────
    company_name: str = Field(
        description="Name of the hiring company."
    )

    company_website: Optional[str] = Field(
        default=None,
        description="Official company website URL."
    )

    linkedin_url: Optional[str] = Field(
        default=None,
        description="Official LinkedIn page URL of the company."
    )

    address: Optional[str] = Field(
        default=None,
        description="Physical address or office location of the company."
    )

    # ── Job Details ─────────────────────────────────────────────
    work_location: Optional[str] = Field(
        default=None,
        description="Primary work location (e.g. Bangalore, Remote, Hybrid)."
    )

    job_designation: list[str] = Field(
        description="List of all job roles/designations offered by the company."
    )

    employment_type: Optional[Literal["Internship", "FTE", "SLP + FTE"]] = Field(
        default=None,
        description=(
            "Type of employment. Must be exactly one of: "
            "'Internship' (SLP / internship only), "
            "'FTE' (full-time only), or "
            "'SLP + FTE' (internship with full-time conversion / PPO)."
        )
    )

    # ── Eligibility ─────────────────────────────────────────────
    eligibility_cgpa: Optional[str] = Field(
        default=None,
        description=(
            "Minimum CGPA requirement. Return 'N/A' if not mentioned in the JD. "
            "Do NOT guess or assume a value."
        )
    )

    eligibility_backlogs: Optional[str] = Field(
        default=None,
        description=(
            "Backlog policy (e.g. 'No active backlogs allowed', 'Maximum 1 backlog'). "
            "Return 'N/A' if not mentioned in the JD. Do NOT guess or assume a value."
        )
    )

    eligibility_other: Optional[str] = Field(
        default=None,
        description=(
            "Any other eligibility criteria not covered by CGPA or backlogs "
            "(e.g. specific skills, certifications, graduation year). "
            "Return 'N/A' if not mentioned in the JD. Do NOT guess or assume a value."
        )
    )

    # ── Applicable Branches ─────────────────────────────────────
    applicable_branches: Optional[str] = Field(
        default=None,
        description=(
            "Eligible branches. ONLY map to valid combinations of: CSE, ECE, AIDS. "
            "Valid values: 'CSE', 'ECE', 'AIDS', 'CSE + ECE', 'CSE + AIDS', "
            "'ECE + AIDS', 'CSE + ECE + AIDS'. "
            "Return null if no branches are mentioned or if none match these three."
        )
    )

    # ── Compensation ─────────────────────────────────────────────
    stipend: Optional[str] = Field(
        default=None,
        description="Monthly stipend or internship compensation (can be text or number)."
    )

    ctc: Optional[str] = Field(
        default=None,
        description="Full-time CTC or PPO compensation details (can be text or number)."
    )

    # ── Descriptions (extractor-only, not settable by assistant) ─
    job_description: Optional[str] = Field(
        default=None,
        description="Brief summary of the job responsibilities and role overview."
    )

    about_company: Optional[str] = Field(
        default=None,
        description=(
            "Brief description of the company — what they do, their domain, "
            "scale, or any notable facts mentioned in the JD."
        )
    )

    # ── Process ──────────────────────────────────────────────────
    selection_process: Optional[list[str]] = Field(
        default=None,
        description=(
            "Ordered list of selection rounds (e.g. ['Online Test', 'Technical Interview', 'HR Round']). "
            "Only populate if explicitly listed in the JD. Do NOT assume or guess."
        )
    )

    bond: Optional[str] = Field(
        default=None,
        description=(
            "Any bond or service agreement clause mentioned (e.g. '2-year bond', 'training bond of 6 months'). "
            "Only populate if explicitly mentioned. Do NOT assume."
        )
    )

    slp_duration: Optional[str] = Field(
        default=None,
        description=(
            "Internship or SLP duration (e.g. '6 months', '2 months'). "
            "Only populate if explicitly mentioned. Do NOT assume."
        )
    )

    other_benefits: Optional[str] = Field(
        default=None,
        description=(
            "Additional perks or benefits explicitly mentioned "
            "(e.g. Early PPO opportunity, ESOPs, relocation bonus, meal coupons, insurance, accommodation). "
            "Only populate if explicitly mentioned. Do NOT assume or infer."
        )
    )

    # ── Assignment ───────────────────────────────────────────────
    assignment_required: bool = Field(
        default=False,
        description=(
            "True only if an assignment, assessment, coding test, or task is explicitly "
            "mentioned as part of the hiring process."
        )
    )

    assignment_deadline: Optional[str] = Field(
        default=None,
        description=(
            "Deadline for the assignment submission. "
            "This is always set to the form/application deadline — do NOT extract separately."
        )
    )

    assignment_link: Optional[str] = Field(
        default=None,
        description="Assignment or assessment submission URL if provided in the JD."
    )


class FormFieldItem(BaseModel):
    """A single Google Form field, matching the template store format."""
    label: str = Field(description="Question shown on the Google Form.")
    field_type: str = Field(
        description=(
            "Google Form question type. Must be one of: "
            "short_text, paragraph, email, number, phone, date, "
            "dropdown, multiple_choice, checkboxes."
        )
    )
    required: bool = Field(description="Whether answering this question is mandatory.")
    options: list[str] = Field(
        default_factory=list,
        description="Options for dropdown, multiple_choice, or checkboxes fields.",
    )


class FormFields(BaseModel):
    fields: list[FormFieldItem] = Field(
        description="Complete list of Google Form fields (existing + any new ones added)."
    )
from pydantic import BaseModel, Field
from typing import Optional


class EOIFields(BaseModel):
    company_name: str = Field(
        description="Name of the hiring company."
    )

    company_website: Optional[str] = Field(
        default=None,
        description="Official company website URL."
    )

    linkedin_link: Optional[str] = Field(
        default=None,
        description="Official LinkedIn page URL of the company."
    )

    job_title: list[str] = Field(
        description="List of all job roles/designations offered by the company."
    )

    employment_type: Optional[str] = Field(
        default=None,
        description="Type of employment. Extract exactly one of: 'Internship', 'FTE', or 'SLP + FTE'."
    )

    work_location: Optional[str] = Field(
        default=None,
        description="Primary work location."
    )

    stipend: Optional[str] = Field(
        default=None,
        description="Monthly stipend or internship compensation."
    )

    ctc: Optional[str] = Field(
        default=None,
        description="Full-time CTC or PPO compensation details."
    )

    duration: Optional[str] = Field(
        default=None,
        description="Internship or employment duration."
    )

    eligibility: Optional[str] = Field(
        default=None,
        description="Eligibility criteria including CGPA, backlogs, academic requirements, etc."
    )

    branches: Optional[str] = Field(
        default=None,
        description="Applicable branches or departments."
    )

    job_description: Optional[str] = Field(
        default=None,
        description="Brief summary of the job responsibilities."
    )

    selection_process: Optional[list[str]] = Field(
        default=None,
        description="Ordered list of selection rounds."
    )

    other_benefits: Optional[str] = Field(
        default=None,
        description="Additional benefits such as relocation bonus, joining bonus, travel allowance, accommodation, insurance, ESOPs, meal coupons, etc."
    )

    assignment_required: bool = Field(
        default=False,
        description="Whether an assignment is required as part of the hiring process."
    )

    assignment_link: Optional[str] = Field(
        default=None,
        description="Assignment or assessment submission link if provided."
    )


class FormFields(BaseModel):
    fields: dict[str, str] = Field(
        description="Final Google Form fields mapped to their types."
    )
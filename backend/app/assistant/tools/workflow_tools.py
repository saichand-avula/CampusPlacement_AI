from typing import Annotated, Optional

from langchain_core.messages import ToolMessage
from langchain_core.tools import tool, InjectedToolCallId
from langgraph.prebuilt import InjectedState
from langgraph.types import Command

from assistant.assistant_state import AssistantState


# ──────────────────────────────────────────────
# Tool: check_workflow_status
# ──────────────────────────────────────────────

@tool
async def check_workflow_status(
    state: Annotated[AssistantState, InjectedState],
) -> str:
    """
    Checks whether the placement workflow has been initialized and
    returns a summary of all current placement state values collected
    so far (company, deadline, template, job details, etc.).

    Call this when:
    - The user asks whether the workflow is initialized.
    - The user asks what values are currently set.
    - You need to verify it is safe to update state.
    """
    initialized = state.get("workflow_initialized", False)

    lines = [
        f"Workflow Initialized: {'YES' if initialized else 'NO'}",
        "",
        "Current State Values:",
    ]

    fields = {
        "Company Name":               state.get("initial_company_name"),
        "Deadline":                   state.get("initial_deadline"),
        "JD Path":                    state.get("initial_jd_path"),
        "Form Template":              state.get("initial_form_template_name"),
        "Additional Form Reqs":       state.get("initial_additional_form_requirements"),
        "Company Website":            state.get("initial_company_website"),
        "LinkedIn":                   state.get("initial_linkedin_link"),
        "Job Title(s)":               state.get("initial_job_title"),
        "Employment Type":            state.get("initial_employment_type"),
        "Work Location":              state.get("initial_work_location"),
        "Stipend":                    state.get("initial_stipend"),
        "CTC":                        state.get("initial_ctc"),
        "Duration":                   state.get("initial_duration"),
        "Eligibility":                state.get("initial_eligibility"),
        "Branches":                   state.get("initial_branches"),
    }

    for label, value in fields.items():
        display = value if value not in (None, "", [], {}) else "Not set"
        lines.append(f"  {label}: {display}")

    return "\n".join(lines)


# ──────────────────────────────────────────────
# Tool: update_assistant_state
# ──────────────────────────────────────────────

@tool
async def update_assistant_state(
    tool_call_id: Annotated[str, InjectedToolCallId],
    state: Annotated[AssistantState, InjectedState],
    company_name: Optional[str] = None,
    deadline: Optional[str] = None,
    jd_path: Optional[str] = None,
    form_template_name: Optional[str] = None,
    additional_form_requirements: Optional[str] = None,
    company_website: Optional[str] = None,
    linkedin_link: Optional[str] = None,
    job_title: Optional[list[str]] = None,
    employment_type: Optional[str] = None,
    work_location: Optional[str] = None,
    stipend: Optional[str] = None,
    ctc: Optional[str] = None,
    duration: Optional[str] = None,
    eligibility: Optional[str] = None,
    branches: Optional[str] = None,
) -> Command:
    """
    Updates one or more placement workflow state values.
    Only works when the workflow has NOT been initialized yet.

    Use this whenever the user provides or corrects placement details
    such as company name, deadline, form template, job info, etc.

    Do NOT call this if the workflow is already initialized — instead,
    inform the user that changes after initialization need different handling.

    Args:
        company_name: Name of the hiring company (e.g. "Amazon").
        deadline: Form/application deadline (e.g. "12 Nov 2025 12:00 PM").
        jd_path: File path to the job description document.
        form_template_name: Google Form template name (e.g. "basic template").
        additional_form_requirements: Extra form field requirements.
        company_website: Company's official website URL.
        linkedin_link: LinkedIn job post or company page URL.
        job_title: List of job roles (e.g. ["SDE", "Data Analyst"]).
        employment_type: e.g. "Full-Time", "Internship".
        work_location: e.g. "Remote", "Bangalore", "Hybrid".
        stipend: Monthly stipend amount (for internships).
        ctc: Annual CTC package (for full-time roles).
        duration: Internship / contract duration.
        eligibility: Eligibility criteria.
        branches: Eligible branches or departments.
    """
    initialized = state.get("workflow_initialized", False)

    if initialized:
        return Command(
            update={
                "messages": [
                    ToolMessage(
                        content=(
                            "Cannot update: workflow is already initialized. "
                            "Changes after initialization must be handled separately."
                        ),
                        tool_call_id=tool_call_id,
                    )
                ]
            }
        )

    updates: dict = {}
    updated_fields: list[str] = []

    if company_name is not None:
        updates["initial_company_name"] = company_name
        updated_fields.append(f"Company Name → {company_name}")

    if deadline is not None:
        updates["initial_deadline"] = deadline
        updated_fields.append(f"Deadline → {deadline}")

    if jd_path is not None:
        updates["initial_jd_path"] = jd_path
        updated_fields.append(f"JD Path → {jd_path}")

    if form_template_name is not None:
        updates["initial_form_template_name"] = form_template_name
        updated_fields.append(f"Form Template → {form_template_name}")

    if additional_form_requirements is not None:
        updates["initial_additional_form_requirements"] = additional_form_requirements
        updated_fields.append(f"Additional Form Reqs → {additional_form_requirements}")

    if company_website is not None:
        updates["initial_company_website"] = company_website
        updated_fields.append(f"Company Website → {company_website}")

    if linkedin_link is not None:
        updates["initial_linkedin_link"] = linkedin_link
        updated_fields.append(f"LinkedIn → {linkedin_link}")

    if job_title is not None:
        updates["initial_job_title"] = job_title
        updated_fields.append(f"Job Title(s) → {', '.join(job_title)}")

    if employment_type is not None:
        updates["initial_employment_type"] = employment_type
        updated_fields.append(f"Employment Type → {employment_type}")

    if work_location is not None:
        updates["initial_work_location"] = work_location
        updated_fields.append(f"Work Location → {work_location}")

    if stipend is not None:
        updates["initial_stipend"] = stipend
        updated_fields.append(f"Stipend → {stipend}")

    if ctc is not None:
        updates["initial_ctc"] = ctc
        updated_fields.append(f"CTC → {ctc}")

    if duration is not None:
        updates["initial_duration"] = duration
        updated_fields.append(f"Duration → {duration}")

    if eligibility is not None:
        updates["initial_eligibility"] = eligibility
        updated_fields.append(f"Eligibility → {eligibility}")

    if branches is not None:
        updates["initial_branches"] = branches
        updated_fields.append(f"Branches → {branches}")

    if not updates:
        return Command(
            update={
                "messages": [
                    ToolMessage(
                        content="No fields were provided to update.",
                        tool_call_id=tool_call_id,
                    )
                ]
            }
        )

    summary_lines = ["Updated successfully:"]
    summary_lines.extend(f"  {f}" for f in updated_fields)
    summary = "\n".join(summary_lines)

    return Command(
        update={
            **updates,
            "messages": [
                ToolMessage(
                    content=summary,
                    tool_call_id=tool_call_id,
                )
            ],
        }
    )

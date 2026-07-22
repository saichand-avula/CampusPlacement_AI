from typing import Annotated, Optional
from typing_extensions import TypedDict, NotRequired
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage


class AssistantState(TypedDict):
    # Conversation metadata
    thread_id: NotRequired[str]
    summary: NotRequired[str]

    # Indicates whether the placement workflow has been initialized
    # Only becomes True when the workflow graph is explicitly started.
    workflow_initialized: NotRequired[bool]

    # Complete conversation history
    messages: Annotated[list[BaseMessage], add_messages]

    # Initial workflow inputs collected from the user before workflow execution
    initial_company_name: NotRequired[str | None]
    initial_deadline: NotRequired[str | None]
    initial_jd_path: NotRequired[str | None]

    # Form configuration provided by the user
    initial_form_template_name: NotRequired[str | None]
    initial_additional_form_requirements: NotRequired[str | None]

    # ── Company details ────────────────────────────────────────
    initial_company_website: NotRequired[str | None]
    initial_linkedin_url: NotRequired[str | None]
    initial_address: NotRequired[str | None]

    # ── Job details ────────────────────────────────────────────
    initial_job_designation: NotRequired[list[str] | None]
    initial_employment_type: NotRequired[str | None]
    initial_work_location: NotRequired[str | None]

    # ── Eligibility (3 sub-fields) ─────────────────────────────
    initial_eligibility_cgpa: NotRequired[str | None]
    initial_eligibility_backlogs: NotRequired[str | None]
    initial_eligibility_other: NotRequired[str | None]

    # ── Branches ──────────────────────────────────────────────
    initial_applicable_branches: NotRequired[str | None]

    # ── Compensation ──────────────────────────────────────────
    initial_stipend: NotRequired[str | None]
    initial_ctc: NotRequired[str | None]

    # ── Process / Benefits (strict — only if explicitly mentioned) ──
    initial_selection_process: NotRequired[list[str] | None]
    initial_bond: NotRequired[str | None]
    initial_slp_duration: NotRequired[str | None]
    initial_other_benefits: NotRequired[str | None]

    # ── Assignment ─────────────────────────────────────────────
    initial_assignment_required: NotRequired[bool | None]
    initial_assignment_link: NotRequired[str | None]
    # NOTE: initial_assignment_deadline is NOT stored — it always equals initial_deadline
from typing import Annotated
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

    # Optional company details provided or corrected by the user
    initial_company_website: NotRequired[str | None]
    initial_linkedin_link: NotRequired[str | None]

    # Optional job details used to initialize the workflow
    initial_job_title: NotRequired[list[str] | None]
    initial_employment_type: NotRequired[str | None]
    initial_work_location: NotRequired[str | None]
    initial_stipend: NotRequired[str | None]
    initial_ctc: NotRequired[str | None]
    initial_duration: NotRequired[str | None]
    initial_eligibility: NotRequired[str | None]
    initial_branches: NotRequired[str | None]
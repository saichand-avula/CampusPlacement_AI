from typing import Annotated, Optional

from langchain_core.messages import ToolMessage
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool, InjectedToolCallId
from langgraph.prebuilt import InjectedState, InjectedStore
from langgraph.store.base import BaseStore
from langgraph.types import Command

from assistant.assistant_state import AssistantState
from graphs.graph import get_graph


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


# ──────────────────────────────────────────────
# Tool: initialize_workflow
# ──────────────────────────────────────────────

@tool
async def initialize_workflow(
    tool_call_id: Annotated[str, InjectedToolCallId],
    state: Annotated[AssistantState, InjectedState],
    store: Annotated[BaseStore, InjectedStore],
    config: RunnableConfig,
) -> Command:
    """
    Initializes the placement workflow by mapping the current assistant
    state into the workflow graph and running it.

    Before initializing:
      1. Checks that a JD has been uploaded (initial_jd_path must be set).
         If not, returns a signal so the frontend can show the upload popup.
      2. Resolves the form template:
         a. Uses initial_form_template_name if already set.
         b. Falls back to long-term memory (category "template_preference").
         c. If neither exists, asks the user to create/choose a template.
      3. Verifies the resolved template exists for this user in the store.
         If the name is given by user but not found, asks user to create it first.
      4. Maps all initial_* fields from AssistantState → mystate.
      5. Invokes the workflow graph using the same thread_id as the assistant.
      6. Sets workflow_initialized = True.

    Call this when the user says "start workflow", "initialize workflow",
    "create workflow", "run the placement drive", or similar.
    """
    # ── Guard: already initialized ────────────────────────────
    if state.get("workflow_initialized", False):
        return Command(
            update={
                "messages": [
                    ToolMessage(
                        content="Workflow is already initialized. No action taken.",
                        tool_call_id=tool_call_id,
                    )
                ]
            }
        )

    # ── Hardcoded user_id (same as rest of the system) ────────
    user_id = "1"
    # Read thread_id from the LangGraph config (it's NEVER in state values)
    thread_id = config["configurable"].get("thread_id", "")

    # ── Gate 1: JD must be uploaded ───────────────────────────
    jd_path = state.get("initial_jd_path")
    if not jd_path:
        return Command(
            update={
                "messages": [
                    ToolMessage(
                        content=(
                            '{"requires": "jd_upload", '
                            '"message": "A Job Description (JD) file is required before '
                            'the workflow can be initialized. Please upload the JD PDF."}'
                        ),
                        tool_call_id=tool_call_id,
                    )
                ]
            }
        )

    # ── Gate 2: Resolve form template ─────────────────────────
    template_name = state.get("initial_form_template_name")

    # 2a. If not in state, look in long-term memory
    if not template_name:
        memory_items = await store.asearch(
            (user_id, "longterm_memory"),
            query="template preference",
        )
        for item in memory_items:
            if item.value.get("category") == "template_preference":
                template_name = item.value.get("content", "").strip()
                break

    # 2b. If still none → use hardcoded default "basic template"
    #     (The system profile always sets this as the default for the user.)
    if not template_name:
        template_name = "basic template"

    # 2c. Verify the template exists for this user in the store
    existing_templates = await store.asearch((user_id, "templates"))
    template_names = [item.key for item in existing_templates]

    if template_name not in template_names:
        # Template name is set but not yet created → ask user to create it
        return Command(
            update={
                "messages": [
                    ToolMessage(
                        content=(
                            '{"requires": "template", '
                            f'"message": "Template \'{template_name}\' has not been created yet. '
                            'Please create it first by telling me what fields you want in the form."}'
                        ),
                        tool_call_id=tool_call_id,
                    )
                ]
            }
        )

    # ── Build workflow input (AssistantState → mystate) ───────
    # Core fields
    workflow_input: dict = {
        "user_id": user_id,
        "thread_id": thread_id,
        "jd_path": jd_path,
        "deadline": state.get("initial_deadline") or "",
        "form_template_name": template_name,
        "additional_form_requirements": state.get("initial_additional_form_requirements") or "",
        # Pass user-provided values as preset_* so EOI extractor respects them
        "preset_company_name": state.get("initial_company_name"),
        "preset_job_title": state.get("initial_job_title"),
        "preset_employment_type": state.get("initial_employment_type"),
        "preset_work_location": state.get("initial_work_location"),
        "preset_stipend": state.get("initial_stipend"),
        "preset_ctc": state.get("initial_ctc"),
        "preset_duration": state.get("initial_duration"),
        "preset_eligibility": state.get("initial_eligibility"),
        "preset_branches": state.get("initial_branches"),
        "preset_company_website": state.get("initial_company_website"),
        "preset_linkedin_link": state.get("initial_linkedin_link"),
    }

    # ── Run workflow graph ─────────────────────────────────────
    # Use a prefixed thread_id to avoid checkpointer conflicts
    # with the assistant graph which shares the same SQLite DB.
    wf_graph = get_graph()
    wf_config = {"configurable": {"thread_id": f"wf_{thread_id}"}}

    try:
        final_state: dict = await wf_graph.ainvoke(workflow_input, config=wf_config)
    except Exception as exc:
        return Command(
            update={
                "messages": [
                    ToolMessage(
                        content=f"Workflow failed to start: {str(exc)}",
                        tool_call_id=tool_call_id,
                    )
                ]
            }
        )

    # ── Serialize result and persist to store ─────────────────
    # ainvoke returns the final state dict. Serialize Pydantic
    # models so the store (which uses JSON) can hold them.
    serializable: dict = {}
    for k, v in final_state.items():
        if hasattr(v, "model_dump"):
            serializable[k] = v.model_dump()
        elif isinstance(v, list):
            serializable[k] = [
                item.model_dump() if hasattr(item, "model_dump") else item
                for item in v
            ]
        else:
            serializable[k] = v

    # Store result under (user_id, "workflow_results") keyed by thread_id
    await store.aput(
        (user_id, "workflow_results"),
        thread_id,
        serializable,
    )

    # ── Mark workflow as initialized in assistant state ────────
    return Command(
        update={
            "workflow_initialized": True,
            "initial_form_template_name": template_name,
            "messages": [
                ToolMessage(
                    content=(
                        '{"status": "workflow_started", '
                        f'"template": "{template_name}", '
                        f'"jd_path": "{jd_path}"}}'
                    ),
                    tool_call_id=tool_call_id,
                )
            ],
        }
    )

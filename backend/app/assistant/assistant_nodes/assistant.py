import json

from langchain_core.messages import BaseMessage, SystemMessage, AIMessage, ToolMessage

from assistant.assistant_state import AssistantState
from assistant.llm import llm
from assistant.prompts import (
    SYSTEM_PROMPT,
    SHORT_TERM_MEMORY_CONTEXT,
    USER_PROFILE_CONTEXT,
)
from assistant.tools.template_creator import create_template
from assistant.tools.template_retriver import fetchtemplates
from assistant.tools.workflow_tools import (
    check_workflow_status,
    update_assistant_state,
    initialize_workflow,
)


tools = [
    create_template,
    check_workflow_status,
    update_assistant_state,
    initialize_workflow,
    fetchtemplates,
]

assistant_llm = llm.bind_tools(tools)


# ──────────────────────────────────────────────
# Hardcoded responses for known tool signals
# The LLM must never be allowed to craft these
# responses freely — it always adds extra text.
# ──────────────────────────────────────────────

_FIXED_RESPONSES: dict[str, str] = {
    "jd_upload":        "Please upload the JD PDF using the upload button above.",
    "template":         "You have no saved templates. Please create one first.",
    "workflow_started": "Done! The workflow is running — check the panel on the right for results.",
}


def _check_fixed_response(messages: list[BaseMessage]) -> str | None:
    """
    Scan the last ToolMessage for a known JSON signal.
    Returns the hardcoded reply string if found, else None.
    """
    for msg in reversed(messages):
        if not isinstance(msg, ToolMessage):
            break
        try:
            data = json.loads(msg.content)
        except (json.JSONDecodeError, TypeError):
            continue

        if isinstance(data, dict):
            requires = data.get("requires")
            status   = data.get("status")

            if requires in _FIXED_RESPONSES:
                return _FIXED_RESPONSES[requires]
            if status in _FIXED_RESPONSES:
                return _FIXED_RESPONSES[status]

    return None


def _normalize_content(msg: BaseMessage) -> BaseMessage:
    """
    Sarvam AI (OpenAI-compatible) requires message content to be a plain
    string. LangGraph / Gemini sometimes stores content as a list of parts
    (e.g. [{"type": "text", "text": "..."}]) or as None after a tool call.
    This function coerces the content to a string so the API never rejects it.
    """
    content = msg.content

    if isinstance(content, str):
        return msg

    if content is None:
        normalized = ""
    elif isinstance(content, list):
        # Extract text parts; ignore image / tool-result parts
        text_parts = []
        for part in content:
            if isinstance(part, str):
                text_parts.append(part)
            elif isinstance(part, dict) and part.get("type") == "text":
                text_parts.append(part.get("text", ""))
        normalized = "".join(text_parts)
    else:
        normalized = str(content)

    # Return a shallow copy with corrected content
    # Use model_copy (Pydantic v2) with fallback to copy (Pydantic v1)
    try:
        return msg.model_copy(update={"content": normalized})
    except AttributeError:
        copied = msg.copy()
        object.__setattr__(copied, "content", normalized)
        return copied


async def assistant_node(state: AssistantState):

    # ── Programmatic intercept ──────────────────────────────────
    # If the last tool call returned a known JSON signal, bypass the
    # LLM entirely and return the exact hardcoded message.
    # This prevents the model from appending "company name / deadline"
    # or any other free-form text to these fixed responses.
    fixed = _check_fixed_response(state["messages"])
    if fixed:
        return {"messages": [AIMessage(content=fixed)]}
    # ────────────────────────────────────────────────────────────

    messages = [
        SystemMessage(content=SYSTEM_PROMPT)
    ]

    # -----------------------
    # Static User Profile
    # User 1 defaults: name=saichand, default template=basic template
    # -----------------------
    messages.append(
        SystemMessage(
            content=USER_PROFILE_CONTEXT
        )
    )

    # -----------------------
    # Short-Term Memory (conversation summary)
    # -----------------------
    if state.get("summary"):
        messages.append(
            SystemMessage(
                content=SHORT_TERM_MEMORY_CONTEXT.format(
                    summary=state["summary"]
                )
            )
        )

    # -----------------------
    # Recent Messages
    # Normalize content to strings — required by OpenAI-compatible APIs
    # (Sarvam AI rejects list/None content that Gemini silently accepted)
    # -----------------------
    messages.extend(
        _normalize_content(m) for m in state["messages"]
    )

    response = await assistant_llm.ainvoke(messages)

    return {
        "messages": [response]
    }
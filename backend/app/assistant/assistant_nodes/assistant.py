from langchain_core.messages import BaseMessage, SystemMessage
from langgraph.runtime import Runtime

from assistant.assistant_state import AssistantState
from assistant.llm import llm
from assistant.prompts import (
    SYSTEM_PROMPT,
    SHORT_TERM_MEMORY_CONTEXT,
    LONG_TERM_MEMORY_CONTEXT,
)
from assistant.tools.template_creator import create_template


tools = [
    create_template,
]

assistant_llm = llm.bind_tools(tools)


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
    msg = msg.copy()
    msg.content = normalized
    return msg


async def assistant_node(
    state: AssistantState,
    runtime: Runtime,
):

    messages = [
        SystemMessage(
            content=SYSTEM_PROMPT
        )
    ]

    # -----------------------
    # Long-Term Memory
    # -----------------------

    memories = await runtime.store.asearch(
        ("1", "longterm_memory")
    )

    if memories:

        memory_text = "\n".join(
            f"- {memory.value['content']}"
            for memory in memories
        )

        messages.append(
            SystemMessage(
                content=LONG_TERM_MEMORY_CONTEXT.format(
                    memories=memory_text
                )
            )
        )

    # -----------------------
    # Short-Term Memory
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
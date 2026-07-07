from langchain_core.messages import SystemMessage
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
    # -----------------------

    messages.extend(state["messages"])

    response = await assistant_llm.ainvoke(messages)

    return {
        "messages": [response]
    }
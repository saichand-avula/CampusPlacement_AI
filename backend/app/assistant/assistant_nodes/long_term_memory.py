from uuid import uuid4

from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.runtime import Runtime

from assistant.assistant_state import AssistantState
from assistant.llm import llm
from assistant.prompts import (
    LONG_TERM_MEMORY_PROMPT,
    MEMORY_DUPLICATE_PROMPT,
)
from assistant.schemas import MemoryList


memory_extractor = llm.with_structured_output(MemoryList)
duplicate_filter = llm.with_structured_output(MemoryList)


async def long_term_memory(
    state: AssistantState,
    runtime: Runtime,
):
    store = runtime.store

    # ----------------------------
    # Get latest user message
    # ----------------------------
    latest_user_message = None

    for message in reversed(state["messages"]):
        if getattr(message, "type", "") == "human":
            latest_user_message = message.content
            break

    if latest_user_message is None:
        return {}

    # ----------------------------
    # Extract candidate memories
    # ----------------------------
    extracted = await memory_extractor.ainvoke(
        [
            SystemMessage(
                content=LONG_TERM_MEMORY_PROMPT
            ),
            HumanMessage(
                content=latest_user_message
            ),
        ]
    )

    if not extracted.memories:
        return {}

    # ----------------------------
    # Fetch existing memories
    # ----------------------------
    existing_items = await store.asearch(
        ("1", "longterm_memory")
    )

    existing_memories = [
        item.value["content"]
        for item in existing_items
    ]

    # ----------------------------
    # Remove duplicates
    # ----------------------------
    filtered = await duplicate_filter.ainvoke(
        [
            SystemMessage(
                content=MEMORY_DUPLICATE_PROMPT
            ),
            HumanMessage(
                content=f"""
Existing Memories:

{existing_memories}

Candidate Memories:

{[memory.model_dump() for memory in extracted.memories]}
"""
            ),
        ]
    )

    if not filtered.memories:
        return {}

    # ----------------------------
    # Save new memories
    # ----------------------------
    for memory in filtered.memories:

        await store.aput(
            ("1", "longterm_memory"),
            str(uuid4()),
            {
                "content": memory.content,
                "category": memory.category,
            },
        )

    return {}
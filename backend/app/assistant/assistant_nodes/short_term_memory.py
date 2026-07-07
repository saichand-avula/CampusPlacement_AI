from langchain_core.messages import HumanMessage, SystemMessage

from assistant.llm import llm
from assistant.prompts import SUMMARY_PROMPT
from assistant.assistant_state import AssistantState


async def short_term_memory(state: AssistantState):

    messages = state["messages"]

    if len(messages) <= 13:
        return {}

    old_messages = messages[:-6]
    recent_messages = messages[-6:]

    summary = state.get("summary", "").strip()

    prompt = [
        SystemMessage(content=SUMMARY_PROMPT),
        HumanMessage(
            content=f"""
Existing Summary:
{summary if summary else "No previous summary."}

New Messages:
{old_messages}

Update the summary.

Requirements:
- Merge the previous summary with the new conversation.
- Preserve important user preferences, decisions and ongoing context.
- Do not include greetings or small talk.
- Keep the summary concise (around 200-300 words maximum).
- The summary should be sufficient to continue the conversation later.
"""
        ),
    ]

    response = await llm.ainvoke(prompt)

    return {
        "summary": response.content,
        "messages": recent_messages,
    }
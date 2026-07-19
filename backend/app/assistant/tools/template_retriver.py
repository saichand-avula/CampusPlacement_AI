from typing import Annotated
from langchain_core.tools import tool
from langgraph.prebuilt import InjectedStore
from langgraph.store.base import BaseStore

# Hardcoded user_id — the whole system currently operates as user "1"
_USER_ID = "1"

@tool
async def fetchtemplates(store: Annotated[BaseStore, InjectedStore]) -> str:
    """
    Use this tool if user asks about templates.
    """
    items = await store.asearch((_USER_ID, "templates"))

    if not items:
        return "No templates found."

    lines = ["These are our templates and fields:"]

    for index, item in enumerate(items, start=1):
        fields = item.value.get("fields", [])
        field_lines = []

        for field in fields:
            label = field.get("label", "Unnamed field")
            field_type = field.get("field_type", "unknown")
            required = "required" if field.get("required") else "optional"
            options = field.get("options", [])

            text = f"{label} ({field_type}, {required})"
            if options:
                text += f" options: {', '.join(options)}"
            field_lines.append(f"- {text}")

        lines.append(f"{index}. {item.key}")
        lines.extend(f"   {line}" for line in field_lines or ["   - No fields saved."])

    return "\n".join(lines)
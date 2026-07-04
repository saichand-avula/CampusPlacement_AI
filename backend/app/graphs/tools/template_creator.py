from langchain_core.tools import tool
from langgraph.store.base import BaseStore
from typing import Dict


@tool
async def create_template(
    user_id: str,
    template_name: str,
    fields: Dict[str, str],
    store: BaseStore,
) -> str:
    """
    Creates or updates a Google Form template in the long-term store.

    Args:
        user_id: Owner of the template.
        template_name: Name of the template.
        fields: Dictionary mapping field names to their types.
                Example:
                {
                    "Name": "string",
                    "Email": "email",
                    "Phone Number": "string",
                    "CGPA": "float"
                }
        store: LangGraph store.

    Returns:
        Success message.
    """

    namespace = (
        user_id,
        "templates",
    )

    await store.aput(
        namespace,
        template_name,
        {
            "fields": fields
        },
    )

    return f"Template '{template_name}' saved successfully."
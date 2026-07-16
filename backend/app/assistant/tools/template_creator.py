from typing import Annotated, Literal

from pydantic import BaseModel, Field
from langchain_core.tools import tool
from langgraph.prebuilt import InjectedStore
from langgraph.store.base import BaseStore

# Hardcoded user_id — the whole system currently operates as user "1"
_USER_ID = "1"


class FormField(BaseModel):
    label: str = Field(
        description="Question shown on the Google Form."
    )

    field_type: Literal[
        "short_text",
        "paragraph",
        "email",
        "number",
        "phone",
        "date",
        "dropdown",
        "multiple_choice",
        "checkboxes",
    ] = Field(
        description="Google Form question type."
    )

    required: bool = Field(
        description="Whether answering this question is mandatory."
    )

    options: list[str] = Field(
        default_factory=list,
        description="Options for dropdown, multiple choice or checkboxes.",
    )


@tool
async def create_template(
    template_name: str,
    fields: list[FormField],
    store: Annotated[BaseStore, InjectedStore],
) -> str:
    """
    Creates or updates a reusable Google Form template for the current user.

    Args:
        template_name: Name of the template (e.g. "basic template").
        fields: List of Google Form fields to include.
    """

    namespace = (_USER_ID, "templates")

    await store.aput(
        namespace,
        template_name,
        {
            "fields": [
                field.model_dump()
                for field in fields
            ]
        },
    )

    return f"Template '{template_name}' saved successfully under user {_USER_ID}."
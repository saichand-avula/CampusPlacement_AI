from typing import Annotated, Literal

from pydantic import BaseModel, Field
from langchain_core.tools import tool
from langgraph.prebuilt import InjectedStore
from langgraph.store.base import BaseStore


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
        description="Options for dropdown, multiple choice or checkboxes."
    )


@tool
async def create_template(
    user_id: str,
    template_name: str,
    fields: list[FormField],
    store: Annotated[BaseStore, InjectedStore],
) -> str:
    """
    Creates or updates a reusable Google Form template.

    Args:
        user_id: Owner of the template.
        template_name: Template name.
        fields: Google Form fields.
    """

    namespace = (
        user_id,
        "templates",
    )

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

    return (
        f"Template '{template_name}' "
        "saved successfully."
    )
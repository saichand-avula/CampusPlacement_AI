from typing import Annotated, Literal, Optional

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
    replace: Optional[bool] = False,
) -> str:
    """
    Creates or updates a reusable Google Form template for the current user.

    IMPORTANT: By default (replace=False) this MERGES the given fields with
    any existing fields already saved under this template name — existing fields
    are preserved and new fields are appended. Only set replace=True when the
    user explicitly asks to completely replace/recreate the template from scratch.

    Use this tool ONLY when the user wants to permanently create or update a
    named template. Do NOT use this to add temporary extra fields for a single
    workflow run — use update_assistant_state(additional_form_requirements=...)
    for that instead.

    Args:
        template_name: Name of the template (e.g. "custom template").
        fields: List of Google Form fields to add/include.
        replace: If True, replaces the template entirely. If False (default),
                 merges new fields with existing ones (existing fields kept).
    """

    namespace = (_USER_ID, "templates")

    new_fields = [field.model_dump() for field in fields]

    if not replace:
        # Fetch existing template and merge — never silently wipe existing fields
        existing_item = await store.aget(namespace, template_name)
        if existing_item is not None:
            existing_fields: list[dict] = existing_item.value.get("fields", [])
            # Avoid duplicate labels (case-insensitive check)
            existing_labels = {f["label"].lower() for f in existing_fields}
            for nf in new_fields:
                if nf["label"].lower() not in existing_labels:
                    existing_fields.append(nf)
            merged_fields = existing_fields
        else:
            merged_fields = new_fields
    else:
        merged_fields = new_fields

    await store.aput(
        namespace,
        template_name,
        {"fields": merged_fields},
    )

    action = "replaced" if replace else "updated"
    return f"Template '{template_name}' {action} successfully under user {_USER_ID}. Total fields: {len(merged_fields)}."
from langgraph.runtime import Runtime

from graphs.llm import llm
from graphs.state import mystate
from graphs.schemas import FormFields
from graphs.prompts import form_creator_prompt


structured_llm = llm.with_structured_output(FormFields)

form_creator_chain = form_creator_prompt | structured_llm


async def create_form(state: mystate, runtime: Runtime):

    store = runtime.store

    template = await store.aget(
        (
            state["user_id"],
            "templates",
        ),
        state["form_template_name"],
    )

    if template is None:
        raise ValueError(
            f"Template '{state['form_template_name']}' not found."
        )

    template_fields = template.value["fields"]

    additional_req = state.get("additional_form_requirements", "").strip()

    if not additional_req:
        return {
            "form_fields": template_fields
        }

    updated_fields = form_creator_chain.invoke(
        {
            "template": template_fields,
            "requirements": additional_req,
        }
    )

    return {
        "form_fields": updated_fields.fields
    }
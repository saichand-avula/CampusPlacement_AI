from graphs.schemas import EOIFields
from graphs.state import mystate
from graphs.llm import llm
from graphs.prompts import field_extractor_prompt


structured_llm = llm.with_structured_output(EOIFields)

field_extractor_chain = field_extractor_prompt | structured_llm


def extract_fields(state: mystate):

    extracted_fields = field_extractor_chain.invoke(
        {
            "jd_text": state["jd_text"],
            "raw_links": "\n".join(state["raw_links"]),
        }
    )

    return {
        "eoi_fields": extracted_fields
    }
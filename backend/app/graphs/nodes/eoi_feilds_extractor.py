from graphs.schemas import EOIFields
from graphs.state import mystate
from graphs.llm import llm
from graphs.prompts import field_extractor_prompt


structured_llm = llm.with_structured_output(EOIFields)

field_extractor_chain = field_extractor_prompt | structured_llm


def extract_fields(state: mystate):
    """
    Extracts EOI fields from the JD text, then merges with any preset values
    the user explicitly provided via the assistant.

    Priority: user-provided (preset_*) > JD-extracted > None
    """

    extracted: EOIFields = field_extractor_chain.invoke(
        {
            "jd_text": state["jd_text"],
            "raw_links": "\n".join(state["raw_links"]),
        }
    )

    def pick(preset_val, extracted_val):
        """Return preset_val if non-empty, else extracted_val."""
        if preset_val is not None and preset_val != "" and preset_val != []:
            return preset_val
        return extracted_val

    merged = EOIFields(
        company_name=pick(
            state.get("preset_company_name"),
            extracted.company_name,
        ),
        company_website=pick(
            state.get("preset_company_website"),
            extracted.company_website,
        ),
        linkedin_link=pick(
            state.get("preset_linkedin_link"),
            extracted.linkedin_link,
        ),
        job_title=pick(
            state.get("preset_job_title"),
            extracted.job_title,
        ),
        employment_type=pick(
            state.get("preset_employment_type"),
            extracted.employment_type,
        ),
        work_location=pick(
            state.get("preset_work_location"),
            extracted.work_location,
        ),
        stipend=pick(
            state.get("preset_stipend"),
            extracted.stipend,
        ),
        ctc=pick(
            state.get("preset_ctc"),
            extracted.ctc,
        ),
        duration=pick(
            state.get("preset_duration"),
            extracted.duration,
        ),
        eligibility=pick(
            state.get("preset_eligibility"),
            extracted.eligibility,
        ),
        branches=pick(
            state.get("preset_branches"),
            extracted.branches,
        ),
        job_description=extracted.job_description,
        selection_process=extracted.selection_process,
        other_benefits=extracted.other_benefits,
        assignment_required=extracted.assignment_required,
        assignment_link=extracted.assignment_link,
    )

    return {
        "eoi_fields": merged,
    }

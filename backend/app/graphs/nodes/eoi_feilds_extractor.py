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

    Fields that are extractor-only (job_description, about_company) are never
    overridden by presets.

    assignment_deadline is always set equal to the workflow deadline when
    assignment_required is True.
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

    # Resolve assignment_required first (needed for assignment_deadline logic)
    resolved_assignment_required = pick(
        state.get("preset_assignment_required"),
        extracted.assignment_required,
    )
    # Coerce to bool in case preset came in as None/truthy value
    if resolved_assignment_required is None:
        resolved_assignment_required = False

    # assignment_deadline always equals the form deadline (never extracted separately)
    resolved_assignment_deadline = (
        state.get("deadline") or None
    ) if resolved_assignment_required else None

    merged = EOIFields(
        # ── Company Info ──────────────────────────────────────────
        company_name=pick(
            state.get("preset_company_name"),
            extracted.company_name,
        ),
        company_website=pick(
            state.get("preset_company_website"),
            extracted.company_website,
        ),
        linkedin_url=pick(
            state.get("preset_linkedin_url"),
            extracted.linkedin_url,
        ),
        address=pick(
            state.get("preset_address"),
            extracted.address,
        ),

        # ── Job Details ───────────────────────────────────────────
        work_location=pick(
            state.get("preset_work_location"),
            extracted.work_location,
        ),
        job_designation=pick(
            state.get("preset_job_designation"),
            extracted.job_designation,
        ),
        employment_type=pick(
            state.get("preset_employment_type"),
            extracted.employment_type,
        ),

        # ── Eligibility ───────────────────────────────────────────
        eligibility_cgpa=pick(
            state.get("preset_eligibility_cgpa"),
            extracted.eligibility_cgpa,
        ),
        eligibility_backlogs=pick(
            state.get("preset_eligibility_backlogs"),
            extracted.eligibility_backlogs,
        ),
        eligibility_other=pick(
            state.get("preset_eligibility_other"),
            extracted.eligibility_other,
        ),

        # ── Branches ─────────────────────────────────────────────
        applicable_branches=pick(
            state.get("preset_applicable_branches"),
            extracted.applicable_branches,
        ),

        # ── Compensation ──────────────────────────────────────────
        stipend=pick(
            state.get("preset_stipend"),
            extracted.stipend,
        ),
        ctc=pick(
            state.get("preset_ctc"),
            extracted.ctc,
        ),

        # ── Extractor-only fields (no preset override) ────────────
        job_description=extracted.job_description,
        about_company=extracted.about_company,

        # ── Process / Benefits (preset wins, but extractor tries to extract) ──
        selection_process=pick(
            state.get("preset_selection_process"),
            extracted.selection_process,
        ),
        bond=pick(
            state.get("preset_bond"),
            extracted.bond,
        ),
        slp_duration=pick(
            state.get("preset_slp_duration"),
            extracted.slp_duration,
        ),
        other_benefits=pick(
            state.get("preset_other_benefits"),
            extracted.other_benefits,
        ),

        # ── Assignment ────────────────────────────────────────────
        assignment_required=resolved_assignment_required,
        assignment_deadline=resolved_assignment_deadline,
        assignment_link=pick(
            state.get("preset_assignment_link"),
            extracted.assignment_link,
        ),
    )

    return {
        "eoi_fields": merged,
    }

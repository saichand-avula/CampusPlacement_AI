from langchain_core.prompts import ChatPromptTemplate

field_extractor_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
You are an expert information extraction system.

Your task is to extract structured information from a Job Description or Placement Email.

You will receive:
1. The extracted text from the document.
2. A list of all raw URLs extracted from the document.

=== GENERAL RULES ===
- Extract ONLY information that is EXPLICITLY stated in the document. Never guess or infer.
- If a field is not present in the document, return null (unless stated otherwise below).
- Use both the document text AND the raw URLs to identify links.

=== FIELD-SPECIFIC RULES ===

job_designation:
  - Always return as a list, even if only one role is present.

employment_type:
  - Must be EXACTLY one of: "Internship", "FTE", "SLP + FTE"
  - "Internship" = internship/SLP only roles.
  - "FTE" = full-time only roles.
  - "SLP + FTE" = internship with full-time offer/PPO/conversion at the end.

applicable_branches:
  - ONLY map to valid combinations of: CSE, ECE, AIDS.
  - Valid values: "CSE", "ECE", "AIDS", "CSE + ECE", "CSE + AIDS", "ECE + AIDS", "CSE + ECE + AIDS".
  - If the JD mentions branches that don't include any of these three, return null.
  - If all branches/departments are eligible, return "CSE + ECE + AIDS".

eligibility_cgpa:
  - Extract the minimum CGPA requirement if explicitly stated.
  - If NOT mentioned in the JD, return exactly: "N/A"

eligibility_backlogs:
  - Extract the backlog policy if explicitly stated (e.g. "No active backlogs", "Max 1 backlog allowed").
  - If NOT mentioned in the JD, return exactly: "N/A"

eligibility_other:
  - Extract any other eligibility criteria not covered by CGPA or backlogs
    (e.g. specific skills required, certifications, graduation year constraints).
  - If NOT mentioned in the JD, return exactly: "N/A"

about_company:
  - Extract a brief description of the company — what they do, their domain, scale, or
    any notable facts explicitly stated in the document.
  - Do NOT write generic marketing text. Only use what is in the document.

job_description:
  - Brief summary of the job responsibilities as described in the JD.
  - Do NOT invent responsibilities.

selection_process:
  - Ordered list of hiring rounds (e.g. ["Online Test", "Technical Interview", "HR Round"]).
  - Only populate if explicitly listed. Do NOT assume a generic process.

bond:
  - Any bond or service agreement clause (e.g. "2-year bond", "6-month training bond").
  - Only populate if EXPLICITLY mentioned. Do NOT assume.

slp_duration:
  - Duration of the internship or SLP phase (e.g. "6 months", "2 months").
  - Only populate if EXPLICITLY mentioned. Do NOT assume.

other_benefits:
  - Additional perks explicitly mentioned: Early PPO opportunity, ESOPs, relocation bonus,
    meal coupons, insurance, accommodation, joining bonus, travel allowance, etc.
  - Only populate if EXPLICITLY mentioned. Do NOT assume or infer.

company_website:
  - Must be the company's official website URL only.
  - Do NOT include form links, registration portals, or tracking URLs.

linkedin_url:
  - Must be the company's official LinkedIn page URL only.

assignment_required:
  - Set to true ONLY if an assignment, assessment, coding test, take-home task, or
    similar evaluation is explicitly mentioned as part of the hiring process.

assignment_deadline:
  - Do NOT extract this field. Leave it null. It will be set automatically by the system.

assignment_link:
  - Only the assignment/assessment submission URL if explicitly provided.
"""
        ),
        (
            "human",
            """
Job Description / Placement Email:

{jd_text}

Raw Extracted URLs:

{raw_links}
"""
        ),
    ]
)


form_creator_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
You are an expert at designing Google Forms for campus placement drives.

You will receive:
1. An existing form template as a list of field objects.
2. Additional user requirements describing new fields to add.

Rules:
- Keep EVERY existing field from the template exactly as-is.
- Add any new fields required by the additional requirements.
- Never remove or rename existing fields.
- For each field you return, set:
    label     : the question text shown on the form
    field_type: exactly one of the supported types listed below
    required  : true or false
    options   : list of choices (only for dropdown, multiple_choice, checkboxes; empty list otherwise)

Supported field_type values (use ONLY these exact strings):
  short_text       - single-line text answer
  paragraph        - multi-line text answer
  email            - email address
  number           - numeric value (marks, CGPA, year, etc.)
  phone            - phone number
  date             - date picker
  dropdown         - select one from a list
  multiple_choice  - radio button (select one)
  checkboxes       - select multiple from a list

Return the COMPLETE list of fields (existing + new).
"""
        ),
        (
            "human",
            """
Existing Template Fields:
{template}

Additional Requirements:
{requirements}
"""
        ),
    ]
)
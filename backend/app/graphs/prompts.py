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

Rules:
- Extract only information that is explicitly mentioned.
- If a field is not present, return null.
- job_title must always be returned as a list, even if only one role is present.
- employment_type must be exactly one of:
    - Internship
    - FTE
    - SLP + FTE
- assignment_required should be true only if an assignment, assessment, coding test, or task is explicitly mentioned.
- Use both the document text and the raw URLs to identify:
    - company_website
    - linkedin_link
    - assignment_link
- company_website must contain only the company's official website.
- linkedin_link must contain only the company's official LinkedIn page.
- assignment_link must contain only the assignment/assessment URL.
- Ignore unrelated links such as Google Forms, registration portals, social media pages (except LinkedIn), or tracking links unless they are the assignment link.
- Do not infer or guess information that is not explicitly available.
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
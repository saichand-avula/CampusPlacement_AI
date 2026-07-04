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
You are an expert at designing Google Forms.

You will receive:
1. An existing form template as a dictionary.
2. Additional user requirements.

Rules:
- Keep every existing field unless explicitly told to remove it.
- Add any fields required by the additional requirements.
- Update field types if necessary.
- Return the complete set of fields.
- Supported types:
  string
  email
  phone
  integer
  float
  number
  boolean
  date
  url
  file
"""
        ),
        (
            "human",
            """
Existing Template:
{template}

Additional Requirements:
{requirements}
"""
        ),
    ]
)
"""
seed_basic_template.py
======================
Run once to:
  1. Create / migrate memory.db (store + checkpoint tables)
  2. Insert the hardcoded "basic template" for user_id = "1"

Usage:
    python seed_basic_template.py
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "app"))

from store_connection import init_store, close_store

USER_ID = "1"
TEMPLATE_NAME = "basic template"

BASIC_TEMPLATE_FIELDS = [
    {"label": "Full Name", "field_type": "short_text", "required": True, "options": []},
    {"label": "Email Address", "field_type": "email", "required": True, "options": []},
    {"label": "Phone Number", "field_type": "phone", "required": True, "options": []},
    {"label": "Roll Number", "field_type": "short_text", "required": True, "options": []},
    {"label": "Branch / Department", "field_type": "dropdown", "required": True, "options": ["CSE", "ECE", "AIDS"]},
    {"label": "Year of Graduation", "field_type": "number", "required": True, "options": []},
    {"label": "CGPA", "field_type": "number", "required": True, "options": []},
    {"label": "Resume Link (Google Drive / PDF)", "field_type": "short_text", "required": False, "options": []},
    {"label": "Are you interested in this placement drive?", "field_type": "multiple_choice", "required": True, "options": ["Yes", "No"]},
    {"label": "Additional Comments", "field_type": "paragraph", "required": False, "options": []},
]


async def seed():
    print("Initializing memory.db store ...")
    store = await init_store()
    print("Store initialized (memory.db created / migrated)\n")

    namespace = (USER_ID, "templates")

    print(f'Seeding template "{TEMPLATE_NAME}" for user_id="{USER_ID}" ...')
    await store.aput(namespace, TEMPLATE_NAME, {"fields": BASIC_TEMPLATE_FIELDS})
    print(f'Template "{TEMPLATE_NAME}" saved successfully!\n')

    print("Verifying stored template ...")
    items = await store.asearch(namespace)
    found = [item for item in items if item.key == TEMPLATE_NAME]

    if found:
        fields = found[0].value.get("fields", [])
        print(f"Found template with {len(fields)} fields:")
        for f in fields:
            req = "required" if f["required"] else "optional"
            print(f"  [{f['field_type']}] {f['label']} - {req}")
    else:
        print("ERROR: Template NOT found!")

    await close_store()
    print("\nDone! memory.db is fresh and ready.")


if __name__ == "__main__":
    asyncio.run(seed())

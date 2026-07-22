import json
import uuid

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from langchain_core.messages import HumanMessage
from pydantic import BaseModel

from sqllite_connection import get_connection
from store_connection import get_store
from assistant.assistant_graph import get_graph

router = APIRouter(prefix="/chat", tags=["chat"])


class MessageRequest(BaseModel):
    message: str


# ─────────────────────────────────────────────
# GET /chat/list
# ─────────────────────────────────────────────

@router.get("/list")
async def list_chats():
    """Return all chats for user_id='1', ordered by latest."""

    conn = get_connection()
    cursor = conn.cursor()

    rows = cursor.execute(
        """
        SELECT thread_id, chat_name AS title, updated_at
        FROM chats
        WHERE user_id = ?
        ORDER BY updated_at DESC
        """,
        ("1",),
    ).fetchall()

    return [dict(row) for row in rows]


# ─────────────────────────────────────────────
# GET /chat/templates/{user_id}
# ─────────────────────────────────────────────

@router.get("/templates/{user_id}")
async def list_templates(user_id: str):
    """
    Return all form template names saved for a user in the store.
    Namespace: (user_id, "templates").
    """
    store = get_store()
    items = await store.asearch((user_id, "templates"))

    templates = [
        {
            "name": item.key,
            "fields": item.value.get("fields", []),
        }
        for item in items
    ]

    return {"templates": templates, "count": len(templates)}


# ─────────────────────────────────────────────
# GET /chat/assistant-state/{thread_id}
# ─────────────────────────────────────────────

@router.get("/assistant-state/{thread_id}")
async def get_assistant_state(thread_id: str):
    """
    Return the key assistant state fields for the given thread
    (workflow_initialized, jd_path, company_name, template, etc.).
    """
    graph = get_graph()
    config = {"configurable": {"thread_id": thread_id}}

    state = await graph.aget_state(config)
    if not state or not state.values:
        return {
            "workflow_initialized": False,
            "initial_jd_path": None,
            "initial_company_name": None,
            "initial_form_template_name": None,
        }

    values = state.values
    return {
        "workflow_initialized": values.get("workflow_initialized", False),
        "initial_jd_path": values.get("initial_jd_path"),
        "initial_company_name": values.get("initial_company_name"),
        "initial_form_template_name": values.get("initial_form_template_name"),
        "initial_deadline": values.get("initial_deadline"),
        # Company
        "initial_company_website": values.get("initial_company_website"),
        "initial_linkedin_url": values.get("initial_linkedin_url"),
        "initial_address": values.get("initial_address"),
        # Job
        "initial_job_designation": values.get("initial_job_designation"),
        "initial_employment_type": values.get("initial_employment_type"),
        "initial_work_location": values.get("initial_work_location"),
        # Eligibility
        "initial_eligibility_cgpa": values.get("initial_eligibility_cgpa"),
        "initial_eligibility_backlogs": values.get("initial_eligibility_backlogs"),
        "initial_eligibility_other": values.get("initial_eligibility_other"),
        # Branches
        "initial_applicable_branches": values.get("initial_applicable_branches"),
        # Compensation
        "initial_stipend": values.get("initial_stipend"),
        "initial_ctc": values.get("initial_ctc"),
        # Process / Benefits
        "initial_selection_process": values.get("initial_selection_process"),
        "initial_bond": values.get("initial_bond"),
        "initial_slp_duration": values.get("initial_slp_duration"),
        "initial_other_benefits": values.get("initial_other_benefits"),
        # Assignment
        "initial_assignment_required": values.get("initial_assignment_required"),
        "initial_assignment_link": values.get("initial_assignment_link"),
    }


# ─────────────────────────────────────────────
# GET /chat/workflow-state/{thread_id}
# ─────────────────────────────────────────────

@router.get("/workflow-state/{thread_id}")
async def get_workflow_state(thread_id: str):
    """
    Return the finalized workflow output for the given thread.
    Results are stored in the LangGraph store under
    (user_id=1, 'workflow_results') keyed by thread_id.
    This avoids any checkpointer-conflict with the assistant graph.
    """
    store = get_store()
    item = await store.aget(("1", "workflow_results"), thread_id)

    if item is None:
        raise HTTPException(
            status_code=404,
            detail="Workflow results not available yet for this thread.",
        )

    values: dict = item.value

    return {
        "thread_id": values.get("thread_id"),
        "user_id": values.get("user_id"),
        "jd_path": values.get("jd_path"),
        "jd_text": (values.get("jd_text") or "")[:500],   # truncated for display
        "deadline": values.get("deadline"),
        "form_template_name": values.get("form_template_name"),
        "eoi_fields": values.get("eoi_fields"),          # already a plain dict
        "form_fields": values.get("form_fields"),
        "form_link": values.get("form_link"),
        "form_sheet_link": values.get("form_sheet_link"),
        "form_drive_link": values.get("form_drive_link"),
        "raw_links": values.get("raw_links", []),
    }


# ─────────────────────────────────────────────
# POST /chat/new
# ─────────────────────────────────────────────

@router.post("/new")
async def new_chat():
    """Create a new thread. Returns thread_id only."""

    thread_id = str(uuid.uuid4())

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO chats (thread_id, user_id)
        VALUES (?, ?)
        """,
        (thread_id, "1"),
    )

    conn.commit()

    return {"thread_id": thread_id}


# ─────────────────────────────────────────────
# GET /chat/{thread_id}  — messages
# ─────────────────────────────────────────────

@router.get("/{thread_id}")
async def get_messages(thread_id: str):
    """Return complete conversation for a thread."""

    conn = get_connection()
    cursor = conn.cursor()

    rows = cursor.execute(
        """
        SELECT id, thread_id, role, content, created_at
        FROM messages
        WHERE thread_id = ?
        ORDER BY created_at ASC
        """,
        (thread_id,),
    ).fetchall()

    return [dict(row) for row in rows]


# ─────────────────────────────────────────────
# POST /chat/{thread_id}  —  SSE streaming
# ─────────────────────────────────────────────

async def _stream_response(thread_id: str, message: str):
    """
    Async generator that:
      1. Invokes the assistant graph with astream_events.
      2. Yields SSE `data:` frames for each text token.
      3. Keeps the connection alive with heartbeat comments during
         long-running tool calls (e.g. initialize_workflow).
      4. Saves user + assistant messages to the DB.
      5. Yields a final `[DONE]` sentinel.
    """
    import asyncio
    import time

    graph = get_graph()

    config = {
        "configurable": {
            "thread_id": thread_id,
        }
    }

    input_data = {
        "messages": [HumanMessage(content=message)],
    }

    full_response = ""
    last_heartbeat = time.monotonic()
    HEARTBEAT_INTERVAL = 10  # seconds

    try:
        async for event in graph.astream_events(
            input_data,
            config=config,
            version="v2",
        ):
            # ── Heartbeat: keep SSE alive during slow tool calls ──
            now = time.monotonic()
            if now - last_heartbeat >= HEARTBEAT_INTERVAL:
                yield ": heartbeat\n\n"  # SSE comment — ignored by parser, keeps TCP alive
                last_heartbeat = now

            event_name = event["event"]

            # ── Tool start: let frontend know we're working ────────
            if event_name == "on_tool_start":
                tool_name = event.get("name", "")
                if tool_name == "initialize_workflow":
                    yield f"data: {json.dumps({'token': '⚙️ Running workflow…'})}\n\n"
                    last_heartbeat = time.monotonic()
                continue

            if event_name != "on_chat_model_stream":
                continue

            # Only stream tokens from the "assistant" node
            node = event.get("metadata", {}).get(
                "langgraph_node", ""
            )
            if node != "assistant":
                continue

            chunk = event["data"].get("chunk")
            if chunk is None:
                continue

            content = getattr(chunk, "content", "")
            if not isinstance(content, str) or not content:
                continue

            full_response += content

            yield f"data: {json.dumps({'token': content})}\n\n"
            last_heartbeat = time.monotonic()

    except Exception as exc:
        yield f"data: {json.dumps({'error': str(exc)})}\n\n"
        return

    # ── Persist to SQLite ──────────────────────

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO messages (thread_id, role, content) VALUES (?, ?, ?)",
        (thread_id, "user", message),
    )

    cursor.execute(
        "INSERT INTO messages (thread_id, role, content) VALUES (?, ?, ?)",
        (thread_id, "assistant", full_response),
    )

    cursor.execute(
        "UPDATE chats SET updated_at = CURRENT_TIMESTAMP WHERE thread_id = ?",
        (thread_id,),
    )

    conn.commit()

    yield "data: [DONE]\n\n"


@router.post("/{thread_id}")
async def send_message(thread_id: str, body: MessageRequest):
    """
    Accept a user message, invoke the assistant graph,
    and stream the response back as Server-Sent Events.
    """

    return StreamingResponse(
        _stream_response(thread_id, body.message),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )

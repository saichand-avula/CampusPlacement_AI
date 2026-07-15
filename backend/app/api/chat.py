import json
import uuid

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from langchain_core.messages import HumanMessage
from pydantic import BaseModel

from sqllite_connection import get_connection
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
# GET /chat/{thread_id}
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
      3. Saves user + assistant messages to the DB.
      4. Yields a final `[DONE]` sentinel.
    """

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

    try:
        async for event in graph.astream_events(
            input_data,
            config=config,
            version="v2",
        ):
            if event["event"] != "on_chat_model_stream":
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

from fastapi import APIRouter, Form
from sqllite_connection import get_connection
import uuid

router = APIRouter()


def create_thread() -> str:
    thread_id = str(uuid.uuid4())

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO chats (thread_id, user_id)
        VALUES (?, ?)
        """,
        (thread_id, "1")  # TODO: Replace with logged-in user_id
    )

    conn.commit()
    conn.close()

    return thread_id


@router.post("/newchat")
async def new_chat(
    message: str = Form(...),
):
    # Create a new chat
    thread_id = create_thread()

    # Save the first user message
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO messages (thread_id, role, content)
        VALUES (?, ?, ?)
        """,
        (
            thread_id,
            "user",
            message,
        ),
    )

    conn.commit()
    conn.close()

    # TODO:
    # response = graph.invoke({
    #     "thread_id": thread_id,
    #     "messages": [HumanMessage(content=message)]
    # })

    return {
        "thread_id": thread_id,
        "status": "success",
    }
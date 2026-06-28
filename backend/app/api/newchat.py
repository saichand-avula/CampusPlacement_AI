from fastapi import APIRouter, UploadFile, File, Form
from pathlib import Path
import shutil
from graphs.graph import graph

router = APIRouter()


def getthreadid():
    return "1"


@router.post("/newchat")
async def new_chat(
    deadline: str = Form(...),
    jd: UploadFile = File(...)
):

    thread_id = getthreadid()

    # Create public/<thread_id>/
    upload_dir = Path("public") / thread_id
    upload_dir.mkdir(parents=True, exist_ok=True)

    extension = Path(jd.filename).suffix
    jd_path = upload_dir / f"jd{extension}"

    with open(jd_path, "wb") as buffer:
        shutil.copyfileobj(jd.file, buffer)

    # Initial graph state
    initial_state = {
        "thread_id": thread_id,
        "deadline": deadline,
        "jd_path": str(jd_path),
    }

    # Run the graph
    final_state = graph.invoke(initial_state)

    return {
        "thread_id": thread_id,
        "state": final_state
    }
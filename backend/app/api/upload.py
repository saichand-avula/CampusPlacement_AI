import os
import shutil

from fastapi import APIRouter, File, HTTPException, UploadFile

from assistant.assistant_graph import get_graph

router = APIRouter(prefix="/upload", tags=["upload"])

JD_UPLOAD_DIR = os.path.join(
    os.path.dirname(__file__), "..", "..", "public", "jd_uploads"
)


@router.post("/jd/{thread_id}")
async def upload_jd(thread_id: str, file: UploadFile = File(...)):
    """
    Upload or replace a JD PDF for a given thread.
    Saves to public/jd_uploads/{thread_id}/ and patches
    initial_jd_path in the assistant LangGraph checkpoint via update_state.
    Returns the saved absolute file path.
    """
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are accepted.",
        )

    # ── Ensure upload directory exists ─────────────────────────
    upload_dir = os.path.join(JD_UPLOAD_DIR, thread_id)
    os.makedirs(upload_dir, exist_ok=True)

    # ── Remove any previous JD for this thread ─────────────────
    for old_file in os.listdir(upload_dir):
        os.remove(os.path.join(upload_dir, old_file))

    # ── Save new file ──────────────────────────────────────────
    dest_path = os.path.join(upload_dir, file.filename)
    with open(dest_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    abs_path = os.path.abspath(dest_path)

    # ── Patch assistant graph state via update_state ───────────
    graph = get_graph()
    config = {"configurable": {"thread_id": thread_id}}

    await graph.aupdate_state(
        config,
        {"initial_jd_path": abs_path},
    )

    return {
        "jd_path": abs_path,
        "filename": file.filename,
        "thread_id": thread_id,
    }

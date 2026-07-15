from pathlib import Path

from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

_checkpointer = None
_checkpointer_ctx = None

DB_PATH = Path(__file__).resolve().parents[1] / "memory.db"


async def init_checkpointer():
    global _checkpointer, _checkpointer_ctx

    if _checkpointer is None:
        _checkpointer_ctx = AsyncSqliteSaver.from_conn_string(
            str(DB_PATH)
        )
        _checkpointer = await _checkpointer_ctx.__aenter__()
        await _checkpointer.setup()

    return _checkpointer


def get_checkpointer():
    if _checkpointer is None:
        raise RuntimeError(
            "Checkpointer has not been initialized. "
            "Call init_checkpointer() first."
        )

    return _checkpointer


async def close_checkpointer():
    global _checkpointer, _checkpointer_ctx

    if _checkpointer_ctx is not None:
        await _checkpointer_ctx.__aexit__(None, None, None)
        _checkpointer = None
        _checkpointer_ctx = None

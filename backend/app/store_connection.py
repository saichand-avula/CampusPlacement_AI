from pathlib import Path

from langgraph.store.sqlite import AsyncSqliteStore

_store = None
_store_ctx = None

DB_PATH = Path(__file__).resolve().parents[1] / "memory.db"


async def init_store():
    global _store, _store_ctx

    if _store is None:
        _store_ctx = AsyncSqliteStore.from_conn_string(
            str(DB_PATH)
        )
        _store = await _store_ctx.__aenter__()
        await _store.setup()

    return _store


async def close_store():
    global _store, _store_ctx

    if _store_ctx is not None:
        await _store_ctx.__aexit__(None, None, None)
        _store = None
        _store_ctx = None


def get_store():
    if _store is None:
        raise RuntimeError(
            "Store has not been initialized. Call init_store() first."
        )

    return _store
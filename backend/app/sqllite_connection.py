from pathlib import Path
import sqlite3

_connection = None

DB_PATH = Path(__file__).resolve().parents[1] / "chats.db"


def init_database():
    global _connection

    if _connection is None:
        _connection = sqlite3.connect(
            DB_PATH,
            check_same_thread=False,
        )
        _connection.row_factory = sqlite3.Row

    return _connection


def get_connection():
    if _connection is None:
        raise RuntimeError(
            "Database has not been initialized. Call init_database() first."
        )

    return _connection


def close_database():
    global _connection

    if _connection is not None:
        _connection.close()
        _connection = None
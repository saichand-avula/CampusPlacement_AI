import os
import re
from threading import Lock

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnableLambda

load_dotenv()

_GROQ_BASE_URL = "https://api.groq.com/openai/v1"
_GROQ_MODEL = "openai/gpt-oss-20b"
_rotation_lock = Lock()
_rotation_index = 0


def _load_groq_api_keys() -> list[str]:
    keys: list[tuple[int, str]] = []

    for name, value in os.environ.items():
        match = re.fullmatch(r"GROQ_API_KEY(\d*)", name)
        if match is None:
            continue

        normalized_value = value.strip()
        if not normalized_value:
            continue

        suffix = match.group(1)
        order = int(suffix) if suffix else 0
        keys.append((order, normalized_value))

    keys.sort(key=lambda item: item[0])
    return [key for _, key in keys]


def _next_groq_api_keys() -> list[str]:
    keys = _load_groq_api_keys()
    if not keys:
        raise RuntimeError(
            "No Groq API keys found. Set GROQ_API_KEY, GROQ_API_KEY1, GROQ_API_KEY2, ... in your environment."
        )

    global _rotation_index

    with _rotation_lock:
        start_index = _rotation_index % len(keys)
        _rotation_index = (_rotation_index + 1) % len(keys)

    return keys[start_index:] + keys[:start_index]


def _invoke_with_key_rotation(schema, payload, use_async: bool = False):
    last_error: Exception | None = None

    for api_key in _next_groq_api_keys():
        structured_llm = ChatOpenAI(
            model=_GROQ_MODEL,
            api_key=api_key,
            base_url=_GROQ_BASE_URL,
            temperature=0,
            streaming=True,
            max_retries=0,
        ).with_structured_output(schema)
        try:
            if use_async:
                return structured_llm.ainvoke(payload)
            return structured_llm.invoke(payload)
        except Exception as error:
            last_error = error
            continue

    if last_error is not None:
        raise last_error

    raise RuntimeError("Groq structured output invocation failed unexpectedly.")


class _RotatingGroqClient:
    def with_structured_output(self, schema):
        return RunnableLambda(
            func=lambda payload: _invoke_with_key_rotation(schema, payload),
            afunc=lambda payload: _invoke_with_key_rotation(schema, payload, True),
        )


llm = _RotatingGroqClient()
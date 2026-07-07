from typing import Literal

from pydantic import BaseModel, Field


class Memory(BaseModel):
    content: str = Field(
        description="The important long-term memory to store."
    )

    category: Literal[
        "identity",
        "profession",
        "preference",
        "goal",
        "project",
        "other",
    ] = Field(
        description="Category of the memory."
    )


class MemoryList(BaseModel):
    memories: list[Memory] = Field(
        default_factory=list,
        description="List of memories worth storing."
    )
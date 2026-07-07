from langgraph.graph.message import add_messages
from typing import Annotated, TypedDict
from langchain_core.messages import BaseMessage


class AssistantState(TypedDict):
    thread_id:str
    summary:str
    messages: Annotated[list[BaseMessage], add_messages]


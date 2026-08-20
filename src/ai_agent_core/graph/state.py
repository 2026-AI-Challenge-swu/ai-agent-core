from typing import Annotated, Literal
from typing_extensions import TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    session_id: str
    query: str

    messages: Annotated[list[BaseMessage], add_messages]

    sub_tasks: list[str]
    plan: str | None
    tool_results: list[dict]

    answer: str | None

    quality_score: float | None
    quality_feedback: str | None

    retry_count: int
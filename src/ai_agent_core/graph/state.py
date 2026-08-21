from typing import Annotated, TypedDict
import operator


class AgentState(TypedDict, total=False):
    session_id: str
    query: str

    sub_queries: list[dict]

    worker_results: Annotated[list[dict], operator.add]

    quality_score: float | None
    quality_feedback: str | None

    final_answer: str | None


class WorkerState(TypedDict, total=False):
    # 하나의 세부 질문
    sub_query: str

    # 몇 번째 sub-query인지
    sub_query_id: int
    # planner 결과
    plan: dict
    # tool 실행 결과
    tool_result: dict

    # 생성된 답변
    answer: str

    # 최종 worker 결과
    worker_results: Annotated[list, operator.add]
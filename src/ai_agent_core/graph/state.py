from typing import Annotated, TypedDict
import operator



class UserProfile(TypedDict):
    totalScore: int
    type: str
    grade: int
    nickname: str
    officialName: str
    description: str
    


class AgentState(TypedDict, total=False):
    """
    Main State
    """
    mode: str
    session_id: str
    query: str
    userProfile: UserProfile | None
    portfolio: any
    retirementPlan: any
    metrics: any

    sub_queries: list[dict]

    worker_results: Annotated[list[dict], operator.add]

    quality_score: float | None
    quality_feedback: str | None

    final_answer: str | None


class WorkerState(TypedDict, total=False):
    """
    decomposer 이후 병렬 처리되는 worker state
    """
    sub_mode: str
    sub_query: str
    intent: str

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
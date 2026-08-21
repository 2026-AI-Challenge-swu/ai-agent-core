from src.ai_agent_core.graph.state import WorkerState
from src.ai_agent_core.graph.nodes.base import BaseNode


class GenerateAnswerNode(BaseNode):
    system_path = "./prompts/generate_answer.system.md"
    user_path = "./prompts/generate_answer.user.md"

    async def __call__(self, state: WorkerState) -> dict:
        if state["intent"] == "reject":
            answer="요청하신 정보는 연금 상담 서비스 범위를 벗어나 안내가 어려운 점 양해 부탁드립니다."


        else:
            user_input = {
                "query": state["query"],
            }
            answer=""


        return {
            "answer": answer,
            "worker_results": [
                {
                    "sub_query_id": state["sub_query_id"],
                    "query": state["sub_query"],
                    "plan": state.get("plan"),
                    "tool_result": state.get("tool_result"),
                    "answer": answer,
                }
            ],
        }

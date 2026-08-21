from src.ai_agent_core.graph.state import WorkerState
from src.ai_agent_core.graph.nodes.base import BaseNode


class GenerateAnswerNode(BaseNode):
    system_path = "./prompts/generate_answer.system.md"
    user_path = "./prompts/generate_answer.user.md"

    def __call__(self, state: WorkerState) -> dict:
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

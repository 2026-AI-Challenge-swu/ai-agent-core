from src.ai_agent_core.graph.state import AgentState
from src.ai_agent_core.graph.nodes.base import BaseNode
from ai_common.utils.io import parse_str_to_json


class GenerateAnswerNode(BaseNode):
    system_path = "./prompts/generate_answer.system.md"
    user_path = "./prompts/generate_answer.user.md"

    def __call__(self, state: AgentState) -> dict:
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

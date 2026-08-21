from src.ai_agent_core.graph.state import AgentState
from src.ai_agent_core.graph.nodes.base import BaseNode


class DecomposerNode(BaseNode):
    system_path = "./prompts/decomposer.system.md"
    user_path = "./prompts/decomposer.user.md"


    def __call__(self, state: AgentState) -> dict:
        query = state["query"]


        return {
            "sub_queries": [{"sub_query_id": idx, "sub_query": i}for idx, i in enumerate(query.split(","))],
        }
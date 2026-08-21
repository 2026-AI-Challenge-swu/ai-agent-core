from src.ai_agent_core.graph.state import AgentState
from src.ai_agent_core.graph.nodes.base import BaseNode


class ToolCallNode(BaseNode):
    system_path = "./prompts/tool_call.system.md"
    user_path = "./prompts/tool_call.user.md"


    def __call__(self, state: AgentState) -> dict:
        plan = state["plan"]

        tool_results = []

        return {
            "tool_results": [],
        }
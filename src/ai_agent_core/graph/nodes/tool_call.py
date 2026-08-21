from src.ai_agent_core.graph.state import WorkerState
from src.ai_agent_core.graph.nodes.base import BaseNode


class ToolCallNode(BaseNode):
    system_path = "./prompts/tool_call.system.md"
    user_path = "./prompts/tool_call.user.md"


    async def __call__(self, state: WorkerState) -> dict:
        if state["intent"] == "reject":
            return state

        plan = state["plan"]
        tool_results = []

        return {
            "tool_results": {},
        }
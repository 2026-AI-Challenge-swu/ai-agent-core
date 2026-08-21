from src.ai_agent_core.graph.state import WorkerState
from src.ai_agent_core.graph.nodes.base import BaseNode
from src.ai_agent_core.tools.registry import tool_registry


class ToolCallNode(BaseNode):
    system_path = "./prompts/tool_call.system.md"
    user_path = "./prompts/tool_call.user.md"


    def __init__(self, app_state):
        super().__init__(app_state)
        self.tool_registry = tool_registry

    async def __call__(self, state: WorkerState) -> dict:
        if state["intent"] == "reject":
            return state

        plan = state["plan"]
        plan_id = plan.get("plan_id")
        status = plan.get("status")
        execution_steps = plan.get("execution_steps")

        return {
            "tool_result": {},
        }
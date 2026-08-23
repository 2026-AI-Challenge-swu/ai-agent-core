import inspect

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
        execution_steps = plan.get("execution_steps") or []

        tool_result = {}
        for step in execution_steps:
            tool_name = step["tool"]
            args = step.get("args", {})
            output_variable = step["output_variable"]

            tool_fn = self.tool_registry.get(tool_name)
            if tool_fn is None:
                self.logger.warning(f"[ToolCallNode] unknown tool: {tool_name}")
                continue

            result = tool_fn(**args)
            if inspect.isawaitable(result):
                result = await result

            tool_result[output_variable] = {
                "tool_name": tool_name,
                "result": result,
            }

        return {
            "tool_result": tool_result,
        }
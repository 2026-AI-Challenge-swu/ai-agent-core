from src.ai_agent_core.graph.state import AgentState


class ToolCallNode:

    def __init__(self, app_state):
        self.logger = app_state.logger
        self.tools = app_state.tools

    def __call__(self, state: AgentState) -> dict:
        plan = state["plan"]

        tool_results = []

        return {
            "tool_results": [],
        }
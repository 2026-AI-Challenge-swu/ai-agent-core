from src.ai_agent_core.graph.state import AgentState



class DecomposerNode:
    def __init__(self, app_state):
        self.logger = app_state.logger
        self.llm = app_state.llm

    def __call__(self, state: AgentState) -> dict:
        query = state["query"]


        return {
            "sub_tasks": [],
        }
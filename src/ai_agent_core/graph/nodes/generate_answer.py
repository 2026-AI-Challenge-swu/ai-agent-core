from src.ai_agent_core.graph.state import AgentState


class GenerateAnswerNode:
    def __init__(self, app_state):
        self.logger = app_state.logger
        self.llm = app_state.llm

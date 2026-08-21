from src.ai_agent_core.graph.state import AgentState
from src.ai_agent_core.graph.nodes.base import BaseNode


class QualityCheckNode(BaseNode):
    system_path = "./prompts/quality_check.system.md"
    user_path = "./prompts/quality_check.user.md"


    async def __call__(self, state: AgentState) -> dict:
        return {
            "quality_score": 1.0,
            "quality_feedback": ""
        }

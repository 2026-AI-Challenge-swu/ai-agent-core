from src.ai_agent_core.graph.state import AgentState
from src.ai_agent_core.graph.nodes.base import BaseNode


class SynthesizerNode(BaseNode):
    system_path = "./prompts/synthesizer.system.md"
    user_path = "./prompts/synthesizer.user.md"

    
    def __call__(self, state: AgentState) -> dict:
        final_answer = ""

        return {
            "final_answer" : final_answer
        } 

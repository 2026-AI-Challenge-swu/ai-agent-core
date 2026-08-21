from src.ai_agent_core.graph.state import AgentState
from src.ai_agent_core.graph.nodes.base import BaseNode


class SynthesizerNode(BaseNode):
    system_path = "./prompts/synthesizer.system.md"
    user_path = "./prompts/synthesizer.user.md"

    
    async def __call__(self, state: AgentState) -> dict:
        user_input = {
            "query": state["query"]
        }

        system_prompt = self.llm.get_prompt(self.system_path)
        user_prompt = self.llm.get_prompt(self.user_path, **user_input)

        input = {
            "system_prompt": system_prompt,
            "user_prompt": user_prompt,
        }

        
        final_answer = "얍!"

        return {
            "final_answer" : final_answer
        } 

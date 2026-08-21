from src.ai_agent_core.graph.state import AgentState
from src.ai_agent_core.graph.nodes.base import BaseNode


class SynthesizerNode(BaseNode):
    system_path = "./prompts/synthesizer.system.md"
    user_path = "./prompts/synthesizer.user.md"

    def _build_sub_qa_text(self, worker_results):
        sub_qa_text = []
        if worker_results:
            sub_qa_text.append("- 서브 결과 목록:")
            for idx, result in enumerate(worker_results):
                sub_qa_text.append(f'Q{idx}: {result["query"]} -> A{idx}: {result["answer"]}')

        return " ".join(sub_qa_text)

    async def __call__(self, state: AgentState) -> dict:
        user_input = {
            "query": state["query"],
            "sub_qa_text": self._build_sub_qa_text(state["worker_results"])
        }

        system_prompt = self.llm.get_prompt(self.system_path)
        user_prompt = self.llm.get_prompt(self.user_path, **user_input)

        input = {
            "system_prompt": system_prompt,
            "user_prompt": user_prompt,
            "max_output_tokens": 2048
        }

        def validate_format(result):
            if result:
                return True
            
            return False

        
        final_answer = self._retry_invoke(
            input=input,
            execute_fn=lambda kwargs: self.llm.call_gpt(**kwargs),
            valid_fn=validate_format
        )

        return {
            "final_answer" : final_answer
        } 

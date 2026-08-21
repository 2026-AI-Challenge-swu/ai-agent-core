from src.ai_agent_core.graph.state import AgentState
from src.ai_agent_core.graph.nodes.base import BaseNode
from ai_common.utils.io import parse_str_to_json


class DecomposerNode(BaseNode):
    system_path = "./prompts/decomposer.system.md"
    user_path = "./prompts/decomposer.user.md"


    def __call__(self, state: AgentState) -> dict:
        user_input = {
            "query": state["query"]
        }

        system_prompt = self.llm.get_prompt(self.system_path)
        user_prompt = self.llm.get_prompt(self.user_path, **user_input)

        input = {
            "system_prompt": system_prompt,
            "user_prompt": user_prompt,
        }


        def validate_format(result):
            if not isinstance(result["sub_queries"], list):
                return False

            for i in result["sub_queries"]:
                if not isinstance(i.get("sub_query"), str)\
                    or not isinstance(i.get("intent"), str):
                    return False


            return True


                
        sub_queries = self._retry_invoke(
            input=input,
            execute_fn=self._get_dict_from_llm,
            valid_fn=validate_format
        )


        return {
            "sub_queries": [{"sub_query_id": idx,  **sub_query }for idx, sub_query in enumerate(sub_queries["sub_queries"])],
        }
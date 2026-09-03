from src.ai_agent_core.graph.state import AgentState
from src.ai_agent_core.graph.nodes.base import BaseNode
from ai_common.utils.build_text import build_portfolio_text, build_retirementPlan_text, build_metrics_text


class DecomposerNode(BaseNode):
    async def __call__(self, state: AgentState) -> dict:
        if state['mode'] == "chat":
            user_input = {
                "query": state["query"]
            }

        else:
            user_input = {
                "totalScore": state["userProfile"].totalScore,
                "type": state["userProfile"].type,
                "grade": state["userProfile"].grade,
                "nickname": state["userProfile"].nickname,
                "officialName": state["userProfile"].officialName,
                "description": state["userProfile"].description,
                "portfolio": build_portfolio_text(state["portfolio"]),
                "retirementPlan": build_retirementPlan_text(state["retirementPlan"]),
                "metrics": build_metrics_text(state["metrics"]),
            }

        system_path = f"./prompts/decomposer.{state['mode']}.system.md"
        user_path = f"./prompts/decomposer.{state['mode']}.user.md"

        system_prompt = self.llm.get_prompt(system_path)
        user_prompt = self.llm.get_prompt(user_path, **user_input)

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


                
        sub_queries = await self._retry_invoke(
            input=input,
            execute_fn=self._get_dict_from_llm,
            valid_fn=validate_format
        )


        return {
            "sub_queries": [{"sub_query_id": idx,  **sub_query }for idx, sub_query in enumerate(sub_queries["sub_queries"])],
        }
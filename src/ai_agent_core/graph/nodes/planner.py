from src.ai_agent_core.graph.state import WorkerState
from src.ai_agent_core.graph.nodes.base import BaseNode
from ai_common.utils.io import parse_str_to_json


class PlannerNode(BaseNode):
    system_path = "./prompts/planner.system.md"
    user_path = "./prompts/planner.user.md"


    def __call__(self, state: WorkerState) -> dict:
        user_input = {
            "sub_query": state["sub_query"]
        }

        system_prompt = self.llm.get_prompt(self.system_path)
        user_prompt = self.llm.get_prompt(self.user_path, **user_input)

        input = {
            "system_prompt": system_prompt,
            "user_prompt": user_prompt,
        }

        def get_dict_from_llm(input):
            raw_text = self.llm.call_gpt(**input)
            result = parse_str_to_json(raw_text)


            return result


        def validate_format(result):
            if not isinstance(result, dict):
                return False

            plan = result.get("plan")

            if not isinstance(plan, dict)\
                or not isinstance(plan.get("plan_id"), str)\
                or plan.get("status") not in {"READY", "NEED_MORE_INFO"}:
                return False

            # execution_steps
            execution_steps = plan.get("execution_steps")
            if not isinstance(execution_steps, list):
                return False

            for step in execution_steps:
                if not isinstance(step, dict)\
                    or not isinstance(step.get("step"), int)\
                    or not isinstance(step.get("tool"), str)\
                    or not isinstance(step.get("args"), dict)\
                    or not isinstance(step.get("output_variable"), str):
                    return False


            return True

        plan = self._retry_invoke(
            input=input,
            execute_fn=get_dict_from_llm,
            valid_fn=validate_format
        )
        return {
            "plan": plan["plan"],
        }
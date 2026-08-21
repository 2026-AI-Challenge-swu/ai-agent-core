from abc import ABC
from ai_common.utils.io import parse_str_to_json


class BaseNode(ABC):
    system_path: str
    user_path: str

    def __init__(self, app_state):
        self.logger = app_state.logger
        self.llm = app_state.llm


    def _get_dict_from_llm(self, input):
        raw_text = self.llm.call_gpt(**input)
        result = parse_str_to_json(raw_text)

        return result


    def _retry_invoke(self, input, execute_fn, valid_fn):
        for i in range(3):
            try:
                result = execute_fn(input)
                if valid_fn(result):
                    return result

                raise ValueError("Invalid result")

            except Exception as e:
                if i < 2:
                    self.logger.warning(
                        f"[Retry {i + 1}/3] error: {e}"
                    )
                else:
                    self.logger.warning(
                        f"[Retry Failed] error: {e}"
                    )

        return None
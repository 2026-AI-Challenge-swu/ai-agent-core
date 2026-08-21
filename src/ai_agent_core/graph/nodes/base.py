from abc import ABC


class BaseNode(ABC):
    system_path: str
    user_path: str

    def __init__(self, app_state):
        self.logger = app_state.logger
        self.llm = app_state.llm

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
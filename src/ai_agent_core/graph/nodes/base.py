import asyncio
from abc import ABC
from ai_common.utils.io import parse_str_to_json


class BaseNode(ABC):
    system_path: str
    user_path: str

    def __init__(self, app_state):
        self.logger = app_state.logger
        self.llm = app_state.llm


    async def _get_dict_from_llm(self, input):
        # self.llm.call_gpt는 동기(blocking) OpenAI 호출이라, 그냥 호출하면 이 요청이
        # 끝날 때까지 이벤트 루프 전체(다른 모든 요청 포함)가 멈춤 — 별도 스레드로 돌려서
        # 이벤트 루프가 그동안 다른 요청도 처리할 수 있게 함.
        raw_text = await asyncio.to_thread(self.llm.call_gpt, **input)
        result = parse_str_to_json(raw_text)

        return result


    async def _retry_invoke(self, input, execute_fn, valid_fn):
        for i in range(3):
            try:
                result = await execute_fn(input)
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
from src.ai_agent_core.graph.state import WorkerState
from src.ai_agent_core.graph.nodes.base import BaseNode


class GenerateAnswerNode(BaseNode):
    system_path = "./prompts/generate_answer.system.md"
    user_path = "./prompts/generate_answer.user.md"


    def _build_tool_result_text(self, tool_result):
        tool_result_text = []
        if tool_result:
            tool_result_text.append("- tool 실행 결과:")
            if tool_result["tool_name"] == "search_pension_rag":
                pass
            elif tool_result["tool_name"] == "search_pension_rag":
                pass
            elif tool_result["tool_name"] == "calculate_tax_credit":
                pass
            elif tool_result["tool_name"] == "ask_user_for_info":
                tool_result_text.append("주어진 정보가 부족하여 질문을 해결하기 위한 작업을 할 수 없습니다.")
                tool_result_text.append(tool_result["result"])

        return "".join(tool_result_text)
        


    async def __call__(self, state: WorkerState) -> dict:
        if state["intent"] == "reject":
            answer="요청하신 정보는 연금 상담 서비스 범위를 벗어나 안내가 어려운 점 양해 부탁드립니다."


        else:
            user_input = {
                "sub_query": state["sub_query"],
                "tool_result_text": self._build_tool_result_text(state["tool_result"])
            }
            answer=""


        return {
            "answer": answer,
            "worker_results": [
                {
                    "sub_query_id": state["sub_query_id"],
                    "query": state["sub_query"],
                    "plan": state.get("plan"),
                    "tool_result": state.get("tool_result"),
                    "answer": answer,
                }
            ],
        }

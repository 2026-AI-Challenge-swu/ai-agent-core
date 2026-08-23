from src.ai_agent_core.graph.state import WorkerState
from src.ai_agent_core.graph.nodes.base import BaseNode


class GenerateAnswerNode(BaseNode):
    system_path = "./prompts/generate_answer.system.md"
    user_path = "./prompts/generate_answer.user.md"


    def _format_rag_context(self, context_items):
        if not context_items:
            return "  (검색된 관련 문서 없음)"

        lines = []
        for item in context_items:
            lines.append(
                f"  - [{item['source']} p.{item['page']} / {item['category']} "
                f"/ score={item['rerank_score']:.3f}] {item['text']}"
            )
        return "\n".join(lines)

    def _build_tool_result_text(self, tool_result):
        tool_result_text = []
        if tool_result:
            tool_result_text.append("- tool 실행 결과:")
            for step_result in tool_result.values():
                tool_name = step_result.get("tool_name")
                result = step_result.get("result")

                if tool_name == "search_pension_rag":
                    tool_result_text.append(self._format_rag_context(result))
                elif tool_name == "calculate_tax_credit":
                    pass
                elif tool_name == "ask_user_for_info":
                    tool_result_text.append("주어진 정보가 부족하여 질문을 해결하기 위한 작업을 할 수 없습니다.")
                    tool_result_text.append(str(result))

        return "\n".join(tool_result_text)
        


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

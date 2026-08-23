from src.ai_agent_core.clients.rag_client import rag_client
from src.ai_agent_core.tools.registry import tool_registry


@tool_registry.register(name="search_pension_rag")
async def search_pension_rag(query: str):
    return await rag_client.search(query)

@tool_registry.register(name="calculate_tax_credit")
def calculate_tax_credit(pension_type: str, amount: int, annual_income: int):
    # 세액공제 계산 api 호출
    pass

@tool_registry.register(name="get_user_profile")
def get_user_profile(pension_type: str, session_id: str):
    # 보고서 관련 메타데이터 가져오기
    pass

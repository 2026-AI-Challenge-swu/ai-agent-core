import os

import httpx
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential


class RagClient:
    """ai-rag-engine의 /search API 호출 클라이언트"""

    def __init__(self, base_url: str | None = None, timeout: float = 60.0):
        self._base_url_override = base_url
        self.timeout = timeout

    @property
    def base_url(self) -> str:
        # load_dotenv()는 앱 startup 시점(lifespan)에 실행되므로,
        # 모듈 import 시점이 아니라 호출 시점에 환경 변수를 읽어야 함
        return self._base_url_override or os.environ.get("RAG_ENGINE_URL", "http://localhost:8001")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=0.5, max=4),
        retry=retry_if_exception_type((httpx.ConnectError, httpx.TimeoutException)),
        reraise=True,
    )
    async def search(self, query: str) -> list[dict]:
        async with httpx.AsyncClient(base_url=self.base_url, timeout=self.timeout) as client:
            response = await client.post("/search", json={"query": query})
            response.raise_for_status()
            return response.json()["context"]


rag_client = RagClient()

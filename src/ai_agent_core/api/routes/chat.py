from fastapi import APIRouter, Request
from ai_common.dto.chat import ChatRequest


router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)


@router.post("")
async def chat(
    request: Request,
    body: ChatRequest,
):
    logger = request.app.state.logger
    agent = request.app.state.agent

    session_id = body.session_id
    query = body.query
    logger.info("호출 완료")

    response = agent.run(
        query=query,
        session_id=session_id
    )

    return {
        "session_id": session_id,
        "query": query,
        "response": response
    }
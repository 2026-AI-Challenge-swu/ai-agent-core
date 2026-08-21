from fastapi import APIRouter, Request
import json
import asyncio
from ai_common.dto.chat import ChatRequest
from sse_starlette.sse import EventSourceResponse


router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)


@router.post("/default")
async def chat(
    request: Request,
    body: ChatRequest,
):
    logger = request.app.state.logger
    agent = request.app.state.agent

    session_id = body.session_id
    query = body.query
    logger.info("호출 완료")

    response = await agent.run(
        query=query,
        session_id=session_id
    )

    return {
        "session_id": session_id,
        "query": query,
        "response": response
    }


@router.post("/sse")
async def chat(
    request: Request,
    body: ChatRequest,
):
    logger = request.app.state.logger
    agent = request.app.state.agent

    session_id = body.session_id
    query = body.query
    logger.info(f"호출 완료 - session_id: {session_id}")

    async def event_generator():
        async for event in agent.stream_run(query=query, session_id=session_id):
            yield {
                "event": event.get("event"),  # SSE event 타입
                "data": json.dumps(event, ensure_ascii=False)  # SSE data 내용
            }

        # 최종 종료 알림 (필요 시)
        yield {
            "event": "close",
            "data": json.dumps({"status": "completed", "session_id": session_id})
        }

    return EventSourceResponse(event_generator())
from fastapi import APIRouter, Request
import json
from ai_common.dto.report import ReportRequest


router = APIRouter(
    prefix="/report",
    tags=["Report"],
)


@router.post("/default")
async def chat(
    request: Request,
    body: ReportRequest,
):
    logger = request.app.state.logger
    # agent = request.app.state.agent

    context = body.context
    logger.info("호출 완료")

    # response = await agent.run(
    #     context=context,
    # )

    return {
        "total_comment": "response",
        "road_map": [{
            "id": 0, 
            "time": "", 
            "todo": ""
            }],
        "counselling_points": [{
            "tendency": "", 
            "detail": ""
            }],
    }


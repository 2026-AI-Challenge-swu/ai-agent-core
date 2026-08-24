from fastapi import APIRouter, Request
import json
from ai_common.dto.report import ReportRequest


router = APIRouter(
    prefix="/report",
    tags=["Report"],
)


@router.post("")
async def report(
    request: Request,
    body: ReportRequest,
):
    logger = request.app.state.logger
    agent = request.app.state.agent

    userProfile = body.userProfile
    portfolio = body.portfolio
    retirementPlan = body.retirementPlan
    metrics = body.metrics
    logger.info("호출 완료")

    response = await agent.run(
        userProfile=userProfile,
        portfolio=portfolio,
        retirementPlan=retirementPlan,
        metrics=metrics,
        mode="report",
    )

    return response["final_answer"]


from fastapi import APIRouter, HTTPException, status

from app.schemas.report_schema import ResearchReportResponse
from app.services.report_service import get_research_report

router = APIRouter()


@router.get(
    "/{research_id}/report",
    response_model=ResearchReportResponse
)
def get_report(research_id: str):

    research = get_research_report(research_id)

    if research is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Research job not found."
        )

    if research["status"] != "completed":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Research is not completed yet. Current status: {research['status']}"
        )

    return ResearchReportResponse(
        research_id=research["research_id"],
        company=research["company"],
        ticker=research["ticker"],
        final_report=research["final_report"]
    )
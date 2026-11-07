from fastapi import APIRouter, BackgroundTasks, status,Query
from fastapi import HTTPException
from app.schemas.research_schema import (
    ResearchRequest,
    ResearchResponse,
    ResearchStatusResponse,
    ResearchHistoryItem
)

from app.services.research_service import (
    submit_research,
    execute_research,
    get_research_status,
    get_research_history
)


router = APIRouter()

@router.get(
    "/history",
    response_model=list[ResearchHistoryItem]
)
def research_history(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100)
):
    return get_research_history(
        skip=skip,
        limit=limit
    )
@router.post(
    "",
    response_model=ResearchResponse,
    status_code=status.HTTP_202_ACCEPTED
)
def create_research(
    request: ResearchRequest,
    background_tasks: BackgroundTasks
):

    # Create research job
    research_id = submit_research(
        company=request.company,
        ticker=request.ticker
    )

    # Execute CrewAI in the background
    background_tasks.add_task(
        execute_research,
        research_id,
        request.company.strip(),
        request.ticker.strip().upper()
    )

    return ResearchResponse(
        research_id=research_id,
        company=request.company,
        ticker=request.ticker.upper(),
        status="pending",
        message="Financial research started successfully."
    )

@router.get(
    "/{research_id}",
    response_model=ResearchStatusResponse
)
def research_status(research_id: str):

    research = get_research_status(research_id)

    if research is None:
        raise HTTPException(
            status_code=404,
            detail="Research job not found."
        )

    return research
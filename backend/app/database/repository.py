from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models import ResearchJob


def create_research_job(
    db: Session,
    company: str,
    ticker: str
):
    research = ResearchJob(
        research_id=str(uuid4()),
        company=company,
        ticker=ticker,
        status="pending"
    )

    db.add(research)
    db.commit()
    db.refresh(research)

    return research


def get_research_job(
    db: Session,
    research_id: str
):
    return db.get(ResearchJob, research_id)


def update_research_job(
    db: Session,
    research_id: str,
    status: str,
    final_report: str | None = None,
    error: str | None = None
):
    research = db.get(ResearchJob, research_id)

    if research is None:
        return None

    research.status = status
    research.final_report = final_report
    research.error = error

    db.commit()
    db.refresh(research)

    return research


def get_all_research_jobs(
    db: Session,
    skip: int = 0,
    limit: int = 20
):
    statement = (
        select(ResearchJob)
        .order_by(ResearchJob.created_at.desc())
        .offset(skip)
        .limit(limit)
    )

    return db.scalars(statement).all()
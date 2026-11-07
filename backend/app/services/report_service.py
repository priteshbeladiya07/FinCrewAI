
from sqlalchemy.orm import Session

from app.database.connection import SessionLocal
from app.database.repository import get_research_job


def get_research_report(research_id: str):
    """
    Retrieve the final consolidated research report
    from PostgreSQL.
    """

    db: Session = SessionLocal()

    try:
        research = get_research_job(
            db=db,
            research_id=research_id
        )

        if research is None:
            return None

        return {
            "research_id": research.research_id,
            "company": research.company,
            "ticker": research.ticker,
            "status": research.status,
            "final_report": research.final_report,
            "error": research.error,
            "created_at": research.created_at
        }

    finally:
        db.close()

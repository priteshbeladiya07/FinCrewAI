
import json

from sqlalchemy.orm import Session

from app.schemas.report_schema import InvestmentResearchReport
from app.crews.research_flow import run_financial_research
from app.database.connection import SessionLocal
from app.database.repository import (
    create_research_job,
    get_research_job,
    get_all_research_jobs,
    update_research_job
)
from app.utils.logger import get_logger
from app.utils.validators import (
    normalize_company_name,
    normalize_ticker
)

logger = get_logger(__name__)


def get_research_history(skip: int = 0, limit: int = 20):
    """
    Retrieve saved research jobs from PostgreSQL.
    """

    db: Session = SessionLocal()

    try:
        research_jobs = get_all_research_jobs(
            db=db,
            skip=skip,
            limit=limit
        )

        return [
            {
                "research_id": research.research_id,
                "company": research.company,
                "ticker": research.ticker,
                "status": research.status,
                "created_at": research.created_at,
                "updated_at": research.updated_at
            }
            for research in research_jobs
        ]

    finally:
        db.close()


def execute_research(
    research_id: str,
    company: str,
    ticker: str
):
    """
    Execute CrewAI research in the background.
    Validate and store only the final consolidated report.
    """

    db: Session = SessionLocal()

    try:
        # Check whether the research job exists.
        research = get_research_job(db, research_id)

        if research is None:
            logger.error(
                "Research job %s was not found.",
                research_id
            )
            return

        # Mark the job as processing.
        update_research_job(
            db=db,
            research_id=research_id,
            status="processing",
            final_report=None,
            error=None
        )

        logger.info(
            "Starting six-agent research for %s (%s)",
            company,
            ticker
        )

        # Execute the CrewAI workflow.
        result = run_financial_research(
            company=company,
            ticker=ticker
        )

        # Extract raw final-agent output.
        raw_report = getattr(result, "raw", None)

        if not raw_report or not raw_report.strip():
            raise RuntimeError(
                "CrewAI returned an empty final report."
            )

        # Extract the JSON object from the response.
        start = raw_report.find("{")
        end = raw_report.rfind("}") + 1

        if start == -1 or end <= start:
            raise ValueError(
                "Final agent did not return a valid JSON object."
            )

        json_text = raw_report[start:end]

        # Check whether the output is valid JSON.
        try:
            report_data = json.loads(json_text)
        except json.JSONDecodeError as error:
            raise ValueError(
                f"Final report contains invalid JSON: {error}"
            ) from error

        # Validate the report against the Pydantic schema.
        structured_report = InvestmentResearchReport.model_validate(
            report_data
        )

        # Serialize the validated report for PostgreSQL.
        final_report_json = structured_report.model_dump_json(
            indent=2
        )

        # Save only the validated final consolidated report.
        update_research_job(
            db=db,
            research_id=research_id,
            status="completed",
            final_report=final_report_json,
            error=None
        )

        logger.info(
            "Research completed successfully. Research ID: %s",
            research_id
        )

    except Exception as error:

        # Roll back any unfinished database transaction.
        db.rollback()

        try:
            update_research_job(
                db=db,
                research_id=research_id,
                status="failed",
                final_report=None,
                error=str(error)
            )

        except Exception:
            db.rollback()

            logger.exception(
                "Could not update failed research job: %s",
                research_id
            )

        logger.exception(
            "Research execution failed. Research ID: %s",
            research_id
        )

    finally:
        db.close()


def get_research_status(research_id: str):
    """
    Retrieve research job details from PostgreSQL.
    """

    db: Session = SessionLocal()

    try:
        research = get_research_job(db, research_id)

        if research is None:
            logger.warning(
                "Research job not found: %s",
                research_id
            )
            return None

        return {
            "research_id": research.research_id,
            "company": research.company,
            "ticker": research.ticker,
            "status": research.status,
            "error": research.error,
            "created_at": research.created_at,
            "updated_at": research.updated_at
        }

    finally:
        db.close()


def get_research_report(research_id: str):
    """
    Retrieve the final consolidated research report from PostgreSQL.
    """

    db: Session = SessionLocal()

    try:
        research = get_research_job(db, research_id)

        if research is None:
            return None

        return {
            "research_id": research.research_id,
            "company": research.company,
            "ticker": research.ticker,
            "status": research.status,
            "final_report": research.final_report
        }

    finally:
        db.close()


def submit_research(
    company: str,
    ticker: str
):
    """
    Validate input and create a new research job in PostgreSQL.
    """

    company = normalize_company_name(company)
    ticker = normalize_ticker(ticker)

    db: Session = SessionLocal()

    try:
        research = create_research_job(
            db=db,
            company=company,
            ticker=ticker
        )

        logger.info(
            "Research job created: %s | %s (%s)",
            research.research_id,
            company,
            ticker
        )

        return research.research_id

    except Exception:
        db.rollback()

        logger.exception(
            "Failed to create research job for %s (%s)",
            company,
            ticker
        )
        raise

    finally:
        db.close()

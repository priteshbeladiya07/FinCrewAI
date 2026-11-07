
import crewai.llms.cache as crewai_cache

crewai_cache.mark_cache_breakpoint = lambda message: message

from app.crews.financial_research_crew import (
    create_financial_research_crew
)


def run_financial_research(company: str, ticker: str):
    """
    Execute the complete six-agent financial research system.
    """

    if not company or not company.strip():
        raise ValueError("Company name cannot be empty.")

    if not ticker or not ticker.strip():
        raise ValueError("Ticker symbol cannot be empty.")

    company = company.strip()
    ticker = ticker.strip().upper()

    crew = create_financial_research_crew()

    print("\n" + "=" * 65)
    print("STARTING SIX-AGENT FINANCIAL RESEARCH SYSTEM")
    print("=" * 65)

    print(f"Company : {company}")
    print(f"Ticker  : {ticker}")

    result = crew.kickoff(
        inputs={
            "company": company,
            "ticker": ticker
        }
    )

    print("\nCREW OUTPUT DIAGNOSTICS")
    print("Result type:", type(result))
    print("Pydantic output:", getattr(result, "pydantic", None))
    print("Raw output:", getattr(result, "raw", None))

    return result

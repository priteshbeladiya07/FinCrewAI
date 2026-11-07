
import json

from crewai import Task

from app.agents.investment_agent import investment_agent
from app.schemas.report_schema import InvestmentResearchReport


REPORT_SCHEMA = json.dumps(
    InvestmentResearchReport.model_json_schema(),
    indent=2
)

investment_task = Task(
    description="""
    Prepare a final investment research assessment for
    {company} ({ticker}).

    INPUT REPORTS

    SENTIMENT ANALYSIS:
    {sentiment_report}

    RISK ANALYSIS:
    {risk_report}

    REQUIREMENTS

    - Use only the supplied reports.
    - Analyze the listed company represented by the supplied ticker.
    - Do not combine financial results from unrelated subsidiaries.
    - Flag company-name and ticker mismatches.
    - Never invent financial figures, news or market data.
    - Distinguish facts from interpretations.
    - Select up to three material positive factors.
    - Select up to three material negative factors.
    - Identify meaningful competing signals.
    - Assess short-term, medium-term and long-term outlooks.
    - Identify up to five monitoring points.
    - Identify important information gaps.
    - Keep the executive summary concise.
    - Avoid repeating evidence across fields.
    - Ensure all assessments are internally consistent.

    OUTPUT FORMAT — IMPORTANT

    Return ONLY a valid JSON object.

    Do not return:
    - Markdown code fences
    - Python object representations
    - Explanatory text before or after the JSON
    - Comments inside the JSON

    Follow this JSON schema exactly:
    """ + REPORT_SCHEMA,

    expected_output=(
        "A valid JSON object matching the supplied "
        "InvestmentResearchReport JSON schema."
    ),

    agent=investment_agent
)


from typing import Literal

from pydantic import BaseModel, Field


InvestmentOutlook = Literal[
    "Bullish",
    "Moderately Bullish",
    "Neutral",
    "Moderately Bearish",
    "Bearish",
]

ConfidenceLevel = Literal["High", "Moderate", "Low"]
RiskLevel = Literal["High", "Moderate", "Low"]

HorizonOutlook = Literal[
    "Bullish",
    "Moderately Bullish",
    "Neutral",
    "Moderately Bearish",
    "Bearish",
    "Insufficient evidence",
]


class InvestmentFactor(BaseModel):
    title: str = Field(description="Short name of the investment factor")
    evidence: str = Field(description="Evidence from the supplied reports")
    significance: str = Field(
        description="Why this factor matters to the investment assessment"
    )
    time_horizon: str | None = None


class TimeHorizonAssessment(BaseModel):
    outlook: HorizonOutlook
    supporting_evidence: str
    main_risk: str


class AgentConflict(BaseModel):
    topic: str
    positive_evidence: str
    opposing_evidence: str
    investment_significance: str


class SentimentRiskAssessment(BaseModel):
    positive_signals: list[str] = Field(default_factory=list, max_length=3)
    key_risks: list[str] = Field(default_factory=list, max_length=3)
    competing_signals: list[AgentConflict] = Field(default_factory=list)
    consistency_summary: str


class TimeHorizonOutlook(BaseModel):
    short_term: TimeHorizonAssessment
    medium_term: TimeHorizonAssessment
    long_term: TimeHorizonAssessment


class DetailedAnalysis(BaseModel):
    fundamental: str
    technical: str
    news: str
    sentiment: str
    risk: str


class InvestmentResearchReport(BaseModel):
    """Structured output produced by the final CrewAI investment agent."""

    company: str
    ticker: str

    overall_outlook: InvestmentOutlook
    confidence: ConfidenceLevel
    risk_level: RiskLevel

    executive_summary: str = Field(
        description="Concise investment summary, maximum approximately 100 words"
    )
    outlook_justification: str

    positive_factors: list[InvestmentFactor] = Field(max_length=3)
    negative_factors: list[InvestmentFactor] = Field(max_length=3)

    sentiment_risk: SentimentRiskAssessment

    time_horizon: TimeHorizonOutlook

    monitoring_points: list[str] = Field(max_length=5)

    detailed_analysis: DetailedAnalysis

    limitations: list[str] = Field(default_factory=list, max_length=5)

    conclusion: str

    disclaimer: str


# API response wrapper.
# Keep this existing response compatible until we integrate
# structured JSON storage in the next step.
class ResearchReportResponse(BaseModel):
    research_id: str
    company: str
    ticker: str
    final_report: str

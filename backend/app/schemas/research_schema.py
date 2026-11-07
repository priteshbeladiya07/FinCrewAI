from typing import Literal

from pydantic import BaseModel, Field, field_validator

from app.utils.validators import (
    normalize_company_name,
    normalize_ticker
)
from datetime import datetime


class ResearchHistoryItem(BaseModel):

    research_id: str
    company: str
    ticker: str

    status: Literal[
        "pending",
        "processing",
        "completed",
        "failed"
    ]

    created_at: datetime
    updated_at: datetime

class ResearchRequest(BaseModel):

    company: str = Field(
        min_length=2,
        max_length=100,
        description="Company name"
    )

    ticker: str = Field(
        min_length=1,
        max_length=20,
        description="Stock ticker symbol"
    )

    @field_validator("company")
    @classmethod
    def validate_company(cls, value):
        return normalize_company_name(value)

    @field_validator("ticker")
    @classmethod
    def validate_ticker(cls, value):
        return normalize_ticker(value)


class ResearchResponse(BaseModel):

    research_id: str
    company: str
    ticker: str
    status: str
    message: str


class ResearchStatusResponse(BaseModel):

    research_id: str
    company: str
    ticker: str

    status: Literal[
        "pending",
        "processing",
        "completed",
        "failed"
    ]

    error: str | None = None
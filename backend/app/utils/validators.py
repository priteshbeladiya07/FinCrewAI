import re


TICKER_PATTERN = re.compile(
    r"^[A-Z0-9^][A-Z0-9.&^=_-]{0,19}$"
)


def normalize_company_name(company: str) -> str:
    """
    Validate and normalize a company name.
    """

    if not isinstance(company, str):
        raise ValueError("Company name must be a string.")

    company = " ".join(company.split())

    if not company:
        raise ValueError("Company name cannot be empty.")

    if len(company) < 2:
        raise ValueError(
            "Company name must contain at least 2 characters."
        )

    if len(company) > 100:
        raise ValueError(
            "Company name cannot exceed 100 characters."
        )

    return company


def normalize_ticker(ticker: str) -> str:
    """
    Validate and normalize a stock ticker symbol.
    """

    if not isinstance(ticker, str):
        raise ValueError("Ticker must be a string.")

    ticker = ticker.strip().upper()

    if not ticker:
        raise ValueError("Ticker symbol cannot be empty.")

    if len(ticker) > 20:
        raise ValueError(
            "Ticker symbol cannot exceed 20 characters."
        )

    if not TICKER_PATTERN.fullmatch(ticker):
        raise ValueError(
            "Ticker symbol contains invalid characters."
        )

    return ticker
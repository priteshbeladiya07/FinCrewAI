from pydantic import BaseModel


class StockQuoteResponse(BaseModel):
    symbol: str
    market_date: str
    latest_price: float
    previous_close: float | None = None
    change: float | None = None
    change_percent: float | None = None
    open: float | None = None
    high: float | None = None
    low: float | None = None
    volume: int | None = None
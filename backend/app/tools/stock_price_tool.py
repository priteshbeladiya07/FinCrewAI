
import json
from datetime import datetime, timezone
from app.services.stock_service import get_stock_quote,get_historical_stock_data


import yfinance as yf
from crewai.tools import tool


@tool("Stock Price Tool")
def stock_price_tool(symbol: str) -> str:
    """
    Retrieve the latest available daily stock quote
    for a given stock ticker symbol.
    """

    try:
        stock_data = get_stock_quote(symbol)

        return json.dumps(stock_data, indent=2)

    except LookupError as error:
        return f"Stock data unavailable: {error}"

    except Exception as error:
        return f"Unable to retrieve stock data: {error}"

@tool("Stock Price Data Tool")
def stock_price_data_tool(ticker: str) -> str:
    """
    Fetch historical daily stock OHLCV data for a ticker.

    Returns historical dates, open, high, low, close, volume,
    currency, exchange timezone, latest trading session,
    and data quality information.
    """

    try:
        ticker = ticker.strip().upper()

        if not ticker:
            return json.dumps({
                "error": "Ticker cannot be empty."
            })

        stock = yf.Ticker(ticker)

        # Two years of data provides enough history for SMA 200.
        history = stock.history(
            period="2y",
            interval="1d",
            auto_adjust=True,
            actions=False
        )

        if history.empty:
            return json.dumps({
                "error": f"No historical data found for {ticker}."
            })

        history = history.dropna(
            subset=["Open", "High", "Low", "Close"]
        )

        historical_data = []

        for date, row in history.iterrows():
            historical_data.append({
                "date": date.strftime("%Y-%m-%d"),
                "open": round(float(row["Open"]), 4),
                "high": round(float(row["High"]), 4),
                "low": round(float(row["Low"]), 4),
                "close": round(float(row["Close"]), 4),
                "volume": int(row["Volume"])
                if row["Volume"] is not None else 0
            })

        currency = None
        exchange_timezone = None
        warnings = []

        try:
            currency = stock.fast_info.get("currency")
        except Exception:
            warnings.append("Currency metadata unavailable.")

        try:
            exchange_timezone = stock.fast_info.get(
                "timezone"
            )
        except Exception:
            warnings.append("Exchange timezone unavailable.")

        if len(historical_data) < 200:
            warnings.append(
                "Fewer than 200 trading sessions are available. "
                "SMA 200 may not be available."
            )

        latest = historical_data[-1]

        result = {
            "ticker": ticker,
            "currency": currency,
            "exchange_timezone": exchange_timezone,
            "latest_session": latest["date"],
            "latest_bar_status": "latest_available_daily_bar",
            "historical_sessions": len(historical_data),
            "historical_data": historical_data,
            "data_quality": (
                "sufficient_for_sma_200"
                if len(historical_data) >= 200
                else "limited_history"
            ),
            "warnings": warnings,
            "retrieved_at_utc": datetime.now(
                timezone.utc
            ).isoformat()
        }

        return json.dumps(
            result,
            indent=2,
            ensure_ascii=False,
            allow_nan=False
        )

    except Exception as error:
        return json.dumps({
            "error_type": type(error).__name__,
            "error": str(error),
            "ticker": ticker
        })


import json

from crewai.tools import tool

from app.tools.stock_price_tool import stock_price_tool
from app.tools.technical_indicator_tool import technical_indicator_tool


@tool("Technical Analysis Data Tool")
def technical_analysis_data_tool(ticker: str) -> str:
    """
    Fetch stock market data and calculate technical indicators.

    Internally executes:
    1. Stock Price Tool
    2. Technical Indicator Tool

    Returns compact technical analysis JSON without
    exposing the complete historical OHLCV dataset to the LLM.
    """

    try:
        ticker = ticker.strip().upper()

        if not ticker:
            return json.dumps({
                "status": "error",
                "error": "Ticker cannot be empty."
            })

        # Step 1: Fetch historical market data.
        price_result = stock_price_tool.run(
            ticker=ticker
        )

        market_data = json.loads(price_result)

        if market_data.get("error"):
            return json.dumps({
                "status": "error",
                "stage": "stock_price_tool",
                "error": market_data["error"]
            })

        # Step 2: Calculate technical indicators.
        indicator_result = technical_indicator_tool.run(
            market_data_json=price_result
        )

        indicator_data = json.loads(indicator_result)

        if indicator_data.get("error"):
            return json.dumps({
                "status": "error",
                "stage": "technical_indicator_tool",
                "error": indicator_data["error"]
            })

        # Step 3: Attach relevant market-data metadata.
        indicator_data["status"] = "success"

        indicator_data["market_data_metadata"] = {
            "currency": market_data.get("currency"),
            "exchange_timezone": market_data.get(
                "exchange_timezone"
            ),
            "latest_session": market_data.get(
                "latest_session"
            ),
            "latest_bar_status": market_data.get(
                "latest_bar_status"
            ),
            "historical_sessions": len(
                market_data.get("historical_data", [])
            ),
            "data_quality": market_data.get(
                "data_quality"
            ),
            "warnings": market_data.get("warnings", []),
            "retrieved_at_utc": market_data.get(
                "retrieved_at_utc"
            )
        }

        return json.dumps(
            indicator_data,
            indent=2,
            ensure_ascii=False,
            allow_nan=False
        )

    except Exception as error:
        return json.dumps({
            "status": "error",
            "ticker": ticker,
            "error_type": type(error).__name__,
            "error": str(error)
        })

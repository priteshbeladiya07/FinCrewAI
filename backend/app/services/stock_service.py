import math
from datetime import datetime, timezone

import yfinance as yf

from app.utils.logger import get_logger
from app.utils.validators import normalize_ticker


logger = get_logger(__name__)


def get_number(row, column):
    """
    Safely extract a finite numeric value from a stock-data row.
    """

    if row is None:
        return None

    try:
        value = float(row[column])

        if not math.isfinite(value):
            return None

        return value

    except (TypeError, ValueError, KeyError, IndexError):
        return None


def get_stock_quote(symbol: str) -> dict:
    """
    Retrieve the latest available daily stock quote.

    Returns:
        Latest price, previous close, price change,
        percentage change, OHLC and volume.
    """

    symbol = normalize_ticker(symbol)

    logger.info("Fetching stock quote for %s", symbol)

    try:
        ticker = yf.Ticker(symbol)

        history = ticker.history(
            period="5d",
            interval="1d",
            auto_adjust=False
        )

        if history.empty:
            raise LookupError(
                f"No stock data found for {symbol}."
            )

        latest = history.iloc[-1]

        previous = (
            history.iloc[-2]
            if len(history) > 1
            else None
        )

        latest_price = get_number(latest, "Close")

        if latest_price is None:
            raise LookupError(
                f"Latest closing price unavailable for {symbol}."
            )

        previous_close = get_number(previous, "Close")

        change = None
        change_percent = None

        if previous_close is not None and previous_close != 0:

            change = latest_price - previous_close

            change_percent = (
                change / previous_close
            ) * 100

        volume = get_number(latest, "Volume")

        result = {
            "symbol": symbol,
            "market_date": history.index[-1].date().isoformat(),
            "latest_price": latest_price,
            "previous_close": previous_close,
            "change": change,
            "change_percent": change_percent,
            "open": get_number(latest, "Open"),
            "high": get_number(latest, "High"),
            "low": get_number(latest, "Low"),
            "volume": int(volume) if volume is not None else None
        }

        logger.info(
            "Stock quote retrieved successfully for %s",
            symbol
        )

        return result

    except LookupError:
        logger.warning(
            "Stock quote unavailable for %s",
            symbol
        )
        raise

    except Exception:
        logger.exception(
            "Failed to retrieve stock quote for %s",
            symbol
        )
        raise


def get_historical_stock_data(ticker: str) -> dict:
    """
    Retrieve two years of historical daily OHLCV data.

    Useful for technical indicators such as:
        - SMA 50
        - SMA 200
        - Moving averages
        - Price trends
        - Trading volume analysis
    """

    ticker = normalize_ticker(ticker)

    logger.info(
        "Fetching historical stock data for %s",
        ticker
    )

    try:
        stock = yf.Ticker(ticker)

        history = stock.history(
            period="2y",
            interval="1d",
            auto_adjust=True,
            actions=False
        )

        if history.empty:
            raise LookupError(
                f"No historical data found for {ticker}."
            )

        history = history.dropna(
            subset=["Open", "High", "Low", "Close"]
        )

        historical_data = []

        for date, row in history.iterrows():

            open_price = get_number(row, "Open")
            high_price = get_number(row, "High")
            low_price = get_number(row, "Low")
            close_price = get_number(row, "Close")
            volume_value = get_number(row, "Volume")

            if None in (
                open_price,
                high_price,
                low_price,
                close_price
            ):
                continue

            historical_data.append({
                "date": date.strftime("%Y-%m-%d"),
                "open": round(open_price, 4),
                "high": round(high_price, 4),
                "low": round(low_price, 4),
                "close": round(close_price, 4),
                "volume": (
                    int(volume_value)
                    if volume_value is not None and volume_value >= 0
                    else 0
                )
            })

        if not historical_data:
            raise LookupError(
                f"No valid historical sessions found for {ticker}."
            )

        # Retrieve market metadata
        currency = None
        exchange_timezone = None
        warnings = []

        try:
            currency = stock.fast_info.get("currency")
        except Exception:
            warnings.append("Currency metadata unavailable.")

        try:
            exchange_timezone = stock.fast_info.get("timezone")
        except Exception:
            warnings.append("Exchange timezone unavailable.")

        latest = historical_data[-1]

        # Check whether sufficient data exists for SMA 200
        if len(historical_data) < 200:
            warnings.append(
                "Fewer than 200 trading sessions available. "
                "SMA 200 may not be available."
            )

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

        logger.info(
            "Retrieved %d historical sessions for %s",
            len(historical_data),
            ticker
        )

        return result

    except LookupError:
        logger.warning(
            "Historical stock data unavailable for %s",
            ticker
        )
        raise

    except Exception:
        logger.exception(
            "Historical stock data retrieval failed for %s",
            ticker
        )
        raise

import json

import numpy as np
import pandas as pd

from crewai.tools import tool


@tool("Technical Indicator Calculation Tool")
def technical_indicator_tool(market_data_json: str) -> str:
    """
    Calculate technical indicators from historical OHLCV JSON.

    Calculates SMA 20/50/200, RSI 14, MACD, MACD signal,
    MACD histogram, volume ratio, trend signals, and
    approximate support and resistance levels.

    Requires historical_data containing date, open, high,
    low, close and volume.
    """

    try:
        market_data = json.loads(market_data_json)

        if market_data.get("error"):
            return json.dumps({
                "error": market_data["error"]
            })

        records = market_data.get("historical_data", [])

        if not records:
            return json.dumps({
                "error": "Historical market data is empty."
            })

        df = pd.DataFrame(records)

        required_columns = [
            "date", "open", "high",
            "low", "close", "volume"
        ]

        missing = [
            column for column in required_columns
            if column not in df.columns
        ]

        if missing:
            return json.dumps({
                "error": f"Missing columns: {missing}"
            })

        df["date"] = pd.to_datetime(df["date"])

        numeric_columns = [
            "open", "high", "low", "close", "volume"
        ]

        for column in numeric_columns:
            df[column] = pd.to_numeric(
                df[column],
                errors="coerce"
            )

        df = (
            df.dropna(subset=["close"])
            .sort_values("date")
            .drop_duplicates(subset=["date"])
            .reset_index(drop=True)
        )

        if len(df) < 30:
            return json.dumps({
                "error": (
                    "At least 30 valid trading sessions "
                    "are required for basic technical analysis."
                ),
                "available_sessions": len(df)
            })

        close = df["close"]
        volume = df["volume"]

        # Moving averages
        df["sma_20"] = close.rolling(20).mean()
        df["sma_50"] = close.rolling(50).mean()
        df["sma_200"] = close.rolling(200).mean()

        # RSI 14 using Wilder-style exponential smoothing
        delta = close.diff()

        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)

        avg_gain = gain.ewm(
            alpha=1 / 14,
            min_periods=14,
            adjust=False
        ).mean()

        avg_loss = loss.ewm(
            alpha=1 / 14,
            min_periods=14,
            adjust=False
        ).mean()

        rs = avg_gain / avg_loss.replace(0, np.nan)

        df["rsi_14"] = 100 - (
            100 / (1 + rs)
        )

        # Handle zero-loss cases.
        df.loc[
            (avg_loss == 0) & (avg_gain > 0),
            "rsi_14"
        ] = 100

        df.loc[
            (avg_loss == 0) & (avg_gain == 0),
            "rsi_14"
        ] = 50

        # MACD: 12, 26, 9
        ema_12 = close.ewm(
            span=12,
            adjust=False
        ).mean()

        ema_26 = close.ewm(
            span=26,
            adjust=False
        ).mean()

        df["macd"] = ema_12 - ema_26

        df["macd_signal"] = df["macd"].ewm(
            span=9,
            adjust=False
        ).mean()

        df["macd_histogram"] = (
            df["macd"] - df["macd_signal"]
        )

        # Volume analysis
        df["average_volume_20"] = volume.rolling(
            20
        ).mean()

        df["volume_ratio"] = (
            volume / df["average_volume_20"].replace(
                0, np.nan
            )
        )

        latest = df.iloc[-1]

        def safe_float(value):
            if pd.isna(value):
                return None
            return round(float(value), 4)

        current_price = safe_float(latest["close"])

        if current_price is None:
            return json.dumps({
                "error": "Latest closing price is unavailable."
            })

        sma_20 = safe_float(latest["sma_20"])
        sma_50 = safe_float(latest["sma_50"])
        sma_200 = safe_float(latest["sma_200"])

        rsi = safe_float(latest["rsi_14"])
        macd = safe_float(latest["macd"])
        macd_signal = safe_float(latest["macd_signal"])
        macd_histogram = safe_float(
            latest["macd_histogram"]
        )

        average_volume = safe_float(
            latest["average_volume_20"]
        )

        volume_ratio = safe_float(
            latest["volume_ratio"]
        )

        # RSI interpretation
        if rsi is None:
            rsi_signal = "Unavailable"
        elif rsi >= 70:
            rsi_signal = "Overbought"
        elif rsi <= 30:
            rsi_signal = "Oversold"
        else:
            rsi_signal = "Neutral"

        # MACD interpretation
        if macd is None or macd_signal is None:
            macd_signal_text = "Unavailable"
        elif macd > macd_signal:
            macd_signal_text = "Bullish"
        else:
            macd_signal_text = "Bearish"

        # Moving-average interpretation
        def moving_average_signal(price, average):
            if average is None:
                return "Unavailable"
            return (
                "Bullish"
                if price > average
                else "Bearish"
            )

        sma_signals = {
            "sma_20": moving_average_signal(
                current_price, sma_20
            ),
            "sma_50": moving_average_signal(
                current_price, sma_50
            ),
            "sma_200": moving_average_signal(
                current_price, sma_200
            )
        }

        # Trend classifications
        short_term = (
            "Bullish"
            if sma_20 is not None and current_price > sma_20
            else "Bearish"
            if sma_20 is not None
            else "Unavailable"
        )

        medium_term = (
            "Bullish"
            if sma_50 is not None and current_price > sma_50
            else "Bearish"
            if sma_50 is not None
            else "Unavailable"
        )

        long_term = (
            "Bullish"
            if sma_200 is not None and current_price > sma_200
            else "Bearish"
            if sma_200 is not None
            else "Unavailable"
        )

        available_trends = [
            trend for trend in [
                short_term,
                medium_term,
                long_term
            ]
            if trend != "Unavailable"
        ]

        bullish_count = available_trends.count("Bullish")
        bearish_count = available_trends.count("Bearish")

        if bullish_count == len(available_trends):
            overall_trend = "Bullish"
        elif bearish_count == len(available_trends):
            overall_trend = "Bearish"
        else:
            overall_trend = "Mixed/Sideways"

        # Approximate support and resistance:
        # Lowest low and highest high in the last 20 sessions.
        recent_data = df.tail(20)

        support = safe_float(
            recent_data["low"].min()
        )

        resistance = safe_float(
            recent_data["high"].max()
        )

        warnings = []

        if sma_200 is None:
            warnings.append(
                "SMA 200 unavailable due to insufficient history."
            )

        if rsi is None:
            warnings.append("RSI unavailable.")

        if volume_ratio is None:
            warnings.append("Volume ratio unavailable.")

        result = {
            "ticker": market_data.get("ticker"),
            "latest_session": latest["date"].strftime(
                "%Y-%m-%d"
            ),
            "current_price": current_price,

            "moving_averages": {
                "sma_20": sma_20,
                "sma_50": sma_50,
                "sma_200": sma_200,
                "signals": sma_signals
            },

            "momentum": {
                "rsi_14": rsi,
                "rsi_signal": rsi_signal,
                "macd": macd,
                "macd_signal": macd_signal,
                "macd_histogram": macd_histogram,
                "macd_interpretation": macd_signal_text
            },

            "volume_analysis": {
                "latest_volume": int(latest["volume"]),
                "average_volume_20": average_volume,
                "volume_ratio": volume_ratio
            },

            "trend_analysis": {
                "short_term": short_term,
                "medium_term": medium_term,
                "long_term": long_term,
                "overall_trend": overall_trend,
                "bullish_signals": bullish_count,
                "bearish_signals": bearish_count,
                "available_trend_signals": len(
                    available_trends
                )
            },

            "support_resistance": {
                "support_20_session": support,
                "resistance_20_session": resistance,
                "method": (
                    "Lowest low and highest high "
                    "over the last 20 sessions"
                )
            },

            "data_quality": {
                "historical_sessions": len(df),
                "sma_200_available": sma_200 is not None,
                "warnings": warnings
            }
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
            "error": str(error)
        })

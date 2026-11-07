
from crewai import Task

from app.agents.technical_agent import technical_agent

from app.tools.technical_analysis_data_tool import (
    technical_analysis_data_tool
)


technical_task = Task(
    description="""
    Conduct a comprehensive technical analysis of {company}
    using the ticker symbol {ticker}.

    Your objective is to evaluate historical price action,
    market trends, momentum, volume, and potential support
    and resistance levels.

    ==================================================
    TOOL EXECUTION
    ==================================================

    1. Call the Technical Analysis Data Tool exactly once
       using the ticker symbol {ticker}.

    2. The tool internally:
       - Fetches historical stock market data.
       - Calculates technical indicators.
       - Identifies market trends.
       - Calculates support and resistance levels.
       - Generates a rule-based technical score.

    3. Use the returned JSON as the authoritative source
       for all calculated technical indicators.

    4. Check the tool response status.

    5. If status is "error", clearly report the failure.
       Do not invent or estimate missing technical data.

    ==================================================
    1. PRICE ACTION ANALYSIS
    ==================================================

    Examine:
    - Latest closing price.
    - Previous closing price.
    - Daily percentage change.
    - Latest available trading date.
    - Exchange timezone.
    - Latest market bar status.

    Distinguish a single-day price movement from
    the broader market trend.

    ==================================================
    2. MOVING AVERAGE ANALYSIS
    ==================================================

    Examine:
    - SMA 20, SMA 50 and SMA 200.
    - EMA 20 and EMA 50.
    - Moving-average alignment.
    - Current price positions relative to each SMA.

    Interpret:
    - Price above an SMA as positive positioning.
    - Price below an SMA as negative positioning.
    - SMA 20 above SMA 50 as a positive shorter-term
      moving-average relationship.
    - SMA 20 below SMA 50 as a negative shorter-term
      moving-average relationship.
    - SMA 20 > SMA 50 > SMA 200 as bullish alignment.
    - SMA 20 < SMA 50 < SMA 200 as bearish alignment.

    Do not confuse price positioning with
    overall moving-average alignment.

    ==================================================
    3. MOMENTUM ANALYSIS
    ==================================================

    Analyze RSI (14):

    - RSI >= 70: Traditional overbought zone.
    - RSI <= 30: Traditional oversold zone.
    - RSI between 50 and 70: Positive momentum.
    - RSI between 30 and below 50: Weaker momentum.

    Analyze MACD:
    - MACD value.
    - MACD signal line.
    - MACD histogram.
    - Bullish or bearish interpretation.

    MACD above its signal line indicates bullish
    momentum relative to the signal line.

    Do not treat RSI or MACD as guaranteed
    buy or sell signals.

    ==================================================
    4. VOLUME ANALYSIS
    ==================================================

    Examine:
    - Latest trading volume.
    - Previous 20-session average volume.
    - Volume ratio.
    - Volume interpretation.

    Interpret:
    - Ratio >= 1.2: Significantly above average.
    - Ratio <= 0.8: Below average.
    - Between these levels: Near average.

    Near-average volume does not provide strong
    confirmation of a price movement.

    Low volume does not automatically confirm
    a bearish trend.

    ==================================================
    5. TREND ANALYSIS
    ==================================================

    Examine the tool's classifications:

    - Short-term trend.
    - Medium-term trend.
    - Long-term trend.
    - Overall trend.

    Explain the methodology and identify agreement
    or disagreement between different time horizons.

    Keep short-term momentum separate from
    medium-term and long-term market structure.

    ==================================================
    6. SUPPORT AND RESISTANCE
    ==================================================

    Analyze the support and resistance levels
    returned by the tool.

    Explain:
    - Potential support levels.
    - Potential resistance levels.
    - Their relationship to the latest closing price.
    - The method used to identify them.

    These are potential price levels, not guaranteed
    support or resistance zones.

    Do not invent additional levels.

    ==================================================
    7. TECHNICAL SCORE
    ==================================================

    Examine:
    - Technical score.
    - Maximum absolute score.
    - Signal classification.
    - Supporting reasons.

    Explain that the score is a rule-based heuristic,
    not a probability or price prediction.

    Do not allow the score to override contradictory
    evidence from the moving averages or trend analysis.

    ==================================================
    8. BULLISH AND BEARISH FACTORS
    ==================================================

    Identify the strongest evidence-supported
    bullish and bearish technical factors.

    Explain competing technical signals and
    their relevance to different time horizons.

    ==================================================
    9. FINAL TECHNICAL OUTLOOK
    ==================================================

    Choose one classification:

    - Bullish
    - Moderately Bullish
    - Neutral / Mixed
    - Moderately Bearish
    - Bearish

    Base the conclusion on combined evidence from:
    - Price positioning.
    - Moving averages.
    - RSI and MACD.
    - Trading volume.
    - Trend analysis.
    - Support and resistance.

    Explain why the selected classification
    is appropriate.

    ==================================================
    10. CONFIDENCE LEVEL
    ==================================================

    Assign one analytical confidence level:

    HIGH:
    Data is complete and several independent
    indicators show consistent signals.

    MODERATE:
    Data is sufficient but important indicators
    or time horizons show mixed signals.

    LOW:
    Data is incomplete, inconsistent or insufficient.

    Explain the selected confidence level.

    ==================================================
    IMPORTANT RULES
    ==================================================

    1. Use only values returned by the tool.
    2. Never invent prices, dates or indicators.
    3. Preserve numerical accuracy.
    4. Use the latest available market date.
    5. Do not call RSI 67 overbought.
    6. Do not describe near-average volume as
       strong volume confirmation.
    7. Do not treat technical scores as probabilities.
    8. Do not make guaranteed price predictions.
    9. Keep technical conclusions separate from
       business fundamentals and financial performance.
    10. Do not repeat information gaps in multiple sections.
        Present each important limitation clearly and once.
    11. If the tool fails, report the failure instead
        of generating an analysis from assumptions.
    12. This report is for general market research
        and educational purposes, not personalized
        investment advice.
    """,

    expected_output="""
    A comprehensive, professionally structured
    Technical Analysis Report for {company} ({ticker}).

    Follow this exact report structure:

    1. COMPANY AND MARKET DATA
       - Company and ticker.
       - Latest market date and exchange timezone.
       - Latest closing price.
       - Daily percentage change.
       - Market bar status.

    2. MOVING AVERAGE ANALYSIS
       - SMA 20, SMA 50 and SMA 200.
       - EMA 20 and EMA 50.
       - Moving-average alignment.
       - Price positioning.

    3. MOMENTUM ANALYSIS
       - RSI 14 and interpretation.
       - MACD and signal line.
       - MACD histogram and interpretation.

    4. VOLUME ANALYSIS
       - Latest volume.
       - Previous 20-session average volume.
       - Volume ratio.
       - Volume confirmation assessment.

    5. TREND ANALYSIS
       - Short-term trend.
       - Medium-term trend.
       - Long-term trend.
       - Overall trend.
       - Competing technical signals.

    6. SUPPORT AND RESISTANCE
       - Potential support levels.
       - Potential resistance levels.
       - Methodology and limitations.

    7. TECHNICAL SCORE
       - Score and signal classification.
       - Supporting reasons.
       - Explanation of limitations.

    8. BULLISH FACTORS
       - Evidence-supported positive technical signals.

    9. BEARISH FACTORS
       - Evidence-supported negative technical signals.

    10. FINAL TECHNICAL OUTLOOK
        - Overall technical classification.
        - Evidence supporting the conclusion.

    11. CONFIDENCE AND LIMITATIONS
        - High, Moderate or Low confidence.
        - Justification.
        - Important data limitations.

    All numerical claims must match the tool output.
    Keep the report clear, concise, internally consistent
    and useful for downstream sentiment and risk analysis.
    """,

    agent=technical_agent,

    tools=[technical_analysis_data_tool]
)

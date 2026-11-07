
from crewai import Task
from app.agents.sentiment_agent import sentiment_agent


sentiment_task = Task(
    description="""
    Conduct a comprehensive multi-dimensional financial sentiment
    analysis for {company} using the outputs of three independent
    research agents.

    ==============================
    INPUT RESEARCH REPORTS
    ==============================

    1. NEWS RESEARCH REPORT:
    {news_report}

    2. FUNDAMENTAL ANALYSIS REPORT:
    {fundamental_report}

    3. TECHNICAL ANALYSIS REPORT:
    {technical_report}


    ==============================
    1. NEWS SENTIMENT ANALYSIS
    ==============================

    Analyze the news research report.

    Identify:
    - Positive business developments.
    - Negative announcements and market concerns.
    - Neutral information.
    - Important company announcements.
    - Industry and macroeconomic factors.
    - Recurring positive or negative themes.

    Distinguish company-specific developments from
    broader market and industry developments.

    Do not assume that every positive news headline
    will positively affect the stock price.


    ==============================
    2. FUNDAMENTAL SENTIMENT ANALYSIS
    ==============================

    Interpret the fundamental analysis report from
    an investor sentiment perspective.

    Evaluate:
    - Revenue growth and business performance.
    - Profitability and margin trends.
    - Debt and financial leverage.
    - Liquidity position.
    - Operating cash flow and cash flow quality.
    - Financial strengths and weaknesses.

    Classify fundamental sentiment as:
    Positive, Negative, Neutral, or Mixed.

    Important:
    - Revenue growth alone does not prove strong
      financial health.
    - Increasing debt is not automatically negative;
      consider available context.
    - Liquidity ratios below 1 indicate a consideration,
      not automatic financial distress.
    - Distinguish improving cash flow from improving
      accounting profitability.


    ==============================
    3. TECHNICAL SENTIMENT ANALYSIS
    ==============================

    Interpret the technical analysis report.

    Evaluate:
    - Price position relative to SMA20, SMA50 and SMA200.
    - Moving average alignment.
    - RSI momentum.
    - MACD direction and histogram.
    - Trading volume and volume confirmation.
    - Short-term, medium-term and long-term trends.
    - Overall technical signal.

    RSI INTERPRETATION:

    - Below 30: Traditionally oversold territory.
    - 30 to below 50: Relatively weaker momentum.
    - 50 to 70: Generally positive momentum.
    - Above 70: Traditionally overbought territory.

    Do not classify RSI 67 as overbought.

    VOLUME INTERPRETATION:

    - Volume ratio above 1 means volume is above
      its reference average.
    - Volume ratio below 1 means volume is below
      its reference average.
    - Below-average volume does not automatically
      indicate bearish sentiment.
    - Explain whether volume confirms the price movement.

    Distinguish technical momentum from the longer-term
    market trend.

    Classify technical sentiment as:
    Positive, Negative, Neutral, or Mixed.


    ==============================
    4. CROSS-REPORT SENTIMENT ANALYSIS
    ==============================

    Compare the three research reports.

    Identify:

    A. Consistent positive signals:
       Signals that support one another across reports.

    B. Consistent negative signals:
       Signals that reinforce one another across reports.

    C. Conflicting signals:
       Findings that indicate different market or
       business conditions.

    D. Independent signals:
       Findings that describe different aspects of
       the company and are not necessarily contradictory.

    For every important conflict:
    - Identify the two opposing findings.
    - Explain why they differ.
    - Explain their potential significance.
    - Avoid assuming that one finding invalidates another.

    Example:
    Positive business fundamentals alongside bearish
    long-term technical trends represent different
    dimensions of the company's performance and market
    behavior. They should not automatically be treated
    as a direct contradiction.


    ==============================
    5. SENTIMENT BY TIME HORIZON
    ==============================

    Evaluate sentiment across three horizons:

    Short-term:
    Focus on recent news and technical momentum.

    Medium-term:
    Focus on business developments, financial trends
    and intermediate technical conditions.

    Long-term:
    Focus on financial sustainability, profitability,
    debt, cash flow and long-term technical positioning.

    Use only evidence available in the supplied reports.
    If a horizon cannot be assessed reliably, state that.


    ==============================
    6. OVERALL SENTIMENT CLASSIFICATION
    ==============================

    Determine the overall sentiment for {company}.

    Choose exactly one:

    - Positive
    - Negative
    - Neutral
    - Mixed

    Consider:
    - Strength of positive evidence.
    - Strength of negative evidence.
    - Consistency across the three reports.
    - Importance of the identified risks.
    - Different time horizons.

    Explain why the selected classification is appropriate.

    Do not use an arbitrary numerical weighting system.
    Do not force a positive or negative conclusion when
    the available evidence is mixed.


    ==============================
    7. CONFIDENCE ASSESSMENT
    ==============================

    Assign one confidence level:

    High, Moderate, or Low.

    Consider:
    - Completeness of the three research reports.
    - Availability of supporting figures and evidence.
    - Consistency between independent findings.
    - Missing or ambiguous information.
    - Reliability and limitations of the supplied data.

    Explain why the selected confidence level is justified.

    Confidence refers to confidence in the sentiment
    assessment, not confidence in predicting stock prices.


    ==============================
    EXPECTED OUTPUT FORMAT
    ==============================

    # Financial Sentiment Analysis Report

    ## 1. Executive Summary

    ## 2. News Sentiment
    - Classification
    - Positive signals
    - Negative signals
    - Neutral signals
    - Important developments

    ## 3. Fundamental Sentiment
    - Classification
    - Financial strengths
    - Financial concerns

    ## 4. Technical Sentiment
    - Classification
    - Bullish signals
    - Bearish signals
    - Volume confirmation
    - Trend interpretation

    ## 5. Cross-Report Analysis
    - Consistent positive signals
    - Consistent negative signals
    - Conflicting signals
    - Independent signals

    ## 6. Sentiment by Time Horizon
    - Short-term
    - Medium-term
    - Long-term

    ## 7. Overall Market Sentiment
    - Classification
    - Main sentiment drivers
    - Supporting explanation

    ## 8. Confidence and Limitations
    - Confidence level
    - Justification
    - Missing information
    - Analytical limitations


    ==============================
    STRICT ANALYTICAL RULES
    ==============================

    1. Use only information from the three supplied reports.
    2. Never invent financial figures, news, indicators,
       events, or market data.
    3. Preserve the original figures and units.
    4. Do not independently recalculate technical indicators.
    5. Distinguish reported facts from your interpretations.
    6. Do not confuse company performance with stock performance.
    7. Do not treat positive news as a guaranteed price catalyst.
    8. Do not treat bearish technical signals as proof of
       deteriorating company fundamentals.
    9. Avoid repeating the same signal in multiple sections
       unless necessary for the explanation.
    10. If a report lacks information, explicitly mention it.
    11. Never guarantee future market movements.
    12. Do not provide personalized investment advice.
    """,

    expected_output="""
    A detailed and structured Financial Sentiment Analysis Report
    containing:

    1. Executive summary.
    2. Separate news, fundamental and technical sentiment.
    3. Positive and negative signals.
    4. Cross-report consistency and conflict analysis.
    5. Short-term, medium-term and long-term sentiment.
    6. Overall classification: Positive, Negative, Neutral or Mixed.
    7. Confidence level with justification.
    8. Missing information and analytical limitations.

    All conclusions must be supported by the three supplied reports.
    """,

    agent=sentiment_agent
)

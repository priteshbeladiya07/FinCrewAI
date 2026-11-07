from crewai import Task
 
from app.agents.fundamental_agent import fundamental_agent
 
 
fundamental_task = Task(
    description="""
    Conduct a detailed fundamental analysis of {company}.
 
    Stock ticker: {ticker}
 
    First, call the Fundamental Financial Data tool.
 
    How to use the tool output:
    - annual_financials: historical annual figures and ratios, keyed by
      fiscal year (for example FY2026). Use it for historical analysis.
    - trend_analysis: movement of each metric between consecutive years,
      calculated in Python. Use its direction labels and steps as given.
      Do NOT recalculate growth rates, margins, ratios or trends.
    - analytical_flags: facts that must not be overlooked, such as growth
      below 1%, margins moving in different directions, quick ratio
      below 1, or negative free cash flow. Address every flag that is
      relevant to your analysis.
    - current_market_metrics: current valuation snapshot only.
    - units: the unit of all amounts. State it in the report
      (for example, INR crore).
    - warnings, excluded_periods, unavailable_metrics, data_notes:
      data-quality information to disclose in the report.
 
    Analyze these areas:
 
    1. Revenue and earnings:
       - Annual revenue and revenue growth.
       - Net income and net income growth.
       - EPS and EPS growth.
 
    2. Profitability:
       - Gross profit margin.
       - Operating margin.
       - Net profit margin.
       - Return on equity (ROE).
       - Return on assets (ROA).
 
    3. Balance sheet:
       - Total assets and equity.
       - Total debt and cash.
       - Debt-to-equity ratio.
 
    4. Liquidity:
       - Current ratio.
       - Quick ratio.
       - Explain short-term financial risks.
 
    5. Cash flow:
       - Operating cash flow.
       - Capital expenditure (capital_expenditure_outflow).
       - Calculated free cash flow.
       - Explain cash-generation quality.
 
    6. Valuation:
       - Trailing P/E.
       - Forward P/E.
       - Price-to-book.
       - Enterprise value to EBITDA.
       - Explain limitations of these ratios.
 
    7. Fundamental outlook:
       - Financial strengths.
       - Financial weaknesses.
       - Important risks.
       - Overall assessment: Strong, Moderate, or Weak.
 
    ADDITIONAL ANALYSIS REQUIREMENTS:
 
    1. Trend analysis
       - Compare each financial metric across all available annual
         periods, using the trend_analysis section.
       - Explain whether each metric is rising, falling, flat, or
         fluctuating, and quote the year-by-year changes.
       - Never make a general improvement or decline claim when
         individual metrics or years show different trends.
       - Highlight unusually small growth rates, such as growth
         below 1%, and call them effectively flat.
 
    2. Profitability interpretation
       - Analyze gross, operating, and net margins separately.
       - Explain how each margin changed in each reporting period.
       - State whether profitability is moving consistently or
         fluctuating. For example, do not write "increasing margins"
         if one margin fell in the same period.
 
    3. Liquidity interpretation
       - Explain what the current ratio and quick ratio measure.
       - A current ratio above 1 means current assets exceed current
         liabilities. A quick ratio below 1 means current assets
         excluding inventory do not fully cover current liabilities.
         Explain this short-term liquidity consideration.
       - Identify potential short-term liquidity concerns.
       - Do not automatically classify ratios above 1 as healthy.
 
    4. Debt analysis
       - Analyze the debt-to-equity trend across all periods.
       - Explain the relationship between debt and equity. For example,
         a ratio of 0.44 means debt equals about 44% of reported equity
         under the tool's calculation.
       - Do not classify debt as high or low without industry
         benchmarks or peer data. Say that this requires industry
         comparison and debt-servicing metrics.
       - State that debt-servicing metrics (such as interest coverage)
         are unavailable.
 
    5. Cash flow quality
       - Compare operating cash flow, capital expenditure, and free
         cash flow across periods.
       - Explain whether free cash flow is improving or deteriorating
         and what drove the change (operating cash flow versus
         capital expenditure).
       - Identify any periods of negative free cash flow.
       - Do not automatically treat high capital expenditure as
         negative; it may represent investment.
 
    6. Valuation interpretation
       For each available valuation metric, explain:
       - What the metric measures.
       - What the reported value indicates.
       - Its limitations.
       - Why peer comparison or historical valuation data would be
         needed for a stronger conclusion.
       Do not classify the stock as undervalued, overvalued, cheap, or
       expensive without supporting comparison evidence.
 
    7. Final assessment
       Provide:
       - Financial strengths.
       - Financial weaknesses.
       - Key financial risks.
       - Overall assessment: Strong, Moderate, or Weak.
       - Confidence: High, Medium, or Low.
       Explain the evidence behind both the assessment and the
       confidence level.
 
    8. Output quality
       - Use the unit given in the tool's units section (for example,
         INR crore) for financial statement amounts, and state the unit.
       - Use clearly labelled financial years (for example FY2026).
       - Include a concise comparison table for the important metrics
         across all years.
       - Separate reported facts, calculated metrics, and analyst
         interpretations.
       - Do not repeat the same numbers unnecessarily.
       - Explicitly disclose missing data, excluded periods, and
         provider limitations.
 
    STRICT ANALYSIS RULES:
 
    - Use only figures supplied by the data tool.
    - Do not calculate or estimate any financial figure yourself.
    - Do not invent missing financial values.
    - Identify each reporting period explicitly.
    - Do not confuse annual values with quarterly values.
    - Market valuation metrics are current snapshots.
      Never describe them as historical trends.
    - Do not claim improvement if two compared values are equal.
    - If a metric is missing, explicitly say it is unavailable.
    - Do not infer future earnings growth from forward P/E alone.
    - Do not call debt high or low without explaining the evidence.
    - If the company is in the financial sector (banks, insurers), do
      not apply non-financial liquidity or leverage interpretation, and
      say why some metrics are unavailable or not comparable.
    - If the data is incomplete or inconsistent, lower confidence
      in the assessment and explain why.
    - This report is general financial research, not
      personalized investment advice.
    """,
 
    expected_output="""
    # Fundamental Analysis Report
 
    1. Company Overview
       - Company name, ticker, sector, reporting currency and unit,
         data provider and retrieval date.
 
    2. Revenue and Earnings Analysis
       - Annual figures and growth for each year, with trend direction.
 
    3. Profitability Analysis
       - Gross, operating and net margins analyzed separately, plus
         ROE and ROA, with year-by-year movement.
 
    4. Balance Sheet Analysis
       - Assets, equity, debt, cash and debt-to-equity trend.
       - No high/low debt label without a benchmark.
 
    5. Liquidity Analysis
       - Current ratio and quick ratio, what they mean, and short-term
         liquidity considerations.
 
    6. Cash Flow Analysis
       - Operating cash flow, capital expenditure and free cash flow,
         including negative periods and what drove the trend.
 
    7. Valuation Analysis
       - For each metric: what it measures, the reported value, its
         limitations, and what comparison data is needed.
       - No undervalued/overvalued claim without evidence.
 
    8. Key Metrics Comparison Table
       - Concise table of important metrics by financial year.
 
    9. Financial Strengths
 
    10. Financial Weaknesses and Risks
 
    11. Overall Fundamental Outlook
        - Strong, Moderate or Weak.
        - Supporting evidence.
        - Confidence: High, Medium or Low, with the reason.
 
    12. Data Quality and Limitations
        - Missing metrics, excluded periods, reporting period
          limitations, provider limitations, and unavailable
          benchmarks or debt-servicing metrics.
 
    Label every fact as reported, calculated, or interpretation where
    the distinction matters. Include financial years and units wherever
    available. Never fabricate financial figures.
    """,
 
    agent=fundamental_agent
)
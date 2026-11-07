import json
import re
from datetime import datetime, timezone
 
import pandas as pd
import yfinance as yf
from crewai.tools import tool
 
 
# ---------------------------------------------------------------------------
# Units
# ---------------------------------------------------------------------------
 
CRORE = 10_000_000  # 1 crore = 10^7
MILLION = 1_000_000
 
# Money fields shown to the agent (converted to the display unit).
MONEY_FIELDS = [
    "revenue",
    "gross_profit",
    "operating_income",
    "net_income",
    "total_assets",
    "current_assets",
    "current_liabilities",
    "inventory",
    "total_debt",
    "cash",
    "equity",
    "operating_cash_flow",
    "capital_expenditure_outflow",
    "calculated_free_cash_flow",
]
 
# Per-share values (never converted).
PER_SHARE_FIELDS = ["basic_eps", "diluted_eps"]
 
# Ratios and percentages (never converted).
RATIO_FIELDS = [
    "revenue_growth_pct",
    "net_income_growth_pct",
    "eps_growth_pct",
    "gross_margin_pct",
    "operating_margin_pct",
    "net_margin_pct",
    "roe_pct",
    "roa_pct",
    "current_ratio",
    "quick_ratio",
    "debt_to_equity",
    "capex_to_ocf_pct",
]
 
# Metrics for which Python computes a trend label.
# kind: pct_change = % change, pp = percentage-point change,
#       ratio = absolute change in a ratio, abs_change = absolute change.
TREND_SPECS = {
    "revenue": "pct_change",
    "net_income": "pct_change",
    "diluted_eps": "pct_change",
    "operating_cash_flow": "pct_change",
    "capital_expenditure_outflow": "pct_change",
    "calculated_free_cash_flow": "abs_change",
    "total_debt": "pct_change",
    "equity": "pct_change",
    "cash": "pct_change",
    "gross_margin_pct": "pp",
    "operating_margin_pct": "pp",
    "net_margin_pct": "pp",
    "roe_pct": "pp",
    "roa_pct": "pp",
    "capex_to_ocf_pct": "pp",
    "current_ratio": "ratio",
    "quick_ratio": "ratio",
    "debt_to_equity": "ratio",
}
 
# A step smaller than this is treated as "flat".
FLAT_THRESHOLD = {
    "pct_change": 1.0,   # 1 percent
    "pp": 0.05,          # 0.05 percentage points
    "ratio": 0.01,       # 0.01 ratio points
}
 
 
# ---------------------------------------------------------------------------
# Basic helpers
# ---------------------------------------------------------------------------
 
def clean_number(value):
    """Convert financial statement values into JSON-safe numbers."""
 
    if value is None:
        return None
 
    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass
 
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
 
 
def normalize_label(value):
    """Normalize statement labels to make row matching easier."""
    return re.sub(r"[^a-z0-9]", "", str(value).lower())
 
 
def get_statement_value(statement, aliases, period):
    """Retrieve a financial metric for a particular reporting period."""
 
    if statement is None or statement.empty:
        return None
 
    row_lookup = {
        normalize_label(row): row
        for row in statement.index
    }
 
    for alias in aliases:
        actual_row = row_lookup.get(normalize_label(alias))
 
        if actual_row is not None and period in statement.columns:
            return clean_number(statement.loc[actual_row, period])
 
    return None
 
 
def get_periods(statement):
    """Return statement periods in chronological order."""
 
    if statement is None or statement.empty:
        return []
 
    return sorted(
        statement.columns,
        key=lambda period: pd.Timestamp(period)
    )
 
 
def period_label(period):
    """Format a reporting period end date consistently (YYYY-MM-DD)."""
    return pd.Timestamp(period).strftime("%Y-%m-%d")
 
 
def fiscal_year_label(period_end):
    """
    Label a fiscal year by the calendar year in which it ends.
    Example: the year ended 2026-03-31 is labelled FY2026.
    """
    return f"FY{pd.Timestamp(period_end).year}"
 
 
def calculate_percentage(numerator, denominator):
    if numerator is None or denominator in (None, 0):
        return None
 
    return round((numerator / denominator) * 100, 2)
 
 
def calculate_ratio(numerator, denominator):
    if numerator is None or denominator in (None, 0):
        return None
 
    return round(numerator / denominator, 3)
 
 
def calculate_growth(current, previous):
    """Calculate year-over-year growth."""
 
    if current is None or previous in (None, 0):
        return None
 
    return round(((current - previous) / abs(previous)) * 100, 2)
 
 
def is_consecutive_year(current_period_end, previous_period_end):
    """True when two period ends are roughly one year apart."""
    days = (
        pd.Timestamp(current_period_end)
        - pd.Timestamp(previous_period_end)
    ).days
 
    return 330 <= days <= 400
 
 
# ---------------------------------------------------------------------------
# Currency and unit conversion
# ---------------------------------------------------------------------------
 
def determine_currency(info, ticker):
    """Return (currency, source) for the financial statements."""
 
    currency = info.get("financialCurrency") or info.get("currency")
 
    if currency:
        return currency, "provider"
 
    if ticker.endswith((".NS", ".BO")):
        return "INR", "inferred from Indian exchange suffix"
 
    return None, "not available"
 
 
def get_unit_config(currency):
    """Return (divisor, unit_label) used for financial statement amounts."""
 
    if currency == "INR":
        return CRORE, "INR crore"
 
    if currency:
        return MILLION, f"{currency} million"
 
    return 1, "provider units (currency not provided)"
 
 
def convert_amount(value, divisor):
    if value is None:
        return None
 
    return round(value / divisor, 2)
 
 
# ---------------------------------------------------------------------------
# Extraction from raw statements (raw provider units kept internally)
# ---------------------------------------------------------------------------
 
def extract_annual_financials(income, balance, cashflow):
    """
    Extract annual figures and calculate historical ratios.
 
    Returns (annual_data, excluded_periods, warnings).
    annual_data values stay in raw provider units. Periods whose income
    statement values are all null are excluded instead of being sent
    on as valid financial years.
    """
 
    income_metrics = {
        "revenue": ["Total Revenue", "Operating Revenue", "Revenue"],
        "gross_profit": ["Gross Profit"],
        "operating_income": ["Operating Income"],
        "net_income": ["Net Income"],
        "basic_eps": ["Basic EPS"],
        "diluted_eps": ["Diluted EPS"],
    }
 
    balance_metrics = {
        "total_assets": ["Total Assets"],
        "current_assets": ["Current Assets"],
        "current_liabilities": ["Current Liabilities"],
        "inventory": ["Inventory"],
        "total_debt": ["Total Debt"],
        "cash": [
            "Cash And Cash Equivalents",
            "Cash Cash Equivalents And Short Term Investments",
        ],
        "equity": [
            "Stockholders Equity",
            "Stockholders Equity Including Minority Interest",
            "Total Equity Gross Minority Interest",
        ],
    }
 
    cashflow_metrics = {
        "operating_cash_flow": [
            "Operating Cash Flow",
            "Cash Flow From Continuing Operating Activities",
        ],
        "capital_expenditure": ["Capital Expenditure"],
        "reported_free_cash_flow": ["Free Cash Flow"],
    }
 
    balance_periods = set(get_periods(balance))
    cashflow_periods = set(get_periods(cashflow))
 
    annual_data = {}
    excluded_periods = []
    warnings = []
 
    for period in get_periods(income):
 
        values = {}
 
        for name, aliases in income_metrics.items():
            values[name] = get_statement_value(income, aliases, period)
 
        # Remove periods with no usable income statement data.
        if all(value is None for value in values.values()):
            excluded_periods.append({
                "period_end": period_label(period),
                "reason": (
                    "All income statement values were null or "
                    "unavailable from the provider."
                ),
            })
            continue
 
        label = period_label(period)
 
        if period in balance_periods:
            for name, aliases in balance_metrics.items():
                values[name] = get_statement_value(balance, aliases, period)
        else:
            for name in balance_metrics:
                values[name] = None
            warnings.append(
                f"Balance sheet data unavailable for period ending {label}."
            )
 
        if period in cashflow_periods:
            for name, aliases in cashflow_metrics.items():
                values[name] = get_statement_value(cashflow, aliases, period)
        else:
            for name in cashflow_metrics:
                values[name] = None
            warnings.append(
                f"Cash flow data unavailable for period ending {label}."
            )
 
        # Free cash flow = operating cash flow - capital expenditure outflow.
        # Providers usually report capex as a negative number, so the
        # magnitude is used to avoid sign ambiguity.
        ocf = values.get("operating_cash_flow")
        capex = values.get("capital_expenditure")
 
        values["capital_expenditure_outflow"] = (
            abs(capex) if capex is not None else None
        )
 
        if ocf is not None and capex is not None:
            values["calculated_free_cash_flow"] = ocf - abs(capex)
            values["free_cash_flow_source"] = (
                "calculated: operating cash flow minus capital expenditure"
            )
        elif values.get("reported_free_cash_flow") is not None:
            values["calculated_free_cash_flow"] = values[
                "reported_free_cash_flow"
            ]
            values["free_cash_flow_source"] = "provider-reported"
        else:
            values["calculated_free_cash_flow"] = None
            values["free_cash_flow_source"] = "unavailable"
 
        values["capex_to_ocf_pct"] = (
            calculate_percentage(values["capital_expenditure_outflow"], ocf)
            if ocf is not None and ocf > 0
            else None
        )
 
        # Profitability ratios.
        values["gross_margin_pct"] = calculate_percentage(
            values.get("gross_profit"), values.get("revenue")
        )
        values["operating_margin_pct"] = calculate_percentage(
            values.get("operating_income"), values.get("revenue")
        )
        values["net_margin_pct"] = calculate_percentage(
            values.get("net_income"), values.get("revenue")
        )
 
        # Liquidity ratios.
        values["current_ratio"] = calculate_ratio(
            values.get("current_assets"),
            values.get("current_liabilities"),
        )
 
        current_assets = values.get("current_assets")
        inventory = values.get("inventory")
 
        if current_assets is not None and inventory is not None:
            values["quick_ratio"] = calculate_ratio(
                current_assets - inventory,
                values.get("current_liabilities"),
            )
        else:
            values["quick_ratio"] = None
 
        # Leverage ratio.
        values["debt_to_equity"] = calculate_ratio(
            values.get("total_debt"), values.get("equity")
        )
 
        annual_data[label] = values
 
    # Year-over-year growth and average-balance ROE/ROA.
    labels = list(annual_data.keys())
 
    for index, label in enumerate(labels):
 
        current = annual_data[label]
 
        current["revenue_growth_pct"] = None
        current["net_income_growth_pct"] = None
        current["eps_growth_pct"] = None
        current["roe_pct"] = None
        current["roa_pct"] = None
 
        if index == 0:
            continue
 
        previous_label = labels[index - 1]
        previous = annual_data[previous_label]
 
        # Do not compare periods that are not one year apart
        # (for example when a middle year was excluded).
        if not is_consecutive_year(label, previous_label):
            warnings.append(
                f"Periods {previous_label} and {label} are not one year "
                "apart; growth, ROE and ROA were not calculated for "
                f"{label}."
            )
            continue
 
        current["revenue_growth_pct"] = calculate_growth(
            current.get("revenue"), previous.get("revenue")
        )
        current["net_income_growth_pct"] = calculate_growth(
            current.get("net_income"), previous.get("net_income")
        )
        current["eps_growth_pct"] = calculate_growth(
            current.get("diluted_eps"), previous.get("diluted_eps")
        )
 
        average_equity = None
        if (
            current.get("equity") is not None
            and previous.get("equity") is not None
        ):
            average_equity = (current["equity"] + previous["equity"]) / 2
 
        current["roe_pct"] = calculate_percentage(
            current.get("net_income"), average_equity
        )
 
        average_assets = None
        if (
            current.get("total_assets") is not None
            and previous.get("total_assets") is not None
        ):
            average_assets = (
                current["total_assets"] + previous["total_assets"]
            ) / 2
 
        current["roa_pct"] = calculate_percentage(
            current.get("net_income"), average_assets
        )
 
    return annual_data, excluded_periods, warnings
 
 
# ---------------------------------------------------------------------------
# Validation of raw data
# ---------------------------------------------------------------------------
 
def validate_annual_data(raw):
    """Run sanity checks and return a list of warning strings."""
 
    warnings = []
 
    for period_end, values in raw.items():
        label = fiscal_year_label(period_end)
 
        revenue = values.get("revenue")
        gross_profit = values.get("gross_profit")
        current_assets = values.get("current_assets")
        inventory = values.get("inventory")
        equity = values.get("equity")
 
        # Provider FCF vs. our calculation.
        ocf = values.get("operating_cash_flow")
        capex = values.get("capital_expenditure")
        reported_fcf = values.get("reported_free_cash_flow")
        calculated_fcf = values.get("calculated_free_cash_flow")
 
        if (
            ocf is not None
            and capex is not None
            and reported_fcf is not None
            and calculated_fcf is not None
        ):
            scale = max(abs(reported_fcf), abs(calculated_fcf))
            if scale > 0 and abs(reported_fcf - calculated_fcf) / scale > 0.01:
                warnings.append(
                    f"{label}: calculated free cash flow differs from the "
                    "provider-reported figure by more than 1%."
                )
 
        if revenue is not None and revenue <= 0:
            warnings.append(
                f"{label}: revenue is zero or negative; margins are not "
                "meaningful."
            )
 
        if (
            revenue is not None
            and revenue > 0
            and gross_profit is not None
            and gross_profit > revenue
        ):
            warnings.append(
                f"{label}: gross profit exceeds revenue; data may be "
                "inconsistent."
            )
 
        if (
            current_assets is not None
            and inventory is not None
            and inventory > current_assets
        ):
            warnings.append(
                f"{label}: inventory exceeds current assets; quick ratio "
                "may be unreliable."
            )
 
        if equity is not None and equity <= 0:
            warnings.append(
                f"{label}: equity is zero or negative; debt-to-equity, "
                "ROE and book-value based ratios are not meaningful."
            )
 
    return warnings
 
 
# ---------------------------------------------------------------------------
# Display data (converted units) and Python-calculated trends
# ---------------------------------------------------------------------------
 
def build_display_financials(raw, divisor):
    """Convert raw values to the display unit and label fiscal years."""
 
    display = {}
 
    for period_end, values in raw.items():
        row = {"period_end": period_end}
 
        for field in MONEY_FIELDS:
            row[field] = convert_amount(values.get(field), divisor)
 
        for field in PER_SHARE_FIELDS + RATIO_FIELDS:
            row[field] = values.get(field)
 
        row["free_cash_flow_source"] = values.get("free_cash_flow_source")
 
        display[fiscal_year_label(period_end)] = row
 
    return display
 
 
def classify_series(series, kind):
    """
    Describe how a metric moved across consecutive periods.
 
    Returns step-by-step movements and a neutral direction label:
    rising_every_period, falling_every_period, flat,
    rising_with_flat_periods, falling_with_flat_periods, fluctuating,
    or insufficient_data.
    """
 
    valid = [(label, value) for label, value in series.items()
             if value is not None]
 
    result = {
        "direction": "insufficient_data",
        "change_basis": {
            "pct_change": "percent change",
            "pp": "percentage-point change",
            "ratio": "absolute change in ratio",
            "abs_change": "absolute change in reporting unit",
        }[kind],
        "steps": [],
        "net_change_first_to_last": None,
    }
 
    if len(valid) < 2:
        return result
 
    if kind == "abs_change":
        largest = max(abs(value) for _, value in valid)
        threshold = largest * 0.01
    else:
        threshold = FLAT_THRESHOLD[kind]
 
    def compute_change(current, previous):
        if kind == "pct_change":
            return calculate_growth(current, previous)
        if kind == "ratio":
            return round(current - previous, 3)
        return round(current - previous, 2)
 
    for (_, previous_value), (current_label, current_value) in zip(
        valid, valid[1:]
    ):
        change = compute_change(current_value, previous_value)
 
        if change is None:
            continue
 
        if change > threshold:
            movement = "up"
        elif change < -threshold:
            movement = "down"
        else:
            movement = "flat"
 
        result["steps"].append({
            "period": current_label,
            "change": change,
            "movement": movement,
        })
 
    result["net_change_first_to_last"] = {
        "from": valid[0][0],
        "to": valid[-1][0],
        "change": compute_change(valid[-1][1], valid[0][1]),
    }
 
    movements = [step["movement"] for step in result["steps"]]
 
    if not movements:
        return result
 
    ups = movements.count("up")
    downs = movements.count("down")
    flats = movements.count("flat")
 
    if ups and downs:
        direction = "fluctuating"
    elif ups and not flats:
        direction = "rising_every_period"
    elif downs and not flats:
        direction = "falling_every_period"
    elif ups:
        direction = "rising_with_flat_periods"
    elif downs:
        direction = "falling_with_flat_periods"
    else:
        direction = "flat"
 
    result["direction"] = direction
 
    return result
 
 
def build_trend_analysis(display):
    trends = {}
 
    for metric, kind in TREND_SPECS.items():
        series = {
            label: row.get(metric) for label, row in display.items()
        }
        trends[metric] = classify_series(series, kind)
 
    return trends
 
 
def build_analytical_flags(display, trends):
    """Facts the report must not overlook (small growth, divergences...)."""
 
    flags = []
 
    # Growth below 1% is effectively flat.
    for metric, name in [
        ("revenue", "revenue"),
        ("net_income", "net income"),
        ("diluted_eps", "diluted EPS"),
    ]:
        for step in trends[metric]["steps"]:
            if abs(step["change"]) < 1:
                flags.append(
                    f"{step['period']}: {name} growth was "
                    f"{step['change']}%, below 1% (effectively flat)."
                )
 
    # Margins moving in different directions in the same year.
    margin_metrics = [
        "gross_margin_pct",
        "operating_margin_pct",
        "net_margin_pct",
    ]
 
    movements_by_period = {}
 
    for metric in margin_metrics:
        for step in trends[metric]["steps"]:
            movements_by_period.setdefault(step["period"], {})[
                metric
            ] = step["movement"]
 
    for period, moves in movements_by_period.items():
        if "up" in moves.values() and "down" in moves.values():
            detail = ", ".join(
                f"{name.replace('_margin_pct', '')} margin {move}"
                for name, move in moves.items()
            )
            flags.append(
                f"{period}: margins moved in different directions "
                f"({detail}). Describe each margin separately."
            )
 
    # Liquidity and cash flow facts per year.
    for label, row in display.items():
        current_ratio = row.get("current_ratio")
        quick_ratio = row.get("quick_ratio")
        fcf = row.get("calculated_free_cash_flow")
 
        if current_ratio is not None and current_ratio < 1:
            flags.append(
                f"{label}: current ratio is {current_ratio}, below 1.0."
            )
 
        if quick_ratio is not None and quick_ratio < 1:
            flags.append(
                f"{label}: quick ratio is {quick_ratio}, below 1.0 "
                "(current assets excluding inventory are smaller than "
                "current liabilities)."
            )
 
        if fcf is not None and fcf < 0:
            flags.append(f"{label}: free cash flow is negative.")
 
    return flags
 
 
# ---------------------------------------------------------------------------
# Report assembly (pure function: no network access, easy to test)
# ---------------------------------------------------------------------------
 
def build_fundamental_report(
    ticker, income, balance, cashflow, info, extra_warnings=None
):
    """
    Build the JSON-serialisable report dictionary.
 
    Returns (report, raw_annual_data). The raw data keeps the provider's
    original units and is meant for internal checks and testing.
    """
 
    info = info or {}
    warnings = list(extra_warnings or [])
 
    raw, excluded_periods, extraction_warnings = extract_annual_financials(
        income, balance, cashflow
    )
    warnings.extend(extraction_warnings)
 
    if not raw:
        return None, {}
 
    warnings.extend(validate_annual_data(raw))
 
    currency, currency_source = determine_currency(info, ticker)
    divisor, unit_label = get_unit_config(currency)
 
    display = build_display_financials(raw, divisor)
    trends = build_trend_analysis(display)
    flags = build_analytical_flags(display, trends)
 
    # Metrics that are unavailable in every period.
    unavailable_metrics = [
        field
        for field in MONEY_FIELDS + PER_SHARE_FIELDS + RATIO_FIELDS
        if all(row.get(field) is None for row in display.values())
    ]
 
    if unavailable_metrics:
        warnings.append(
            "Metrics unavailable for all periods: "
            + ", ".join(unavailable_metrics) + "."
        )
 
    if len(display) < 2:
        warnings.append(
            "Fewer than two valid annual periods are available. "
            "Growth and trend calculations are unavailable."
        )
 
    if excluded_periods:
        warnings.append(
            "Excluded periods with no data: "
            + ", ".join(p["period_end"] for p in excluded_periods) + "."
        )
 
    sector = info.get("sector")
 
    if sector and "financial" in sector.lower():
        warnings.append(
            "Financial-sector company: gross margin, current ratio, "
            "quick ratio, inventory and debt-to-equity are generally not "
            "comparable with non-financial companies and may be "
            "unavailable or not meaningful. Do not apply "
            "non-financial liquidity or leverage interpretation."
        )
 
    # Current market snapshot (not historical).
    market_fields = {
        "market_cap": "marketCap",
        "trailing_pe": "trailingPE",
        "forward_pe": "forwardPE",
        "price_to_book": "priceToBook",
        "enterprise_to_ebitda": "enterpriseToEbitda",
        "dividend_yield": "dividendYield",
    }
 
    market_metrics = {}
 
    for output_name, source_name in market_fields.items():
        value = clean_number(info.get(source_name))
 
        if value is None:
            continue
 
        if output_name == "market_cap":
            trading_currency = info.get("currency")
 
            if (
                currency
                and trading_currency
                and trading_currency != currency
            ):
                warnings.append(
                    "Market cap is in the trading currency "
                    f"({trading_currency}), which differs from the "
                    f"reporting currency ({currency}); it was not "
                    "converted."
                )
                market_metrics["market_cap_raw_trading_currency"] = value
                continue
 
            value = convert_amount(value, divisor)
 
        market_metrics[output_name] = value
 
    report = {
        "company": (
            info.get("longName") or info.get("shortName") or ticker
        ),
        "ticker": ticker,
        "sector": sector or "Not provided",
        "industry": info.get("industry") or "Not provided",
        "exchange": info.get("exchange", "Not provided"),
        "reporting_currency": currency or "Not provided",
        "currency_source": currency_source,
        "units": {
            "financial_statement_amounts": unit_label,
            "market_cap": unit_label,
            "per_share_values": (
                f"{currency} per share" if currency else "per share"
            ),
            "ratios_and_percentages": (
                "ratios are unitless; fields ending in _pct are percentages"
            ),
        },
        "data_provider": "Yahoo Finance via yfinance",
        "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
        "annual_financials": display,
        "excluded_periods": excluded_periods,
        "trend_analysis": trends,
        "analytical_flags": flags,
        "current_market_metrics": market_metrics,
        "unavailable_metrics": unavailable_metrics,
        "warnings": warnings,
        "methodology": {
            "fiscal_year_label": (
                "Calendar year in which the fiscal year ends "
                "(for example, FY2026 = year ended 2026-03-31)."
            ),
            "growth": "Year-over-year percentage change.",
            "margins": "Profit metric divided by revenue.",
            "roe": "Net income divided by average of opening and "
                   "closing equity.",
            "roa": "Net income divided by average of opening and "
                   "closing total assets.",
            "current_ratio": "Current assets divided by current "
                             "liabilities.",
            "quick_ratio": (
                "(Current assets minus inventory) divided by current "
                "liabilities."
            ),
            "debt_to_equity": "Total debt divided by equity (provider "
                              "total debt may include lease liabilities).",
            "free_cash_flow": (
                "Operating cash flow minus capital expenditure outflow."
            ),
            "capital_expenditure_outflow": (
                "Capital expenditure shown as a positive cash outflow."
            ),
            "capex_to_ocf_pct": (
                "Capital expenditure outflow as a percentage of "
                "operating cash flow (only when operating cash flow "
                "is positive)."
            ),
            "trend_direction": (
                "Neutral movement labels calculated in Python. Steps "
                "smaller than 1% (growth metrics), 0.05 percentage "
                "points (margins, ROE, ROA) or 0.01 (ratios) count as "
                "flat. Labels describe direction only and do not mean "
                "'good' or 'bad'."
            ),
        },
        "data_notes": [
            f"Financial statement amounts are shown in {unit_label}. "
            "Original provider values are not shown.",
            "Market valuation metrics are current snapshots, "
            "not historical annual values.",
            "Trailing P/E uses trailing-twelve-month earnings, which "
            "may not match the latest annual fiscal year.",
            "dividend_yield is shown as supplied by the provider; its "
            "unit (fraction or percent) depends on the yfinance "
            "version, so do not interpret it without confirming.",
            "ROE and ROA are unavailable for the first period because "
            "an opening balance is needed for the average.",
            "Growth is unavailable when the previous value is zero "
            "or missing.",
            "The latest reporting period may be incomplete or "
            "subject to provider updates.",
            "No peer, industry or historical valuation benchmarks are "
            "provided.",
            "No debt-servicing metrics (such as interest coverage) "
            "are provided.",
        ],
    }
 
    return report, raw
 
 
# ---------------------------------------------------------------------------
# CrewAI tool
# ---------------------------------------------------------------------------
 
@tool("Fundamental Financial Data")
def get_fundamental_data(ticker: str) -> str:
    """
    Retrieve annual financial statements and calculate fundamental
    financial ratios, trends and data-quality flags for a stock ticker.
 
    Examples:
    RELIANCE.NS
    TCS.NS
    INFY.NS
    """
 
    ticker = ticker.strip().upper()
 
    if not re.fullmatch(r"[A-Z0-9.^=-]{1,25}", ticker):
        return "Invalid ticker format."
 
    try:
        stock = yf.Ticker(ticker)
 
        income = stock.income_stmt
        balance = stock.balance_sheet
        cashflow = stock.cashflow
 
        if income is None or income.empty:
            return f"No annual income statement found for {ticker}."
 
        extra_warnings = []
 
        try:
            info = stock.info or {}
        except Exception as error:
            info = {}
            extra_warnings.append(
                f"Market information unavailable: {str(error)}"
            )
 
        if balance is None or balance.empty:
            extra_warnings.append("Annual balance sheet is unavailable.")
 
        if cashflow is None or cashflow.empty:
            extra_warnings.append("Annual cash flow statement is unavailable.")
 
        report, _raw = build_fundamental_report(
            ticker, income, balance, cashflow, info, extra_warnings
        )
 
        if report is None:
            return (
                f"No usable annual financial data found for {ticker}: "
                "all reporting periods were empty."
            )
 
        return json.dumps(report, indent=2, ensure_ascii=False)
 
    except Exception as error:
        return (
            f"Fundamental data retrieval failed for {ticker}: "
            f"{str(error)}"
        )
 
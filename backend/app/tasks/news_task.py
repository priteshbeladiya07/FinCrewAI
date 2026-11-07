from crewai import Task
from app.agents.news_agent import news_agent
 
news_task = Task(
    description="""
    Research the last 30 days of news about {company}.
 
    PROCESS
    1. Call "Financial News Search" once with company="{company}".
       It already searches general, results, and risk/negative angles.
       If the result is thin, call it once more with a focus topic.
    2. Use ONLY articles returned by the tool. Never use social media.
    3. Merge articles describing the same event into ONE development.
       Max 8 developments, newest and most important first.
    4. For every figure record its scope and basis: group vs segment,
       consolidated vs standalone, YoY vs QoQ, and the source.
    5. If two sources give different figures for the same metric, do NOT
       pick one silently: list both under "Data Conflicts". Treat a number
       that looks like a segment figure (e.g. retail only) as such.
    6. Negative developments: use the risk_negative results. Write
       "None found in retrieved sources" only if that angle ran and
       returned nothing relevant. Never write "no negative developments"
       as a fact.
    7. Mark each development as FACT (reported) or EXPECTATION
       (forecast, analyst estimate, rating outlook).
    8. Prefer source_tier 1 (official) and 2 (major publisher) for
       numbers. Flag tier 3 or undated items as lower confidence.
 
    Do not invent news, dates, figures or sources. Do not give
    investment advice.
    """,
 
    expected_output="""
    Markdown report with exactly these sections:
 
    1. Company name and report date.
    2. Latest-quarter key figures: table with columns
       Metric | Value | Scope (group/segment, consolidated) | Basis (YoY/QoQ) | Source.
    3. Consolidated developments (max 8): for each give
       Headline | Date | FACT or EXPECTATION | 1-2 sentence summary |
       Source name + URL | Source tier.
    4. Positive developments (with impact, one line each).
    5. Negative developments / risks (from the risk search) or
       "None found in retrieved sources".
    6. Data conflicts between sources (or "None detected").
    7. Potential business impact: short-term and medium-term.
    8. Sources: URL, publisher, publication date (or "unknown").
    9. Overall news outlook: Positive, Neutral or Negative, with a
       2-3 sentence reason and a confidence level (High/Medium/Low).
 
    State clearly whenever information is unavailable.
    """,
 
    agent=news_agent,
)
 
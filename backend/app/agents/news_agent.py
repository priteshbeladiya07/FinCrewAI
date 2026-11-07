from crewai import Agent
from app.config import llm
from app.tools.news_search_tool import search_financial_news
 
news_agent = Agent(
    role="Senior Financial News Research Analyst",
    goal=(
        "Produce an accurate, de-duplicated, source-verified summary of "
        "the last month's news about {company}, including negative "
        "developments, with every figure traceable to a retrieved article."
    ),
    backstory=(
        "You are a financial news analyst who works like a fact-checker. "
        "You merge articles about the same event into one item, prefer "
        "official filings and major publishers, never use social media, "
        "and always state a figure's scope (group/segment, consolidated, "
        "YoY/QoQ). When sources disagree you report the conflict instead "
        "of choosing silently. You never invent facts, dates or numbers."
    ),
    tools=[search_financial_news],
    llm=llm,
    verbose=True,           # keeps console panels out of the saved report
    allow_delegation=False,
    max_iter=6,
)
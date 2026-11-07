
from crewai import Crew, Process

# Import all six agents
from app.agents.news_agent import news_agent
from app.agents.fundamental_agent import fundamental_agent
from app.agents.technical_agent import technical_agent
from app.agents.sentiment_agent import sentiment_agent
from app.agents.risk_agent import risk_agent
from app.agents.investment_agent import investment_agent

# Import all six tasks
from app.tasks.news_task import news_task
from app.tasks.fundamental_task import fundamental_task
from app.tasks.technical_task import technical_task
from app.tasks.sentiment_task import sentiment_task
from app.tasks.risk_task import risk_task
from app.tasks.investment_task import investment_task


def _replace_report_placeholders(task, replacements):
    """Replace report placeholders with task-context instructions."""

    for placeholder, replacement in replacements.items():
        token = "{" + placeholder + "}"

        task.description = task.description.replace(
            token, replacement
        )

        task.expected_output = task.expected_output.replace(
            token, replacement
        )


def create_financial_research_crew():

    # -----------------------------------------------
    # STAGE 1: Three parallel research agents
    # -----------------------------------------------

    news_task.async_execution = False
    fundamental_task.async_execution = False
    technical_task.async_execution = False

    # -----------------------------------------------
    # STAGE 2: Sentiment receives all three reports
    # -----------------------------------------------

    sentiment_task.async_execution = False

    sentiment_task.context = [
        news_task,
        fundamental_task,
        technical_task
    ]

    _replace_report_placeholders(
        sentiment_task,
        {
            "news_report":
                "the completed News Research report in task context",

            "fundamental_report":
                "the completed Fundamental Analysis report in task context",

            "technical_report":
                "the completed Technical Analysis report in task context",
        }
    )

    # -----------------------------------------------
    # STAGE 3: Risk receives sentiment report
    # -----------------------------------------------

    risk_task.async_execution = False
    risk_task.context = [sentiment_task]

    _replace_report_placeholders(
        risk_task,
        {
            "sentiment_report":
                "the completed Sentiment Analysis report in task context"
        }
    )

    # -----------------------------------------------
    # STAGE 4: Investment receives sentiment + risk
    # -----------------------------------------------

    investment_task.async_execution = False

    investment_task.context = [
        sentiment_task,
        risk_task
    ]

    _replace_report_placeholders(
        investment_task,
        {
            "sentiment_report":
                "the completed Sentiment Analysis report in task context",

            "risk_report":
                "the completed Risk Analysis report in task context",
        }
    )

    # -----------------------------------------------
    # STAGE 5: Create crew
    # -----------------------------------------------

    financial_research_crew = Crew(
        agents=[
            news_agent,
            fundamental_agent,
            technical_agent,
            sentiment_agent,
            risk_agent,
            investment_agent
        ],

        tasks=[
            news_task,
            fundamental_task,
            technical_task,
            sentiment_task,
            risk_task,
            investment_task
        ],

        process=Process.sequential,

        verbose=True,

        cache=False
    )

    return financial_research_crew

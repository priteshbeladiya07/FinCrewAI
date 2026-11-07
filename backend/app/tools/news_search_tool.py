
import json
import os
import re

from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode

from tavily import TavilyClient
from crewai.tools import tool


# --------------------------------------------------------------------
# Constants
# --------------------------------------------------------------------

SOCIAL_DOMAINS = {
    "facebook.com",
    "x.com",
    "twitter.com",
    "instagram.com",
    "youtube.com",
    "tiktok.com",
    "reddit.com",
}

SOCIAL_EXCLUDE = [
    "facebook.com",
    "instagram.com",
    "x.com",
    "twitter.com",
    "youtube.com",
    "tiktok.com",
    "reddit.com",
    "tavily.com",
]

COMPANY_DOMAINS = {
    "ril.com",
    "jio.com",
}

EXCHANGE_DOMAINS = {
    "bseindia.com",
    "nseindia.com",
}

TRUSTED_DOMAINS = {
    "reuters.com",
    "bloomberg.com",
    "economictimes.com",
    "moneycontrol.com",
    "business-standard.com",
    "livemint.com",
    "thehindu.com",
    "thehindubusinessline.com",
    "cnbctv18.com",
    "spglobal.com",
}

# Aliases help retrieve relevant articles when the full company name
COMPANY_ALIASES = {
    "reliance industries": [
        "reliance industries",
        "reliance industries limited",
        "reliance industries ltd",
    ],
}

MAX_RESULTS_PER_QUERY = 8
MAX_FINAL_RESULTS = 15
MAX_NEGATIVE_RESULTS = 5
MAX_CONTENT_LENGTH = 2500


# --------------------------------------------------------------------
# Text and URL helpers
# --------------------------------------------------------------------

def normalize_title(title: str) -> str:
    """Normalize a headline for exact duplicate detection."""
    title = title.lower().strip()
    title = re.sub(r"[^\w\s]", "", title)
    return re.sub(r"\s+", " ", title)


def get_domain(url: str) -> str:
    """Extract a normalized hostname from a URL."""
    try:
        return (
            urlsplit(url).hostname or ""
        ).lower().removeprefix("www.")
    except Exception:
        return ""


def domain_matches(domain: str, domains) -> bool:
    """Match a domain and its subdomains safely."""
    return any(
        domain == candidate or domain.endswith("." + candidate)
        for candidate in domains
    )


def normalize_url(url: str) -> str:
    """Remove fragments and common tracking parameters."""
    if not url:
        return ""

    try:
        parsed = urlsplit(url.strip())

        tracking_parameters = {
            "fbclid",
            "gclid",
            "mc_cid",
            "mc_eid",
        }

        query = [
            (key, value)
            for key, value in parse_qsl(parsed.query)
            if not key.lower().startswith("utm_")
            and key.lower() not in tracking_parameters
        ]

        return urlunsplit((
            parsed.scheme.lower(),
            parsed.netloc.lower(),
            parsed.path.rstrip("/"),
            urlencode(query),
            "",
        ))

    except Exception:
        return url.strip()


# --------------------------------------------------------------------
# Company relevance
# --------------------------------------------------------------------

def get_company_aliases(company: str) -> list[str]:
    """Return company name and configured aliases."""
    normalized = company.lower().strip()

    for known_company, aliases in COMPANY_ALIASES.items():
        if normalized == known_company:
            return aliases

    return [normalized]

def is_relevant_article(
    company: str,
    title: str,
    content: str,
) -> bool:
    """
    Check whether an article explicitly mentions the target company.
    Uses word boundaries to avoid accidental partial matches.
    """

    aliases = get_company_aliases(company)

    title_text = title.lower()
    content_text = content.lower()

    # Give headlines more importance than article snippets.
    for alias in aliases:
        alias = alias.lower().strip()

        if not alias:
            continue

        pattern = (
            r"(?<!\w)"
            + re.escape(alias)
            + r"(?!\w)"
        )

        if (
            re.search(pattern, title_text)
            or re.search(pattern, content_text)
        ):
            return True

    return False

# --------------------------------------------------------------------
# Source classification
# --------------------------------------------------------------------

def classify_source(url: str) -> str:
    """Classify the publisher without assuming all official pages are filings."""
    domain = get_domain(url)

    if domain_matches(domain, SOCIAL_DOMAINS):
        return "social_platform_unverified"

    if domain_matches(domain, EXCHANGE_DOMAINS):
        return "exchange_official_source"

    if domain_matches(domain, COMPANY_DOMAINS):
        return "company_official_source"

    if domain_matches(domain, TRUSTED_DOMAINS):
        return "trusted_publisher"

    return "other_publisher"


def source_tier(source_type: str) -> int:
    """
    Tier 1: Official company/exchange sources.
    Tier 2: Recognized publishers.
    Tier 3: Other publishers.
    """
    if source_type in {
        "company_official_source",
        "exchange_official_source",
    }:
        return 1

    if source_type == "trusted_publisher":
        return 2

    return 3


# --------------------------------------------------------------------
# Date parsing
# --------------------------------------------------------------------

def parse_published_date(value):
    """Parse ISO 8601 and RFC 2822 publication dates."""
    if not value or not isinstance(value, str):
        return None

    try:
        parsed = datetime.fromisoformat(
            value.replace("Z", "+00:00")
        )
    except ValueError:
        try:
            parsed = parsedate_to_datetime(value)
        except (ValueError, TypeError, OverflowError):
            return None

    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)

    return parsed.astimezone(timezone.utc)


def is_within_date_range(
    published_date,
    cutoff: datetime,
    now: datetime,
) -> bool:
    """Reject articles outside the requested 30-day window."""
    return (
        published_date is not None
        and cutoff <= published_date <= now
    )


# --------------------------------------------------------------------
# Search query builder
# --------------------------------------------------------------------

def build_queries(
    company: str,
    focus: str = "",
) -> list[tuple[str, str]]:
    """Build separate queries for different financial-news angles."""

    queries = [
        (
            f"{company} latest news announcements",
            "general",
        ),
        (
            f"{company} quarterly results earnings revenue profit guidance",
            "financial",
        ),
        (
            f"{company} risks regulatory investigation penalty lawsuit "
            f"downgrade losses decline debt concerns",
            "risk_negative",
        ),
    ]

    if focus and focus.strip():
        queries.append((
            f"{company} {focus.strip()}",
            "focus",
        ))

    return queries


# --------------------------------------------------------------------
# Article scoring
# --------------------------------------------------------------------

def calculate_article_score(article: dict, now: datetime) -> float:
    """
    Rank articles using source quality, recency and Tavily relevance.

    This is a retrieval-ranking heuristic, not a factual accuracy score.
    """
    tier = article["source_tier"]

    source_score = {
        1: 3.0,
        2: 2.0,
        3: 1.0,
    }.get(tier, 0.0)

    published = article.get("published_date_iso")

    if published:
        published_dt = datetime.fromisoformat(published)
        age_days = max(
            0,
            (now - published_dt).total_seconds() / 86400,
        )
        recency_score = max(0.0, 2.0 - age_days / 15)
    else:
        recency_score = 0.0

    relevance = article.get("relevance_score")

    if relevance is None:
        relevance_score = 0.0
    else:
        relevance_score = max(0.0, min(1.0, relevance)) * 2.0

    return round(
        source_score + recency_score + relevance_score,
        3,
    )


# --------------------------------------------------------------------
# Article validation and deduplication
# --------------------------------------------------------------------

def prepare_article(
    item: dict,
    company: str,
    angle: str,
    cutoff: datetime,
    now: datetime,
):
    """Validate one Tavily result before allowing it into the collection."""

    title = (item.get("title") or "").strip()
    url = (item.get("url") or "").strip()
    content = (item.get("content") or "").strip()

    if not title or not url:
        return None

    parsed_date = parse_published_date(
        item.get("published_date")
    )

    # Unknown dates are not treated as confirmed recent news.
    if not is_within_date_range(parsed_date, cutoff, now):
        return None

    if not is_relevant_article(company, title, content):
        return None

    domain = get_domain(url)
    source_type = classify_source(url)

    if source_type == "social_platform_unverified":
        return None

    tier = source_tier(source_type)

    try:
        relevance = float(item.get("score"))
    except (TypeError, ValueError):
        relevance = None

    article = {
        "title": title[:300],
        "content": content[:MAX_CONTENT_LENGTH],
        "url": url,
        "normalized_url": normalize_url(url),
        "normalized_title": normalize_title(title),
        "source_domain": domain,
        "source_type": source_type,
        "source_tier": tier,
        "found_by_angle": angle,
        "published_date_iso": parsed_date.isoformat(),
        "date_status": "verified_provider_date",
        "relevance_score": relevance,
    }

    article["ranking_score"] = calculate_article_score(
        article,
        now,
    )

    return article


def deduplicate_articles(articles: list[dict]) -> list[dict]:
    """
    Deduplicate only after validation.

    If duplicates appear from multiple search angles, retain the best
    article and preserve all angles that discovered it.
    """
    unique = {}

    for article in articles:
        key = (
            article["normalized_url"]
            or article["normalized_title"]
        )

        if key not in unique:
            article["found_by_angles"] = [
                article["found_by_angle"]
            ]
            unique[key] = article
            continue

        existing = unique[key]

        if article["found_by_angle"] not in existing["found_by_angles"]:
            existing["found_by_angles"].append(
                article["found_by_angle"]
            )

        if article["ranking_score"] > existing["ranking_score"]:
            article["found_by_angles"] = existing["found_by_angles"]
            unique[key] = article

    return list(unique.values())


# --------------------------------------------------------------------
# Search execution
# --------------------------------------------------------------------

def execute_search(
    client: TavilyClient,
    company: str,
    focus: str,
    cutoff: datetime,
    now: datetime,
):
    """Run each search angle independently and collect valid articles."""

    collected = []
    errors = []
    angles_run = []

    for query, angle in build_queries(company, focus):

        try:
            response = client.search(
                query=query,
                search_depth="advanced",
                topic="news",
                time_range="month",
                max_results=MAX_RESULTS_PER_QUERY,
                exclude_domains=SOCIAL_EXCLUDE,
                include_answer=False,
                include_raw_content=False,
                timeout=30,
            )

            angles_run.append(angle)

        except Exception as exc:
            errors.append({
                "angle": angle,
                "error_type": type(exc).__name__,
            })
            continue

        for item in response.get("results", []):

            article = prepare_article(
                item=item,
                company=company,
                angle=angle,
                cutoff=cutoff,
                now=now,
            )

            if article:
                collected.append(article)

    return collected, errors, angles_run


# --------------------------------------------------------------------
# CrewAI Tool
# --------------------------------------------------------------------

@tool("Financial News Search")
def search_financial_news(company: str, focus: str = "") -> str:
    """
    Search for financial news published within the last 30 days.

    Searches general news, financial results and negative developments.
    Optionally searches an additional focus topic.

    Args:
        company: Company name, e.g. "Reliance Industries".
        focus: Optional topic, e.g. "quarterly results".

    Returns:
        JSON containing validated articles, source classifications,
        dates, search angles, ranking scores and search diagnostics.
    """

    if not isinstance(company, str) or not company.strip():
        return json.dumps({
            "status": "error",
            "error": "Company name is empty.",
        })

    company = company.strip()[:120]
    focus = focus.strip()[:120] if isinstance(focus, str) else ""

    api_key = os.getenv("TAVILY_API_KEY")

    if not api_key:
        return json.dumps({
            "status": "error",
            "error": "TAVILY_API_KEY is missing.",
        })

    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(days=30)

    try:
        client = TavilyClient(api_key=api_key)

        raw_articles, errors, angles_run = execute_search(
            client=client,
            company=company,
            focus=focus,
            cutoff=cutoff,
            now=now,
        )

    except Exception as exc:
        return json.dumps({
            "status": "error",
            "error": type(exc).__name__,
        })

    # Deduplicate after date, relevance and source validation.
    articles = deduplicate_articles(raw_articles)

    # Keep negative-news coverage visible instead of allowing general
    # articles to consume the entire result limit.
    negative_articles = [
        article
        for article in articles
        if "risk_negative" in article["found_by_angles"]
    ]

    negative_articles.sort(
        key=lambda article: article["ranking_score"],
        reverse=True,
    )

    selected_negative = negative_articles[:MAX_NEGATIVE_RESULTS]

    selected_keys = {
        article["normalized_url"]
        for article in selected_negative
    }

    remaining_articles = [
        article
        for article in articles
        if article["normalized_url"] not in selected_keys
    ]

    remaining_articles.sort(
        key=lambda article: article["ranking_score"],
        reverse=True,
    )

    final_articles = (
        selected_negative + remaining_articles
    )[:MAX_FINAL_RESULTS]

    # Remove internal fields from the final output.
    output_articles = []

    for article in final_articles:
        output_articles.append({
            key: value
            for key, value in article.items()
            if key not in {
                "normalized_url",
                "normalized_title",
                "ranking_score",
                "found_by_angle",
            }
        })

    return json.dumps({
        "status": "success" if output_articles else "no_results",
        "company": company,
        "requested_period": "Last 30 days",
        "cutoff_utc": cutoff.isoformat(),
        "retrieved_at_utc": now.isoformat(),
        "angles_searched": angles_run,
        "negative_news_search_run": (
            "risk_negative" in angles_run
        ),
        "negative_articles_found": len(negative_articles),
        "total_valid_articles": len(articles),
        "total_results": len(output_articles),
        "results": output_articles,
        "errors": errors,
        "important_notes": [
            "Only articles with provider publication dates inside "
            "the last 30 days are included.",
            "An article date supplied by the search provider is not "
            "independent verification of its publication date.",
            "Source tiers indicate publisher category, not proof "
            "that an individual claim is accurate.",
            "Ranking scores are retrieval heuristics, not factual "
            "accuracy or investment-quality scores.",
            "Articles found by multiple search angles are deduplicated "
            "and retain their discovery-angle metadata.",
            "Different articles may describe the same event. The "
            "research agent must consolidate event-level duplicates.",
            "Distinguish parent-company, subsidiary and segment news.",
            "Verify financial figures against official filings before "
            "presenting them as confirmed financial results.",
            "No results does not prove that no negative news exists.",
        ],
    }, indent=2, ensure_ascii=False)


import os
from pathlib import Path

from dotenv import load_dotenv
from crewai import LLM


# --------------------------------------------------
# 1. Disable unsupported cache breakpoint injection
# --------------------------------------------------

import crewai.llms.cache as crew_cache

crew_cache.mark_cache_breakpoint = lambda msg: msg


# --------------------------------------------------
# 2. Project configuration
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[1]

load_dotenv(BASE_DIR / ".env")


# --------------------------------------------------
# 3. API keys
# --------------------------------------------------

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")


if not MISTRAL_API_KEY:
    raise ValueError("MISTRAL_API_KEY is missing from .env")

if not TAVILY_API_KEY:
    raise ValueError("TAVILY_API_KEY is missing from .env")


# --------------------------------------------------
# 4. Shared Mistral LLM
# --------------------------------------------------
llm = LLM(
    model=os.environ["LLM_MODEL"],
    temperature=float(os.environ["LLM_TEMPERATURE"]),
    timeout=int(os.environ["LLM_TIMEOUT"]),
    max_tokens=int(os.environ["LLM_MAX_TOKENS"])
)
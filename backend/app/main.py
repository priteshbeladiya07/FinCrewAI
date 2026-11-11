
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import (
    health_routes,
    research_routes,
    reports,
    stock
)

from app.database.database import initialize_database


@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_database()
    yield


app = FastAPI(
    title="Financial Research AI",
    description="Six-Agent Financial Research and Stock Analysis API",
    version="1.0.0",
    lifespan=lifespan
)

# Allow requests from the Vite frontend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_routes.router, tags=["Health"])

app.include_router(
    research_routes.router,
    prefix="/api/v1/research",
    tags=["Financial Research"]
)

app.include_router(
    reports.router,
    prefix="/api/v1/research",
    tags=["Research Reports"]
)

app.include_router(
    stock.router,
    prefix="/api/v1/stocks",
    tags=["Stock Market Data"]
)

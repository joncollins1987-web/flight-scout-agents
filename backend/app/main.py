from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes_runs import router as runs_router
from app.api.routes_search import router as search_router
from app.core.logging import configure_logging
from app.db.engine import init_db


configure_logging()

app = FastAPI(title="flight-scout-agents", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(search_router)
app.include_router(runs_router)

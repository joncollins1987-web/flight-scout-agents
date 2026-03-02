from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.agents.orchestrator import orchestrator
from app.core.logging import get_logger
from app.schemas.request import SearchRequest
from app.schemas.response import FinalSearchResult


logger = get_logger(__name__)
router = APIRouter(prefix="/api", tags=["search"])


@router.post("/search", response_model=FinalSearchResult)
async def search_flights(request: SearchRequest) -> FinalSearchResult:
    try:
        return await orchestrator.run_search(request)
    except Exception as exc:  # noqa: BLE001
        logger.exception("search endpoint failed")
        raise HTTPException(status_code=500, detail=f"search failed: {exc}") from exc

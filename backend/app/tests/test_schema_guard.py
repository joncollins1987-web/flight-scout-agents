from __future__ import annotations

import pytest
from pydantic import BaseModel, ConfigDict

from app.agents.schema_guard import BranchHardFailError, SchemaGuard


class MiniSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    count: int


@pytest.mark.asyncio
async def test_schema_guard_repairs_once() -> None:
    guard = SchemaGuard()

    async def producer() -> dict:
        return {"count": "bad"}

    async def repair(_: dict, __: str) -> dict:
        return {"count": 2}

    result = await guard.run(producer=producer, schema=MiniSchema, repair_fn=repair)
    assert result.count == 2


@pytest.mark.asyncio
async def test_schema_guard_hard_fails_after_retry() -> None:
    guard = SchemaGuard()

    async def producer() -> dict:
        return {"count": "bad"}

    async def repair(_: dict, __: str) -> dict:
        return {"count": "still-bad"}

    with pytest.raises(BranchHardFailError):
        await guard.run(producer=producer, schema=MiniSchema, repair_fn=repair)

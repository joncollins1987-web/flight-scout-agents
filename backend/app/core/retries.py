from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable


async def with_retries(
    task_factory: Callable[[], Awaitable[object]],
    retries: int,
    backoff_ms: int,
) -> object:
    last_exc: Exception | None = None
    for attempt in range(retries + 1):
        try:
            return await task_factory()
        except Exception as exc:  # noqa: BLE001
            last_exc = exc
            if attempt >= retries:
                break
            await asyncio.sleep((backoff_ms / 1000.0) * (attempt + 1))
    assert last_exc is not None
    raise last_exc

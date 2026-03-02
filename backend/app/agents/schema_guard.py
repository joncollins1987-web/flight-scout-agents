from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any, TypeVar

from pydantic import BaseModel, ValidationError


T = TypeVar("T", bound=BaseModel)


class BranchHardFailError(RuntimeError):
    pass


class SchemaGuard:
    async def validate_or_repair(
        self,
        raw_output: Any,
        schema: type[T],
        repair_fn: Callable[[Any, str], Awaitable[Any]] | None = None,
    ) -> T:
        try:
            return schema.model_validate(raw_output)
        except ValidationError as first_error:
            if repair_fn is None:
                raise BranchHardFailError(f"schema validation failed: {first_error}") from first_error
            repaired = await repair_fn(raw_output, str(first_error))
            try:
                return schema.model_validate(repaired)
            except ValidationError as second_error:
                raise BranchHardFailError(f"schema validation failed after repair: {second_error}") from second_error

    async def run(
        self,
        producer: Callable[[], Awaitable[Any]],
        schema: type[T],
        repair_fn: Callable[[Any, str], Awaitable[Any]] | None = None,
    ) -> T:
        if repair_fn is None:
            async def _retry_with_fresh_output(_: Any, __: str) -> Any:
                return await producer()

            repair_fn = _retry_with_fresh_output
        raw_output = await producer()
        return await self.validate_or_repair(raw_output=raw_output, schema=schema, repair_fn=repair_fn)

from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from typing import AsyncIterator

from app.core.config import settings

try:
    from playwright.async_api import Browser, Playwright, async_playwright
except Exception:  # pragma: no cover
    Browser = object  # type: ignore[assignment]
    Playwright = object  # type: ignore[assignment]
    async_playwright = None


class BrowserPool:
    def __init__(self) -> None:
        self._lock = asyncio.Lock()
        self._playwright: Playwright | None = None
        self._browser: Browser | None = None

    async def _ensure(self) -> Browser:
        if async_playwright is None:
            raise RuntimeError("playwright is not installed")
        async with self._lock:
            if self._browser is not None:
                return self._browser
            self._playwright = await async_playwright().start()
            self._browser = await self._playwright.chromium.launch(headless=settings.playwright_headless)
            return self._browser

    @asynccontextmanager
    async def page(self) -> AsyncIterator[object]:
        browser = await self._ensure()
        context = await browser.new_context()
        page = await context.new_page()
        try:
            yield page
        finally:
            await context.close()

    async def close(self) -> None:
        async with self._lock:
            if self._browser is not None:
                await self._browser.close()
                self._browser = None
            if self._playwright is not None:
                await self._playwright.stop()
                self._playwright = None


browser_pool = BrowserPool()

"""Playwright browser management with stealth settings."""

import asyncio
from contextlib import asynccontextmanager
from playwright.async_api import async_playwright, Browser, Page


USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
]


class BrowserManager:
    """Manages a Playwright Chromium browser instance with stealth settings."""

    def __init__(self, headless: bool = True):
        self.headless = headless
        self._playwright = None
        self._browser: Browser | None = None

    async def start(self):
        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.launch(
            headless=self.headless,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
            ],
        )

    async def stop(self):
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()

    @asynccontextmanager
    async def get_page(self):
        """Get a new browser page with stealth settings."""
        import random

        context = await self._browser.new_context(
            viewport={"width": 1366, "height": 768},
            user_agent=random.choice(USER_AGENTS),
            locale="en-IN",
            timezone_id="Asia/Kolkata",
            extra_http_headers={
                "Accept-Language": "en-IN,en;q=0.9",
            },
        )

        # Stealth: override navigator.webdriver
        await context.add_init_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )

        page = await context.new_page()
        try:
            yield page
        finally:
            await page.close()
            await context.close()


@asynccontextmanager
async def create_browser(headless: bool = True):
    """Context manager for browser lifecycle."""
    manager = BrowserManager(headless=headless)
    await manager.start()
    try:
        yield manager
    finally:
        await manager.stop()

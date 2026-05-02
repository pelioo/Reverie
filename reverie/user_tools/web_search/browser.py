"""Playwright browser session management."""

import random
import time
from pathlib import Path
from typing import Any

from playwright.sync_api import Browser, BrowserContext, Page, sync_playwright

from .config import SearchConfig, ENGINE_URLS


class BrowserSession:
    """Manages Playwright browser sessions."""

    def __init__(
        self,
        config: SearchConfig | None = None,
        user_data_dir: str | None = None,
    ) -> None:
        self.config = config or SearchConfig()
        self._playwright = None
        self._browser: Browser | None = None
        self._context: BrowserContext | None = None
        self._user_data_dir = user_data_dir

    def __enter__(self) -> "BrowserSession":
        self.start()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.close()

    def start(self) -> None:
        """Start browser session."""
        if self._playwright is not None:
            return

        self._playwright = sync_playwright().start()

        # Launch browser
        launch_options: dict[str, Any] = {
            "headless": True,
            "args": [
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-web-security",
            ],
        }

        # Use existing profile if available
        if self._user_data_dir and Path(self._user_data_dir).exists():
            launch_options["user_data_dir"] = self._user_data_dir

        self._browser = self._playwright.chromium.launch(**launch_options)

        # Create context with anti-detection settings
        ua = random.choice(self.config.user_agents)
        self._context = self._browser.new_context(
            user_agent=ua,
            viewport={"width": 1920, "height": 1080},
            locale="zh-CN",
            extra_http_headers={
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            },
        )

    def new_page(self) -> Page:
        """Create a new page."""
        if self._context is None:
            raise RuntimeError("Browser not started. Call start() first.")
        return self._context.new_page()

    def close(self) -> None:
        """Close browser session."""
        if self._context:
            self._context.close()
            self._context = None
        if self._browser:
            self._browser.close()
            self._browser = None
        if self._playwright:
            self._playwright.stop()
            self._playwright = None

    @staticmethod
    def random_delay(min_sec: float = 0.5, max_sec: float = 2.0) -> None:
        """Sleep for a random duration."""
        time.sleep(random.uniform(min_sec, max_sec))

    @staticmethod
    def slow_type(page: Page, selector: str, text: str) -> None:
        """Type text slowly to simulate human input."""
        page.click(selector)
        page.keyboard.press("Control+a")
        for char in text:
            page.keyboard.type(char, delay=random.uniform(30, 80))
            time.sleep(random.uniform(0.01, 0.03))
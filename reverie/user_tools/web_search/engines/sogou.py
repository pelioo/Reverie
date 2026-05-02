"""Sogou search engine implementation."""

import time
from typing import TYPE_CHECKING

from playwright.sync_api import Page, TimeoutError as PlaywrightTimeout

from ..config import ENGINE_URLS
from ..models import SearchResponse, SearchResult
from .base import BaseEngine

if TYPE_CHECKING:
    from ..browser import BrowserSession


class SogouEngine(BaseEngine):
    """Sogou search engine."""

    name = "sogou"
    url = ENGINE_URLS["sogou"]

    def search(self, query: str, top_k: int) -> SearchResponse:
        """Search using Sogou."""
        start_time = time.time()
        page = self.session.new_page()

        try:
            # Navigate to Sogou
            search_url = self._get_search_url(query)
            page.goto(search_url, wait_until="domcontentloaded", timeout=10000)

            # Wait for results
            self.session.random_delay(1.0, 2.5)

            # Wait for results container
            try:
                page.wait_for_selector(".results", timeout=5000)
            except PlaywrightTimeout:
                try:
                    page.wait_for_selector(".vrwrap", timeout=3000)
                except PlaywrightTimeout:
                    pass

            # Extract results
            results = self._extract_results(page, top_k)

            elapsed_ms = int((time.time() - start_time) * 1000)
            return SearchResponse(
                query=query,
                engine=self.name,
                success=True,
                results=results,
                total_hits=len(results),
                response_time_ms=elapsed_ms,
            )

        except Exception as exc:
            elapsed_ms = int((time.time() - start_time) * 1000)
            return SearchResponse.from_error(query, self.name, str(exc))

        finally:
            page.close()

    def _extract_results(self, page: Page, top_k: int) -> list[SearchResult]:
        """Extract Sogou search results."""
        results = []

        try:
            # Find result items
            items = page.query_selector_all(".vrwrap")

            for i, item in enumerate(items[:top_k]):
                try:
                    # Get title and link
                    title_elem = item.query_selector(".vr-title a")
                    if not title_elem:
                        title_elem = item.query_selector("h3 a")

                    title = title_elem.inner_text() if title_elem else ""
                    url = title_elem.get_attribute("href") if title_elem else ""

                    # Get snippet
                    snippet_elem = item.query_selector(".space-txt")
                    if not snippet_elem:
                        snippet_elem = item.query_selector(".c-abstract")
                    snippet = snippet_elem.inner_text() if snippet_elem else ""

                    if title and url:
                        results.append(
                            SearchResult(
                                rank=i + 1,
                                title=title.strip(),
                                url=url.strip(),
                                snippet=snippet.strip()[:300],
                            )
                        )
                except Exception:
                    continue

        except Exception:
            pass

        return results

    def _get_search_url(self, query: str) -> str:
        """Get Sogou search URL."""
        import urllib.parse

        encoded_query = urllib.parse.quote(query)
        return f"{self.url}/web?query={encoded_query}"
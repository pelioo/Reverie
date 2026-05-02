"""Baidu search engine implementation."""

import time
from typing import TYPE_CHECKING

from playwright.sync_api import Page, TimeoutError as PlaywrightTimeout

from ..config import ENGINE_URLS
from ..models import SearchResponse, SearchResult
from .base import BaseEngine

if TYPE_CHECKING:
    from ..browser import BrowserSession


class BaiduEngine(BaseEngine):
    """Baidu search engine."""

    name = "baidu"
    url = ENGINE_URLS["baidu"]

    def search(self, query: str, top_k: int) -> SearchResponse:
        """Search using Baidu."""
        start_time = time.time()
        page = self.session.new_page()

        try:
            # Navigate to Baidu
            search_url = self._get_search_url(query)
            page.goto(search_url, wait_until="domcontentloaded", timeout=10000)

            # Wait for page to settle
            self.session.random_delay(1.5, 3.0)

            # Wait for results container
            try:
                page.wait_for_selector("#content_left", timeout=5000)
            except PlaywrightTimeout:
                try:
                    page.wait_for_selector(".c-container", timeout=3000)
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
        """Extract Baidu search results."""
        results = []

        try:
            # Find result items
            items = page.query_selector_all(".c-container")

            for i, item in enumerate(items[:top_k]):
                try:
                    # Skip ads and special containers
                    if "ec_ips_general" in (item.get_attribute("id") or ""):
                        continue
                    if "EC-result" in (item.get_attribute("class") or ""):
                        pass

                    # Get title and link - Baidu uses h3 a
                    title_elem = item.query_selector("h3 a")
                    if not title_elem:
                        title_elem = item.query_selector(".t a")

                    title = title_elem.inner_text() if title_elem else ""
                    url = title_elem.get_attribute("href") if title_elem else ""

                    # Get snippet - Baidu uses .c-abstract or .c-span-last
                    snippet_elem = item.query_selector(".c-abstract")
                    if not snippet_elem:
                        snippet_elem = item.query_selector(".c-span-last")
                    snippet = snippet_elem.inner_text() if snippet_elem else ""

                    # Skip empty results
                    if not title or not url:
                        continue

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
        """Get Baidu search URL."""
        import urllib.parse

        encoded_query = urllib.parse.quote(query)
        return f"{self.url}/s?wd={encoded_query}"
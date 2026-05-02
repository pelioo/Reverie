"""Base class for search engines."""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from ..models import SearchResponse, SearchResult

if TYPE_CHECKING:
    from ..browser import BrowserSession
    from playwright.sync_api import Page


class BaseEngine(ABC):
    """Base class for search engines."""

    name: str = "base"
    url: str = ""

    def __init__(self, session: "BrowserSession") -> None:
        self.session = session

    @abstractmethod
    def search(self, query: str, top_k: int) -> SearchResponse:
        """Perform search and return results."""
        ...

    @abstractmethod
    def _extract_results(self, page: "Page", top_k: int) -> list[SearchResult]:
        """Extract results from page."""
        ...

    @abstractmethod
    def _get_search_url(self, query: str) -> str:
        """Get search URL with query."""
        ...
"""Data models for web search tool."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class SearchEngine(Enum):
    """Supported search engines."""

    AUTO = "auto"
    BING = "bing"
    BAIDU = "baidu"
    SOGOU = "sogou"


@dataclass
class SearchResult:
    """Single search result."""

    rank: int
    title: str
    url: str
    snippet: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "rank": self.rank,
            "title": self.title,
            "url": self.url,
            "snippet": self.snippet,
        }


@dataclass
class SearchResponse:
    """Complete search response."""

    query: str
    engine: str
    success: bool
    results: list[SearchResult] = field(default_factory=list)
    total_hits: int = 0
    response_time_ms: int = 0
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "query": self.query,
            "engine": self.engine,
            "success": self.success,
            "results": [r.to_dict() for r in self.results],
            "total_hits": self.total_hits,
            "response_time_ms": self.response_time_ms,
            "error": self.error,
        }

    @classmethod
    def from_error(cls, query: str, engine: str, error: str) -> "SearchResponse":
        """Create an error response."""
        return cls(
            query=query,
            engine=engine,
            success=False,
            results=[],
            total_hits=0,
            response_time_ms=0,
            error=error,
        )
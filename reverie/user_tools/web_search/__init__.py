"""Web search tool package."""

from .browser import BrowserSession
from .config import ENGINE_URLS, DEFAULT_ENGINE_ORDER, SearchConfig
from .engines import BaiduEngine, BingEngine, BaseEngine, SogouEngine
from .models import SearchEngine, SearchResult, SearchResponse
from .searcher import SearchOrchestrator
from .tool import web_search_tool, get_web_search_binding

__all__ = [
    # Config
    "SearchConfig",
    "ENGINE_URLS",
    "DEFAULT_ENGINE_ORDER",
    # Models
    "SearchEngine",
    "SearchResult",
    "SearchResponse",
    # Core
    "BrowserSession",
    "SearchOrchestrator",
    # Engines
    "BaseEngine",
    "BingEngine",
    "BaiduEngine",
    "SogouEngine",
    # Tool
    "web_search_tool",
    "get_web_search_binding",
]
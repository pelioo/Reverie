"""Search orchestrator with fallback logic."""

import time
from typing import TYPE_CHECKING

from .config import DEFAULT_ENGINE_ORDER, SearchConfig
from .models import SearchEngine as SearchEngineEnum
from .models import SearchResponse
from .browser import BrowserSession
from .engines import BaiduEngine, BingEngine, SogouEngine

if TYPE_CHECKING:
    from .models import SearchEngine


class SearchOrchestrator:
    """Orchestrates search across multiple engines with fallback."""

    def __init__(self, config: SearchConfig | None = None) -> None:
        self.config = config or SearchConfig()

    def search(
        self,
        query: str,
        top_k: int = 5,
        engine: str = "auto",
    ) -> SearchResponse:
        """Search with fallback to multiple engines."""
        start_time = time.time()

        # Determine engine order
        if engine == "auto":
            engines_to_try = DEFAULT_ENGINE_ORDER
        else:
            engines_to_try = [engine]

        # Try each engine in order
        last_error = ""
        for engine_name in engines_to_try:
            try:
                result = self._search_with_engine(
                    query, top_k, engine_name
                )
                if result.success and len(result.results) > 0:
                    elapsed_ms = int((time.time() - start_time) * 1000)
                    result.response_time_ms = elapsed_ms
                    return result

            except Exception as exc:
                last_error = str(exc)
                continue

        # All engines failed
        elapsed_ms = int((time.time() - start_time) * 1000)
        error_msg = last_error or "All search engines failed"
        return SearchResponse(
            query=query,
            engine=engine,
            success=False,
            results=[],
            total_hits=0,
            response_time_ms=elapsed_ms,
            error=error_msg,
        )

    def _search_with_engine(
        self, query: str, top_k: int, engine_name: str
    ) -> SearchResponse:
        """Search using a specific engine."""
        with BrowserSession(config=self.config) as session:
            if engine_name == "bing":
                engine = BingEngine(session)
            elif engine_name == "baidu":
                engine = BaiduEngine(session)
            elif engine_name == "sogou":
                engine = SogouEngine(session)
            else:
                raise ValueError(f"Unknown engine: {engine_name}")

            return engine.search(query, top_k)
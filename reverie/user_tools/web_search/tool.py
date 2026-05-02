"""Web search tool implementation."""

from typing import Any

from ...tools.policy import ToolPermissionPolicy
from ...tools.registry import ToolBinding
from .config import SearchConfig
from .searcher import SearchOrchestrator


def web_search_tool(args: dict[str, Any], p: ToolPermissionPolicy) -> dict[str, Any]:
    """Perform web search using headless browser.

    Args:
        args: Tool arguments containing query and options.
        p: Tool permission policy (not used for web search).

    Returns:
        Search results dictionary.
    """
    # Extract parameters
    query = str(args.get("query", ""))
    top_k = int(args.get("top_k", 5))
    engine = str(args.get("engine", "auto"))

    # Validate query
    if not query:
        return {
            "success": False,
            "error": "Query cannot be empty",
            "query": "",
            "engine": engine,
            "results": [],
            "total_hits": 0,
        }

    # Limit top_k
    top_k = min(max(1, top_k), 20)

    # Validate engine
    valid_engines = ["auto", "bing", "baidu", "sogou"]
    if engine not in valid_engines:
        engine = "auto"

    # Perform search
    config = SearchConfig()
    orchestrator = SearchOrchestrator(config=config)
    response = orchestrator.search(query=query, top_k=top_k, engine=engine)

    # Return structured result
    return {
        "query": response.query,
        "engine": response.engine,
        "success": response.success,
        "results": [r.to_dict() for r in response.results],
        "total_hits": response.total_hits,
        "response_time_ms": response.response_time_ms,
        "error": response.error,
    }


def get_web_search_binding() -> ToolBinding:
    """Create web search tool binding."""
    return ToolBinding(
        name="web_search",
        description="Search the web using headless browser. "
        "Supports Bing, Baidu, and Sogou with automatic fallback.",
        handler=web_search_tool,
        input_schema={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query / 搜索关键词",
                },
                "top_k": {
                    "type": "integer",
                    "default": 5,
                    "description": "Number of results to return / 返回结果数量",
                    "minimum": 1,
                    "maximum": 20,
                },
                "engine": {
                    "type": "string",
                    "enum": ["auto", "bing", "baidu", "sogou"],
                    "default": "auto",
                    "description": "Search engine to use: auto=binary fallback, bing/baidu/sogou=specific / "
                    "搜索引擎：auto=自动降级, bing/baidu/sogou=指定",
                },
            },
            "required": ["query"],
        },
    )
"""Web search tool configuration."""

from dataclasses import dataclass


@dataclass
class SearchConfig:
    """Search tool configuration."""

    # Result limits
    max_results: int = 20
    default_results: int = 5

    # Timeouts (milliseconds)
    single_timeout_ms: int = 15000
    total_timeout_ms: int = 45000

    # Browser settings
    enable_images: bool = False
    enable_css: bool = True

    # User agents
    user_agents: tuple[str, ...] = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 "
        "Firefox/121.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    )


# Default search engines in priority order
DEFAULT_ENGINE_ORDER = ["bing", "baidu", "sogou"]

# Engine URLs
ENGINE_URLS = {
    "bing": "https://cn.bing.com",
    "baidu": "https://www.baidu.com",
    "sogou": "https://www.sogou.com",
}
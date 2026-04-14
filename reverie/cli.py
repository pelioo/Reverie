from __future__ import annotations

import argparse
import os

from dotenv import load_dotenv

from .tui import TuiConfig, TuiController, build_app_components


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Reverie CLI")
    parser.add_argument("--message", "-m", action="append", default=[], help="Preloaded user messages; can repeat")
    parser.add_argument("--session-id", default=os.getenv("REVERIE_SESSION_ID", "default"), help="Session ID")
    parser.add_argument(
        "--mode",
        default=os.getenv("REVERIE_RUN_MODE", "Murmur"),
        choices=["Reverie", "Lucid", "Murmur"],
        help="Run mode: Reverie (dream) / Lucid (chat) / Murmur (hybrid)",
    )
    parser.add_argument(
        "--workspace-root",
        default=os.getenv("REVERIE_WORKSPACE_ROOT", "workspace"),
        help="Runtime workspace root (memory/runtime/tool outputs live here)",
    )
    parser.add_argument("--ticks", type=int, default=-1, help="Scheduler ticks; -1 runs until /quit")
    parser.add_argument("--max-idle", type=float, default=60, help="Max idle seconds before autonomous turn")
    parser.add_argument("--model", default=os.getenv("REVERIE_MODEL", "gpt-4o-mini"), help="Model name")
    parser.add_argument("--api-key", default=os.getenv("OPENAI_API_KEY", ""), help="OpenAI-compatible API key")
    parser.add_argument(
        "--base-url",
        default=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
        help="OpenAI-compatible base URL",
    )
    parser.add_argument("--memory-dir", default=os.getenv("REVERIE_MEMORY_DIR", "memory"), help="Markdown memory directory (relative to workspace-root)")
    parser.add_argument("--temperature", type=float, default=0.7, help="Sampling temperature")
    return parser


def main() -> None:
    load_dotenv()
    args = build_parser().parse_args()

    if not args.api_key:
        raise SystemExit("Missing OPENAI_API_KEY or --api-key (configure it in .env)")

    components = build_app_components(
        session_id=args.session_id,
        model=args.model,
        api_key=args.api_key,
        base_url=args.base_url,
        workspace_root=args.workspace_root,
        memory_dir=args.memory_dir,
        temperature=args.temperature,
        max_idle=args.max_idle,
        messages=args.message,
    )
    if args.mode == "Reverie":
        components.scheduler.run(
            ticks=args.ticks,
            print_user_turn=False,
            print_autonomous_turn=True,
            run_mode=args.mode,
        )
        return

    tui = TuiController(
        queue=components.queue,
        scheduler=components.scheduler,
        config=TuiConfig(session_id=args.session_id, ticks=args.ticks, model=args.model, run_mode=args.mode),
    )
    tui.run()


if __name__ == "__main__":
    main()

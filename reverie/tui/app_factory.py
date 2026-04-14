from __future__ import annotations

import os
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from ..context import ContextManager
from ..llm import LLMConfig, OpenAICompatibleClient
from ..memory import MarkdownMemoryStore, MemoryManager
from ..orchestrator import InputEvent
from ..orchestrator.runner import TurnOrchestrator
from ..scheduler import InputQueue, SchedulerLoop, SchedulerState
from ..session_state import SessionStateManager, SessionStateStore
from ..subconscious import SubconsciousIntentRecorder, SubconsciousPrompter
from ..tools import create_default_tool_runtime


@dataclass(slots=True)
class AppComponents:
    queue: InputQueue
    orchestrator: TurnOrchestrator
    scheduler: SchedulerLoop
    session_state: SessionStateManager


def preload_messages(queue: InputQueue, messages: Iterable[str], session_id: str) -> None:
    for msg in messages:
        queue.put(InputEvent(content=msg, session_id=session_id))


def _ensure_soul_memory_file(workspace_path: Path, memory_path: Path) -> Path:
    episodic_dir = memory_path / "episodic"
    episodic_dir.mkdir(parents=True, exist_ok=True)
    soul_target = episodic_dir / "soul.md"
    if soul_target.exists():
        return soul_target

    soul_template = os.getenv("REVERIE_SOUL_TEMPLATE", "souls/soul.md").strip() or "souls/soul.md"
    template_path = Path(soul_template)
    if not template_path.is_absolute():
        template_path = Path.cwd() / template_path

    if template_path.exists() and template_path.is_file():
        shutil.copyfile(template_path, soul_target)
    else:
        soul_target.write_text(
            "# Soul\n\nMaintain your long-term identity constraints, growth direction, and behavioral principles here.\n",
            encoding="utf-8",
        )
    return soul_target


def build_app_components(
    *,
    session_id: str,
    model: str,
    api_key: str,
    base_url: str,
    workspace_root: str,
    memory_dir: str,
    temperature: float,
    max_idle: float,
    messages: Iterable[str],
) -> AppComponents:
    queue = InputQueue()
    preload_messages(queue, messages, session_id=session_id)

    llm_config = LLMConfig(model=model, api_key=api_key, base_url=base_url)
    llm_client = OpenAICompatibleClient(llm_config)

    workspace_path = Path(workspace_root)
    memory_path = Path(memory_dir)
    if not memory_path.is_absolute():
        memory_path = workspace_path / memory_path

    session_dir = workspace_path / "runtime" / "sessions"
    tool_results_dir = workspace_path / "runtime" / "tool_results"
    subconscious_dir = workspace_path / "runtime" / "subconscious_intents"

    memory_store = MarkdownMemoryStore(memory_dir=str(memory_path))
    memory_manager = MemoryManager(memory_store)
    soul_memory_path = _ensure_soul_memory_file(workspace_path=workspace_path, memory_path=memory_path)
    soul_content = soul_memory_path.read_text(encoding="utf-8").strip()

    context_manager = ContextManager(memory_manager=memory_manager, soul_content=soul_content)
    session_store = SessionStateStore(base_dir=str(session_dir))
    session_state = SessionStateManager(store=session_store, session_id=session_id)
    tool_runtime = create_default_tool_runtime(
        memory_manager=memory_manager,
        workspace_root=str(workspace_path),
        raw_dir=str(tool_results_dir),
    )

    orchestrator = TurnOrchestrator(
        llm_client=llm_client,
        context_manager=context_manager,
        session_state=session_state,
        tool_runtime=tool_runtime,
        temperature=temperature,
    )
    available_tools = [
        {"name": spec.name, "description": spec.description}
        for spec in tool_runtime.available_tools()
    ]
    prompter = SubconsciousPrompter(
        llm_client=llm_client,
        available_tools=available_tools,
        soul_content=soul_content,
    )
    intent_recorder = SubconsciousIntentRecorder(base_dir=str(subconscious_dir))
    scheduler = SchedulerLoop(
        queue=queue,
        orchestrator=orchestrator,
        prompter=prompter,
        state=SchedulerState(max_idle_interval=max_idle),
        session_state=session_state,
        intent_recorder=intent_recorder,
    )
    return AppComponents(queue=queue, orchestrator=orchestrator, scheduler=scheduler, session_state=session_state)

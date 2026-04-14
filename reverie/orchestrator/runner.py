from __future__ import annotations

from uuid import uuid4

from ..context import ContextManager
from ..llm import OpenAICompatibleClient
from ..session_state import SessionStateManager
from ..tools import ToolRuntime
from .models import AutonomousIntent, InputEvent, TurnResult
from .helpers import compose_response
from .tool_loop import ToolLoopRunner


class TurnOrchestrator:
    """Turn executor with real LLM calls, memory, and tool-runtime loop."""

    def __init__(
        self,
        llm_client: OpenAICompatibleClient,
        context_manager: ContextManager,
        session_state: SessionStateManager,
        tool_runtime: ToolRuntime,
        temperature: float = 0.7,
    ) -> None:
        self.llm_client = llm_client
        self.context_manager = context_manager
        self.session_state = session_state
        self.tool_runtime = tool_runtime
        self.temperature = temperature
        self._tool_loop = ToolLoopRunner(
            llm_client=llm_client,
            tool_runtime=tool_runtime,
            session_state=session_state,
            temperature=temperature,
        )

    def run_user_turn(self, event: InputEvent) -> TurnResult:
        turn_id = f"turn-user-{uuid4().hex[:8]}"
        self.session_state.on_turn_start(turn_id=turn_id, mode="user", goal="respond_user", user_input=event.content)

        packet = self.context_manager.build_for_user_turn(event.content)
        reply, tool_notes = self._tool_loop.run(packet.messages)
        response = compose_response("reverie", reply, tool_notes)

        self.session_state.on_turn_end(turn_type="user", response=response, memory_write=None)
        return TurnResult(turn_type="user", response=response, memory_write=None)

    def run_autonomous_turn(self, intent: AutonomousIntent) -> TurnResult:
        turn_id = f"turn-auto-{uuid4().hex[:8]}"
        self.session_state.on_turn_start(
            turn_id=turn_id,
            mode="autonomous",
            goal=intent.kind,
            user_input=None,
        )

        if intent.kind == "rest":
            response = (
                f"[auto-turn] Decided to rest for {intent.cooldown_hint_seconds or 1}s; "
                f"reason: {intent.rationale}"
            )
            self.session_state.on_turn_end(turn_type="autonomous", response=response, memory_write=None)
            return TurnResult(
                turn_type="autonomous",
                response=response,
            )

        packet = self.context_manager.build_for_autonomous_turn(
            intent_prompt=intent.prompt,
            intent_kind=intent.kind,
        )
        reply, tool_notes = self._tool_loop.run(packet.messages)
        response = compose_response(f"auto-turn:{intent.kind}", reply, tool_notes)

        self.session_state.on_turn_end(turn_type="autonomous", response=response, memory_write=None)
        return TurnResult(turn_type="autonomous", response=response, memory_write=None)


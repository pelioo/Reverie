from __future__ import annotations

import threading
import time
from datetime import datetime

from ..orchestrator.runner import TurnOrchestrator
from ..session_state import SessionStateManager
from ..subconscious import SubconsciousIntentRecorder, SubconsciousPrompter, SubconsciousState
from .queue import InputQueue
from .state import SchedulerState


class SchedulerLoop:
    """Scheduler loop.

    Modes:
    - Murmur: user input + autonomous intent
    - Reverie: autonomous intent only
    - Lucid: user input only
    """

    def __init__(
        self,
        queue: InputQueue,
        orchestrator: TurnOrchestrator,
        prompter: SubconsciousPrompter,
        state: SchedulerState | None = None,
        session_state: SessionStateManager | None = None,
        intent_recorder: SubconsciousIntentRecorder | None = None,
    ) -> None:
        self.queue = queue
        self.orchestrator = orchestrator
        self.prompter = prompter
        self.state = state or SchedulerState()
        self.sub_state = SubconsciousState()
        self.session_state = session_state
        self.intent_recorder = intent_recorder

    def run(
        self,
        ticks: int = 20,
        *,
        print_user_turn: bool = True,
        print_autonomous_turn: bool = True,
        run_mode: str = "Murmur",
        stop_event: threading.Event | None = None,
        input_gate: threading.Event | None = None,
    ) -> None:
        mode = (run_mode or "Murmur").strip()
        step = 0
        while ticks < 0 or step < ticks:
            if stop_event is not None and stop_event.is_set():
                break
            step += 1

            if mode != "Reverie":
                event = self.queue.get()
                if event is not None:
                    result = self.orchestrator.run_user_turn(event)
                    self.state.last_user_activity_at = datetime.now()
                    if print_user_turn:
                        print(result.response)
                    if self.session_state:
                        self.session_state.checkpoint()
                    if input_gate is not None and not self.queue.has_user_input():
                        input_gate.set()
                    continue

            if self.session_state and self.session_state.is_sleeping():
                time.sleep(0.2)
                continue

            if mode != "Lucid":
                should_auto = self._should_run_autonomous()
                if should_auto:
                    intent = self.prompter.generate(self.sub_state)
                    if self.intent_recorder:
                        sid = self.session_state.session_id if self.session_state else None
                        self.intent_recorder.record(intent, session_id=sid)
                    result = self.orchestrator.run_autonomous_turn(intent)
                    if print_autonomous_turn:
                        print(result.response)
                    self.sub_state.last_turn_response = result.response
                    self.sub_state.autonomous_turn_count += 1
                    self.state.last_autonomous_turn_at = datetime.now()

                    if intent.kind == "rest":
                        seconds = float(intent.cooldown_hint_seconds or 1)
                        if self.session_state:
                            self.session_state.set_sleep(seconds)
                        time.sleep(seconds)
                    if self.session_state:
                        self.session_state.checkpoint()
                    continue

            time.sleep(0.2)

    def _should_run_autonomous(self) -> bool:
        now = time.time()
        last = self.state.last_autonomous_turn_at.timestamp() if self.state.last_autonomous_turn_at else 0.0
        return (now - last) >= self.state.max_idle_interval

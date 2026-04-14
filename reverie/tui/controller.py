from __future__ import annotations

import threading
import termios
from dataclasses import dataclass

from ..orchestrator import InputEvent
from ..scheduler import InputQueue, SchedulerLoop


@dataclass(slots=True)
class TuiConfig:
    session_id: str
    ticks: int
    model: str
    run_mode: str


class TuiController:
    def __init__(self, *, queue: InputQueue, scheduler: SchedulerLoop, config: TuiConfig) -> None:
        self.queue = queue
        self.scheduler = scheduler
        self.config = config
        self.stop_event = threading.Event()
        self.input_gate = threading.Event()
        if queue.has_user_input():
            self.input_gate.clear()
        else:
            self.input_gate.set()

    def run(self) -> None:
        self._print_banner()
        worker = threading.Thread(target=self._input_worker, daemon=True)
        worker.start()
        self.scheduler.run(
            ticks=self.config.ticks,
            print_user_turn=True,
            print_autonomous_turn=self.config.run_mode == "Murmur",
            run_mode=self.config.run_mode,
            stop_event=self.stop_event,
            input_gate=self.input_gate,
        )
        self.stop_event.set()
        print("[reverie] loop finished")

    def _print_banner(self) -> None:
        print("[reverie] started; loop running in the background.")
        print("[reverie] type a message and press Enter; use /quit to exit.")
        print(
            f"[reverie] session={self.config.session_id} model={self.config.model} mode={self.config.run_mode} ticks={self.config.ticks}"
        )

    def _input_worker(self) -> None:
        while not self.stop_event.is_set():
            self.input_gate.wait()
            if self.stop_event.is_set():
                break
            try:
                try:
                    termios.tcflush(0, termios.TCIFLUSH)
                except Exception:
                    pass
                line = input("you> ").strip()
            except EOFError:
                self.stop_event.set()
                break
            if not line:
                continue
            if line == "/quit":
                print("[reverie] exiting...")
                self.stop_event.set()
                break
            self.queue.put(InputEvent(content=line, session_id=self.config.session_id))
            self.input_gate.clear()
            print("[reverie] input received, processing...")

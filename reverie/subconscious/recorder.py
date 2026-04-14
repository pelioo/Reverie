from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime
from pathlib import Path

from ..orchestrator import AutonomousIntent


class SubconsciousIntentRecorder:
    """Persist autonomous intents into standalone JSON files."""

    def __init__(self, base_dir: str = "runtime/subconscious_intents") -> None:
        self.base = Path(base_dir)
        self.base.mkdir(parents=True, exist_ok=True)

    def record(self, intent: AutonomousIntent, session_id: str | None = None) -> str:
        ts = datetime.now().strftime("%Y%m%d-%H%M%S")
        filename = f"{ts}-{intent.kind}-{intent.id[:8]}.json"
        path = self.base / filename

        payload = {
            "recorded_at": datetime.now().isoformat(timespec="seconds"),
            "session_id": session_id,
            "intent": asdict(intent),
        }
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return str(path)

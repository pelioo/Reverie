from __future__ import annotations

import json
import random
from datetime import datetime
from typing import Any

from ..llm import OpenAICompatibleClient
from ..orchestrator import AutonomousIntent
from .state import SubconsciousState


class SubconsciousPrompter:
    """LLM-driven prompter with rule fallback.

    Primary strategy:
    - Let the model decide the next intent type and cooldown.
    - Fall back to a weighted heuristic when LLM is unavailable.
    """

    _ALLOWED_KINDS = {
        "reflect",
        "consolidate",
        "explore",
        "practice",
        "curate",
        "pursue_goal",
        "rest",
    }

    def __init__(
        self,
        llm_client: OpenAICompatibleClient | None = None,
        temperature: float = 0.4,
        available_tools: list[dict[str, Any]] | None = None,
        soul_content: str = "",
    ) -> None:
        self.llm_client = llm_client
        self.temperature = temperature
        self.available_tools = available_tools or []
        self.soul_content = soul_content.strip()
        self.available_tool_names = sorted(
            {
                str(tool.get("name", ""))
                for tool in self.available_tools
                if isinstance(tool, dict) and tool.get("name")
            }
        )

    def generate(self, state: SubconsciousState) -> AutonomousIntent:
        intent = None
        if self.llm_client is not None:
            intent = self._generate_with_llm(state)
        if intent is None:
            intent = self._fallback_intent(state)

        state.last_intent_kind = intent.kind
        state.last_intent_prompt = intent.prompt
        state.last_intent_rationale = intent.rationale
        state.last_intent_at = datetime.now()
        state.last_cooldown_seconds = intent.cooldown_hint_seconds
        return intent

    def _generate_with_llm(self, state: SubconsciousState) -> AutonomousIntent | None:
        prompt = self._build_prompt(state)
        try:
            response = self.llm_client.complete(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a subconscious prompter responsible for generating the next autonomous intent and rest duration.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=self.temperature,
            )
        except Exception:
            return None

        payload = self._extract_json_payload(response.content)
        if not payload:
            return None
        return self._build_intent_from_payload(payload, state)

    def _build_prompt(self, state: SubconsciousState) -> str:
        last = state.last_intent_kind or "none"
        last_prompt = (state.last_intent_prompt or "").strip() or "(none)"
        last_rationale = (state.last_intent_rationale or "").strip() or "(none)"
        last_response = (state.last_turn_response or "").strip() or "(none)"
        cooldown = state.last_cooldown_seconds or 0
        tools_text = self._render_available_tools_for_prompt()
        return """
You are a subconscious prompter that assigns the next self-driven task to the current agent.

Derive the next intent based on the previous subconscious intent and the previous actual output.
You must output JSON with only these fields:
kind, prompt, rationale, priority, suggested_tools, expected_memory_write, cooldown_hint_seconds

Hard constraints:
- kind must be one of: reflect, consolidate, explore, practice, curate, pursue_goal, rest
- prompt must be conversational, specific, and executable, using second-person voice (e.g., "you should...")
- rationale should briefly explain why this follows from the previous state
- priority must be between 0 and 1
- suggested_tools must be chosen only from the available tools
- cooldown_hint_seconds: only when kind=rest, suggest an integer 1~{max_sleep}; otherwise set to null

Previous turn:
- last_intent_kind: {last_intent}
- last_intent_prompt: {last_prompt}
- last_intent_rationale: {last_rationale}
- last_turn_response: {last_response}
- last_cooldown_seconds: {last_cooldown}

Treat soul.md as critical: it defines long-term identity, principles, and growth direction.
If self-correction or growth is needed, you may guide a later turn to use write_file to update workspace/memory/episodic/soul.md.

Current soul.md content:
{soul}

Available tools (name + description):
{available_tools}
""".strip().format(
            last_intent=last,
            last_prompt=last_prompt,
            last_rationale=last_rationale,
            last_response=last_response,
            last_cooldown=cooldown,
            max_sleep=state.max_sleep_seconds,
            soul=self._render_soul_for_prompt(),
            available_tools=tools_text,
        )

    def _extract_json_payload(self, text: str) -> dict[str, Any] | None:
        if not text:
            return None
        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1 or end <= start:
            return None
        try:
            return json.loads(text[start : end + 1])
        except Exception:
            return None

    def _build_intent_from_payload(self, payload: dict[str, Any], state: SubconsciousState) -> AutonomousIntent | None:
        kind = str(payload.get("kind", "")).strip()
        if kind not in self._ALLOWED_KINDS:
            return None

        prompt = str(payload.get("prompt", "")).strip() or self._default_prompt(kind)
        rationale = str(payload.get("rationale", "")).strip() or "Generated after the model assessed the current state."

        try:
            priority = float(payload.get("priority", 0.6))
        except (TypeError, ValueError):
            priority = 0.6
        priority = min(max(priority, 0.0), 1.0)

        suggested_tools = payload.get("suggested_tools")
        if not isinstance(suggested_tools, list):
            suggested_tools = []
        suggested_tools = [str(item) for item in suggested_tools]
        if self.available_tool_names:
            allowed = set(self.available_tool_names)
            suggested_tools = [name for name in suggested_tools if name in allowed]

        expected_memory_write = payload.get("expected_memory_write")
        if not isinstance(expected_memory_write, bool):
            expected_memory_write = kind != "rest"

        cooldown = payload.get("cooldown_hint_seconds")
        if cooldown is None and kind == "rest":
            cooldown = 2
        if cooldown is not None:
            try:
                cooldown = int(cooldown)
            except (TypeError, ValueError):
                cooldown = None
        if cooldown is not None:
            cooldown = min(max(cooldown, 1), state.max_sleep_seconds)

        return AutonomousIntent(
            kind=kind,
            prompt=prompt,
            rationale=rationale,
            priority=priority,
            suggested_tools=suggested_tools,
            expected_memory_write=expected_memory_write,
            cooldown_hint_seconds=cooldown,
        )

    def _fallback_intent(self, state: SubconsciousState) -> AutonomousIntent:
        options = [
            ("explore", 0.3),
            ("reflect", 0.2),
            ("consolidate", 0.15),
            ("practice", 0.1),
            ("curate", 0.1),
            ("pursue_goal", 0.1),
            ("rest", 0.05),
        ]
        if state.last_intent_kind == "rest":
            options = [(k, w * 0.6 if k == "rest" else w) for k, w in options]

        pick = random.random() * sum(w for _, w in options)
        cumulative = 0.0
        choice = "explore"
        for kind, weight in options:
            cumulative += weight
            if pick <= cumulative:
                choice = kind
                break

        return AutonomousIntent(
            kind=choice,
            prompt=self._default_prompt(choice),
            rationale="Weighted heuristic used when the LLM is unavailable.",
            priority=0.6,
            suggested_tools=["list_files"] if choice == "explore" and "list_files" in self.available_tool_names else [],
            expected_memory_write=choice != "rest",
            cooldown_hint_seconds=2 if choice == "rest" else None,
        )

    @staticmethod
    def _default_prompt(kind: str) -> str:
        prompts = {
            "reflect": "You should review the last outcome and identify one actionable improvement.",
            "consolidate": "You should consolidate recent outputs into clear conclusions and fill any gaps.",
            "explore": "You should investigate one related lead and decide whether it is worth pursuing.",
            "practice": "You should run a small validation to confirm the current approach is reliable.",
            "curate": "You should clean up and rewrite unclear memory entries, keeping only actionable information.",
            "pursue_goal": "You should continue advancing the current goal and specify the next deliverable.",
            "rest": "You should take a short rest and resume afterward.",
        }
        return prompts.get(kind, "Choose a suitable autonomous task.")

    def _render_available_tools_for_prompt(self) -> str:
        if not self.available_tools:
            return "- (none)"
        lines: list[str] = []
        for tool in self.available_tools:
            name = str(tool.get("name", "")).strip()
            if not name:
                continue
            desc = str(tool.get("description", "")).strip() or "No description"
            lines.append(f"- {name}: {desc}")
        return "\n".join(lines) if lines else "- (none)"

    def _render_soul_for_prompt(self) -> str:
        if not self.soul_content:
            return "(soul.md is empty)"
        if len(self.soul_content) <= 1800:
            return self.soul_content
        return self.soul_content[:1800] + "\n... (truncated)"

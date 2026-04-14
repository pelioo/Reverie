from __future__ import annotations

from dataclasses import dataclass

from ..memory import MemoryManager, MemorySnippet


@dataclass(slots=True)
class ContextPacket:
    system_prompt: str
    retrieved_memories: list[MemorySnippet]
    messages: list[dict[str, str]]


class ContextManager:
    """Context manager.

    - keep fixed system prompt
    - retrieve top-k relevant memories
    - inject a memory digest block into prompt
    - simple char-budget trimming for memory block
    """

    def __init__(
        self,
        memory_manager: MemoryManager,
        top_k: int = 4,
        memory_char_budget: int = 1200,
        soul_content: str = "",
    ) -> None:
        self.memory_manager = memory_manager
        self.top_k = top_k
        self.memory_char_budget = memory_char_budget
        self.soul_content = soul_content.strip()

    def build_for_user_turn(self, user_input: str) -> ContextPacket:
        snippets = self.memory_manager.search(user_input, top_k=self.top_k)
        memory_block = self._build_memory_block(snippets)
        messages = [
            {
                "role": "system",
                "content": (
                    "You are Reverie. Respond concisely and with actionable steps."
                    "\nPrefer the provided historical memories; if memory is insufficient, say so explicitly."
                    "\nTreat soul.md as critical: it defines your long-term identity, principles, and growth direction."
                    "\nWhen you judge self-growth is needed, you may proactively use write_file to update workspace/memory/episodic/soul.md."
                    "\nMemory policy: only call memory_write when information has reusable long-term value; do not write memory for ordinary chat."
                    "\nIf you need tools, use tool_calls; do not output <tool_call> or JSON."
                    f"\n\nCurrent soul.md content:\n{self._build_soul_block()}"
                ),
            },
            {
                "role": "user",
                "content": f"User input:\n{user_input}\n\nRelevant memories:\n{memory_block}",
            },
        ]
        return ContextPacket(system_prompt=messages[0]["content"], retrieved_memories=snippets, messages=messages)

    def build_for_autonomous_turn(self, intent_prompt: str, intent_kind: str) -> ContextPacket:
        query = f"{intent_kind} {intent_prompt}"
        snippets = self.memory_manager.search(query, top_k=self.top_k)
        memory_block = self._build_memory_block(snippets)
        messages = [
            {
                "role": "system",
                "content": (
                    "You are Reverie in an autonomous turn. Your goal is to produce short, actionable observations or actions."
                    "\nPrefer validated experience from memory and avoid repeating low-value actions."
                    "\nTreat soul.md as critical: it constrains long-term behavior and guides growth."
                    "\nWhen you believe values, strategy, or long-term goals should evolve, you may proactively use write_file to update workspace/memory/episodic/soul.md."
                    "\nMemory policy: only call memory_write when this turn yields reusable long-term rules, conclusions, or high-value facts; exploration noise and temporary info should not be written."
                    "\nIf you need tools, use tool_calls; do not output <tool_call> or JSON."
                    f"\n\nCurrent soul.md content:\n{self._build_soul_block()}"
                ),
            },
            {
                "role": "user",
                "content": f"Intent: {intent_kind}\nTask: {intent_prompt}\n\nRelevant memories:\n{memory_block}",
            },
        ]
        return ContextPacket(system_prompt=messages[0]["content"], retrieved_memories=snippets, messages=messages)

    def _build_memory_block(self, snippets: list[MemorySnippet]) -> str:
        if not snippets:
            return "(no matching memories)"

        lines: list[str] = []
        used = 0
        for idx, s in enumerate(snippets, start=1):
            chunk = (
                f"[{idx}] id={s.memory_id} kind={s.kind} score={s.score:.2f}\n"
                f"title: {s.title}\n"
                f"excerpt: {s.excerpt}\n"
            )
            if used + len(chunk) > self.memory_char_budget:
                break
            lines.append(chunk)
            used += len(chunk)

        return "\n".join(lines) if lines else "(matching memories too long; truncated)"

    def _build_soul_block(self) -> str:
        if not self.soul_content:
            return "Your name is Reverie."
        return self.soul_content

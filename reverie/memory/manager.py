from __future__ import annotations

import json

from .scoring import make_excerpt, score_record, tokenize
from .store import MarkdownMemoryStore
from .types import MemoryRecord, MemorySnippet


class MemoryManager:
    def __init__(self, store: MarkdownMemoryStore) -> None:
        self.store = store

    def capture_event(self, event: dict) -> str:
        record = MemoryRecord(
            id=MemoryRecord.new_id(),
            kind="inbox",
            title=event.get("title", "Event"),
            content=self._event_to_markdown(event),
            tags=event.get("tags", []),
            source=event.get("source", "event"),
            importance=float(event.get("importance", 0.3)),
            related=event.get("related", []),
        )
        return self.store.save(record, folder_override="inbox")

    def write_memory(self, record: MemoryRecord) -> str:
        return self.store.save(record)

    def search(self, query: str, top_k: int = 4) -> list[MemorySnippet]:
        keywords = tokenize(query)
        scored: list[MemorySnippet] = []

        for path in self.store.list_memory_files():
            record = self.store.load(path)
            score = score_record(record, keywords)
            if score <= 0:
                continue
            excerpt = make_excerpt(record.content)
            scored.append(
                MemorySnippet(
                    memory_id=record.id,
                    kind=record.kind,
                    title=record.title,
                    excerpt=excerpt,
                    score=score,
                    path=str(path),
                )
            )

        scored.sort(key=lambda x: x.score, reverse=True)
        return scored[:top_k]

    @staticmethod
    def _event_to_markdown(event: dict) -> str:
        parts: list[str] = []
        if event.get("content"):
            parts.append(event["content"])
        if event.get("prompt"):
            parts.append("## Prompt\n" + event["prompt"])
        if event.get("reply"):
            parts.append("## Reply\n" + event["reply"])
        if not parts:
            parts.append("```json\n" + json.dumps(event, ensure_ascii=False, indent=2) + "\n```")
        return "\n\n".join(parts)

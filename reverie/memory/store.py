from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Iterable

from .types import MemoryRecord


class MarkdownMemoryStore:
    def __init__(self, memory_dir: str = "memory") -> None:
        self.memory_dir = Path(memory_dir)
        for folder in (
            "inbox",
            "working",
            "episodic",
            "semantic",
            "procedural",
            "reflective",
            "summaries",
            "index",
        ):
            (self.memory_dir / folder).mkdir(parents=True, exist_ok=True)

    def save(self, record: MemoryRecord, folder_override: str | None = None) -> str:
        folder = folder_override or record.kind
        target_dir = self.memory_dir / folder
        target_dir.mkdir(parents=True, exist_ok=True)
        path = target_dir / f"{record.id}.md"
        path.write_text(self._render_markdown(record), encoding="utf-8")
        return str(path)

    def list_memory_files(self) -> list[Path]:
        files = list(self.memory_dir.rglob("*.md"))
        return [p for p in files if "index" not in p.parts]

    def load(self, path: Path) -> MemoryRecord:
        text = path.read_text(encoding="utf-8")
        meta, body = self._split_frontmatter(text)

        created_at = _parse_time(meta.get("created_at"))
        updated_at = _parse_time(meta.get("updated_at"))
        tags = _parse_list(meta.get("tags", "[]"))
        related = _parse_list(meta.get("related", "[]"))

        title, content = _split_title_and_content(body)
        return MemoryRecord(
            id=meta.get("id", path.stem),
            kind=meta.get("kind", path.parent.name),
            title=title,
            content=content,
            tags=tags,
            created_at=created_at,
            updated_at=updated_at,
            source=meta.get("source", "unknown"),
            importance=float(meta.get("importance", 0.5)),
            related=related,
        )

    def _split_frontmatter(self, text: str) -> tuple[dict[str, str], str]:
        if not text.startswith("---\n"):
            return {}, text

        end_idx = text.find("\n---\n", 4)
        if end_idx == -1:
            return {}, text

        fm = text[4:end_idx].strip()
        body = text[end_idx + 5 :].lstrip()
        meta: dict[str, str] = {}
        for line in fm.splitlines():
            if ":" not in line:
                continue
            key, value = line.split(":", 1)
            meta[key.strip()] = value.strip()
        return meta, body

    def _render_markdown(self, record: MemoryRecord) -> str:
        frontmatter = "\n".join(
            [
                "---",
                f"id: {record.id}",
                f"kind: {record.kind}",
                f"tags: {self._render_list(record.tags)}",
                f"created_at: {record.created_at.isoformat(timespec='seconds')}",
                f"updated_at: {record.updated_at.isoformat(timespec='seconds')}",
                f"source: {record.source}",
                f"importance: {record.importance:.2f}",
                f"related: {self._render_list(record.related)}",
                "---",
                "",
            ]
        )
        body = f"# {record.title}\n\n{record.content.strip()}\n"
        return frontmatter + body

    @staticmethod
    def _render_list(values: Iterable[str]) -> str:
        values = list(values)
        if not values:
            return "[]"
        joined = ", ".join(values)
        return f"[{joined}]"


def parse_time(text: str | None) -> datetime:
    if not text:
        return datetime.now()
    try:
        return datetime.fromisoformat(text)
    except ValueError:
        return datetime.now()


def parse_list(text: str) -> list[str]:
    text = text.strip()
    if not (text.startswith("[") and text.endswith("]")):
        return []
    inner = text[1:-1].strip()
    if not inner:
        return []
    return [x.strip().strip('"').strip("'") for x in inner.split(",") if x.strip()]


def split_title_and_content(body: str) -> tuple[str, str]:
    lines = body.splitlines()
    if lines and lines[0].startswith("# "):
        return lines[0][2:].strip(), "\n".join(lines[1:]).strip()
    return "Memory", body.strip()


_parse_time = parse_time
_parse_list = parse_list
_split_title_and_content = split_title_and_content

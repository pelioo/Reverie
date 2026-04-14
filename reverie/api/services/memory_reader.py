from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


KINDS = ("episodic", "semantic", "reflective", "procedural", "working", "summaries", "inbox")
EXCLUDED_ROOTS = {"runtime", "__pycache__", ".git", "node_modules", ".vscode", "dist", "build", ".idea"}


def _parse_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    lines = text.splitlines()
    if len(lines) < 3 or lines[0].strip() != "---":
        return {}, text
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break
    if end is None:
        return {}, text
    meta: dict[str, Any] = {}
    for line in lines[1:end]:
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        meta[k.strip()] = v.strip()
    body = "\n".join(lines[end + 1 :]).strip()
    return meta, body


@dataclass(slots=True)
class MemoryReader:
    workspace_root: Path

    @property
    def memory_dir(self) -> Path:
        return self.workspace_root / "memory"

    def list_memory_files(self) -> list[Path]:
        files: list[Path] = []
        if not self.memory_dir.exists():
            return files
        for kind in KINDS:
            kdir = self.memory_dir / kind
            if not kdir.exists():
                continue
            files.extend([p for p in kdir.glob("*.md") if p.is_file()])
        return files

    def memory_count(self) -> int:
        return len(self.list_memory_files())

    def overview(self, limit: int = 100) -> tuple[dict[str, int], list[dict[str, Any]], list[dict[str, str]]]:
        counts = {k: 0 for k in KINDS}
        raw_nodes: list[dict[str, Any]] = []
        edges: list[dict[str, str]] = []

        for p in self.list_memory_files():
            kind = p.parent.name
            if kind in counts:
                counts[kind] += 1

            text = p.read_text(encoding="utf-8")
            meta, body = _parse_frontmatter(text)
            title = self._title_from_body_or_file(body, p)
            node_id = meta.get("id") or p.stem
            importance = self._to_float(meta.get("importance"), 0.4)
            created_at = meta.get("created_at") or self._mtime_iso(p)

            raw_nodes.append(
                {
                    "id": str(node_id),
                    "kind": kind,
                    "title": title,
                    "importance": importance,
                    "created_at": created_at,
                    "related": self._parse_related(meta.get("related")),
                    "path": str(p.relative_to(self.workspace_root)),
                }
            )

        raw_nodes.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        raw_nodes = raw_nodes[:limit]

        by_id = {n["id"]: n for n in raw_nodes}
        for n in raw_nodes:
            for r in n.get("related", []):
                if r in by_id:
                    edges.append({"from": n["id"], "to": r})

        nodes = self._layout_nodes(raw_nodes)
        return counts, nodes, edges

    def workspace_artifacts_overview(
        self, limit: int = 240
    ) -> tuple[dict[str, int], list[dict[str, Any]], list[dict[str, str]], list[dict[str, Any]]]:
        files: list[Path] = []
        root_counts: dict[str, int] = {}

        for root in sorted(self.workspace_root.iterdir()):
            if not root.exists():
                continue
            name = root.name
            if name.startswith(".") or name in EXCLUDED_ROOTS:
                continue
            if root.is_file():
                root_counts["_root"] = root_counts.get("_root", 0) + 1
                files.append(root)
                continue

            count = 0
            for p in root.rglob("*"):
                if not p.is_file():
                    continue
                rel_parts = p.relative_to(self.workspace_root).parts
                if any(part.startswith(".") for part in rel_parts):
                    continue
                if any(part in EXCLUDED_ROOTS for part in rel_parts):
                    continue
                count += 1
                files.append(p)
            root_counts[name] = count

        files = sorted(files, key=lambda p: p.stat().st_mtime, reverse=True)[:limit]
        nodes: list[dict[str, Any]] = []
        edges: list[dict[str, str]] = []
        groups: list[dict[str, Any]] = []

        items_by_cluster: dict[str, list[dict[str, Any]]] = {}
        for p in files:
            rel = str(p.relative_to(self.workspace_root))
            parts = p.relative_to(self.workspace_root).parts
            cluster = f"{parts[0]}/{parts[1]}" if len(parts) > 2 else (parts[0] if parts else "workspace")
            depth = len(parts) - 1
            node_type = self._node_type_by_path(p)
            label = "/".join(parts[-2:]) if len(parts) > 2 else rel
            if len(label) > 42:
                label = f"{label[:20]}…{label[-18:]}"

            item = {
                "id": rel,
                "type": node_type,
                "label": label,
                "cluster": cluster,
                "depth": depth,
                "x": 0,
                "y": 0,
            }
            items_by_cluster.setdefault(cluster, []).append(item)

        cluster_names = sorted(items_by_cluster.keys(), key=lambda c: (-len(items_by_cluster[c]), c))
        for idx, cluster in enumerate(cluster_names):
            col = idx % 2
            row = idx // 2
            base_x = 120 + col * 580
            base_y = 90 + row * 340
            group_items = items_by_cluster[cluster]
            group_items.sort(key=lambda x: (x["depth"], x["label"]))

            groups.append({"group": cluster, "count": len(group_items)})

            parent_by_depth: dict[int, str] = {}
            group_size = len(group_items)
            local_cols = 4 if group_size >= 10 else 3 if group_size >= 5 else 2
            for j, node in enumerate(group_items):
                local_col = j % local_cols
                local_row = j // local_cols
                node["x"] = base_x + local_col * 150 + node["depth"] * 14
                node["y"] = base_y + local_row * 92
                nodes.append(node)

                if node["depth"] in parent_by_depth:
                    edges.append({"from": parent_by_depth[node["depth"]], "to": node["id"]})
                elif node["depth"] > 0:
                    parent = parent_by_depth.get(node["depth"] - 1)
                    if parent:
                        edges.append({"from": parent, "to": node["id"]})

                parent_by_depth[node["depth"]] = node["id"]

        return root_counts, nodes, edges, groups

    def _layout_nodes(self, raw_nodes: list[dict[str, Any]]) -> list[dict[str, Any]]:
        nodes: list[dict[str, Any]] = []
        for i, n in enumerate(raw_nodes):
            col = i % 4
            row = i // 4
            x = 170 + col * 180
            y = 140 + row * 95
            kind = n.get("kind")
            mapped_kind = kind if kind in {"episodic", "semantic", "reflective", "procedural"} else "semantic"
            nodes.append(
                {
                    "type": mapped_kind,
                    "label": f"{kind}/{n.get('title','memory')}",
                    "x": x,
                    "y": y,
                    "id": n["id"],
                }
            )
        return nodes

    def _title_from_body_or_file(self, body: str, p: Path) -> str:
        for line in body.splitlines():
            s = line.strip()
            if s.startswith("#"):
                return s.lstrip("# ").strip()[:42]
        return p.stem[:42]

    def _parse_related(self, value: Any) -> list[str]:
        if value is None:
            return []
        text = str(value).strip()
        if text in {"", "[]"}:
            return []
        if text.startswith("[") and text.endswith("]"):
            inner = text[1:-1].strip()
            if not inner:
                return []
            return [part.strip().strip("'\"") for part in inner.split(",") if part.strip()]
        return [text]

    def _to_float(self, value: Any, default: float) -> float:
        try:
            return float(value)
        except Exception:
            return default

    def _mtime_iso(self, p: Path) -> str:
        return datetime.fromtimestamp(p.stat().st_mtime).isoformat(timespec="seconds")

    def _node_type_by_path(self, p: Path) -> str:
        suffix = p.suffix.lower()
        if suffix in {".md", ".txt", ".rst", ".json", ".yaml", ".yml"}:
            return "semantic"
        if suffix in {".py", ".ts", ".tsx", ".js", ".jsx", ".sh"}:
            return "procedural"
        if suffix in {".png", ".jpg", ".jpeg", ".svg", ".webp", ".gif"}:
            return "episodic"
        return "reflective"

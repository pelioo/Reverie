from __future__ import annotations

from typing import Literal

from pydantic import BaseModel


ActivityKind = Literal["intent", "tool", "result", "scheduler"]
MemoryKind = Literal["episodic", "semantic", "reflective", "procedural", "working", "summaries", "inbox"]


class HealthResponse(BaseModel):
    ok: bool
    runtime_dir: bool
    memory_dir: bool
    session_count: int
    memory_count: int
    generated_at: str


class SessionSummary(BaseModel):
    session_id: str
    mode: str
    active_goal: str | None
    last_updated_at: str | None


class HeroSummary(BaseModel):
    mind_state: str
    intensity: float
    color_hint: str


class StatItem(BaseModel):
    label: str
    value: str
    hint: str | None = None


class ActivityItem(BaseModel):
    time: str
    kind: ActivityKind
    text: str


class IntentToolResult(BaseModel):
    tool: str
    status: Literal["ok", "error"]
    summary: str
    raw_path: str


class IntentData(BaseModel):
    title: str
    source: str
    priority: str
    rationale: str
    guided_prompt: str
    model_thinking: str
    tool_results: list[IntentToolResult]
    memory_write_path: str | None = None


class DashboardOverviewResponse(BaseModel):
    session: SessionSummary
    hero: HeroSummary
    stats: list[StatItem]
    intent: IntentData
    activity: list[ActivityItem]
    generated_at: str


class MemoryNode(BaseModel):
    type: Literal["episodic", "semantic", "reflective", "procedural"]
    label: str
    x: int
    y: int
    id: str | None = None
    cluster: str | None = None
    depth: int | None = None


class MemoryEdge(BaseModel):
    from_: str
    to: str


class WorkspaceGroup(BaseModel):
    group: str
    count: int


class MemoryOverviewResponse(BaseModel):
    counts: dict[str, int]
    nodes: list[MemoryNode]
    edges: list[MemoryEdge]
    groups: list[WorkspaceGroup] = []
    generated_at: str


class SessionStateResponse(BaseModel):
    session_id: str
    current_mode: str
    current_task_tree: list[str]
    recent_tool_results: list[str]
    interrupt_flag: bool
    sleep_until: str | None
    current_active_goal: str | None
    last_user_input: str | None
    last_model_response: str | None
    last_memory_write: str | None
    total_turns: int
    user_turns: int
    autonomous_turns: int
    last_updated_at: str | None

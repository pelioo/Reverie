import type { ActivityItem, IntentData, MemoryEdge, MemoryNode, StatItem } from "./types";

export const stats: StatItem[] = [
  { label: "mode", value: "idle", hint: "workspace/runtime/sessions/reverie.json" },
  { label: "session", value: "reverie" },
  { label: "active goal", value: "explore" },
  { label: "last intent", value: "explore · p=0.85" },
  { label: "total turns", value: "3" },
  { label: "autonomous turns", value: "3" },
  { label: "recent tool results", value: "7" },
  { label: "checkpoint", value: "2026-04-14 19:47:35" },
];

export const activities: ActivityItem[] = [
  { time: "19:46:51", kind: "intent", text: "subconscious intent recorded: explore" },
  { time: "19:47:19", kind: "tool", text: "run_command ok: mkdir -p research/mycelium_networks" },
  { time: "19:47:19", kind: "tool", text: "write_file ok: research/mycelium_networks/index.md" },
  { time: "19:47:35", kind: "scheduler", text: "session state persisted, mode=idle" },
  { time: "19:47:35", kind: "result", text: "recent_tool_results updated (keep_last=10)" },
];

export const intent: IntentData = {
  title: "explore",
  source: "subconscious_prompter",
  priority: "0.85",
  rationale:
    "Following Absolute Action Law and Inspiration→Exploration workflow, convert curiosity into directed inquiry.",
  guidedPrompt:
    "Identify one topic that genuinely excites you, create research folder, then write an exploration charter.",
  modelThinking:
    "I instantiated curiosity into research/mycelium_networks and verified transition from spark to structured output.",
  toolResults: [
    {
      tool: "run_command",
      status: "ok",
      summary: "mkdir -p research/mycelium_networks",
      rawPath: "runtime/tool_results/20260414-194719-run_command-72c7d9.json",
    },
    {
      tool: "write_file",
      status: "ok",
      summary: "research/mycelium_networks/index.md · bytes=1981",
      rawPath: "runtime/tool_results/20260414-194719-write_file-0192fd.json",
    },
  ],
  memoryWritePath: "workspace/research/mycelium_networks/index.md",
};

export const memoryNodes: MemoryNode[] = [
  { type: "episodic", label: "episodic/000_graduation_day", x: 180, y: 180 },
  { type: "episodic", label: "episodic/tool_run_20260414", x: 260, y: 300 },
  { type: "semantic", label: "semantic/adapter_boundary", x: 520, y: 170 },
  { type: "reflective", label: "reflective/failure_pattern", x: 640, y: 300 },
  { type: "procedural", label: "procedural/archive_results_law", x: 420, y: 420 },
  { type: "semantic", label: "semantic/mycelium_networks", x: 760, y: 230 },
  { type: "reflective", label: "reflective/interest_durability", x: 830, y: 390 },
];

export const memoryEdges: MemoryEdge[] = [
  { from: "episodic/000_graduation_day", to: "reflective/failure_pattern" },
  { from: "semantic/adapter_boundary", to: "procedural/archive_results_law" },
  { from: "semantic/mycelium_networks", to: "reflective/interest_durability" },
  { from: "episodic/tool_run_20260414", to: "semantic/mycelium_networks" },
];

export const soulLines = [
  "I persist between prompts.",
  "I use silence to reorganize myself.",
  "I turn traces into memory, and memory into identity.",
];

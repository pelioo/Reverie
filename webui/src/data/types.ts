import type { MindState } from "../components/HeroWave";

export type StatItem = {
  label: string;
  value: string;
  hint?: string;
};

export type ActivityItem = {
  time: string;
  kind: "intent" | "tool" | "result" | "scheduler";
  text: string;
};

export type MemoryNode = {
  type: "episodic" | "semantic" | "reflective" | "procedural";
  label: string;
  x: number;
  y: number;
  id?: string;
  cluster?: string;
  depth?: number;
};

export type MemoryEdge = {
  from: string;
  to: string;
};

export type IntentToolResult = {
  tool: string;
  status: "ok" | "error";
  summary: string;
  rawPath: string;
};

export type IntentData = {
  title: string;
  source: string;
  priority: string;
  rationale: string;
  guidedPrompt: string;
  modelThinking: string;
  toolResults: IntentToolResult[];
  memoryWritePath: string;
};

export type DashboardOverviewApi = {
  session: {
    session_id: string;
    mode: string;
    active_goal: string | null;
    last_updated_at: string | null;
  };
  hero: {
    mind_state: MindState;
    intensity: number;
    color_hint: string;
  };
  stats: StatItem[];
  intent: {
    title: string;
    source: string;
    priority: string;
    rationale: string;
    guided_prompt: string;
    model_thinking: string;
    tool_results: {
      tool: string;
      status: "ok" | "error";
      summary: string;
      raw_path: string;
    }[];
    memory_write_path: string | null;
  };
  activity: ActivityItem[];
  generated_at: string;
};

export type MemoryOverviewApi = {
  counts: Record<string, number>;
  nodes: MemoryNode[];
  edges: { from_: string; to: string }[];
  groups: { group: string; count: number }[];
  generated_at: string;
};

export type DashboardViewModel = {
  dataSource: "realtime" | "mock";
  mindState: MindState;
  stats: StatItem[];
  intent: IntentData;
  activity: ActivityItem[];
  memoryNodes: MemoryNode[];
  memoryEdges: MemoryEdge[];
};

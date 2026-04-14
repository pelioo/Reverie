import { activities as mockActivities, intent as mockIntent, memoryEdges as mockEdges, memoryNodes as mockNodes, stats as mockStats } from "./mock";
import type { DashboardOverviewApi, DashboardViewModel, MemoryOverviewApi } from "./types";

type DashboardMainSlice = Pick<DashboardViewModel, "dataSource" | "mindState" | "stats" | "intent" | "activity">;
type DashboardMemorySlice = Pick<DashboardViewModel, "memoryNodes" | "memoryEdges">;

function toEpoch(value: string): number {
  const t = Date.parse(value);
  return Number.isNaN(t) ? 0 : t;
}

function toMainSlice(overview: DashboardOverviewApi): DashboardMainSlice {
  const activity = [...overview.activity].sort((a, b) => toEpoch(b.time) - toEpoch(a.time));
  const toolResults = [...overview.intent.tool_results]
    .sort((a, b) => b.raw_path.localeCompare(a.raw_path))
    .map((t) => ({
      tool: t.tool,
      status: t.status,
      summary: t.summary,
      rawPath: t.raw_path,
    }));

  return {
    dataSource: "realtime",
    mindState: overview.hero.mind_state,
    stats: overview.stats,
    intent: {
      title: overview.intent.title,
      source: overview.intent.source,
      priority: overview.intent.priority,
      rationale: overview.intent.rationale,
      guidedPrompt: overview.intent.guided_prompt,
      modelThinking: overview.intent.model_thinking,
      toolResults,
      memoryWritePath: overview.intent.memory_write_path ?? "",
    },
    activity,
  };
}

function toMemorySlice(memory: MemoryOverviewApi): DashboardMemorySlice {
  return {
    memoryNodes: memory.nodes.map((n) => ({
      type: n.type,
      label: n.label,
      x: n.x,
      y: n.y,
      id: n.id,
      cluster: n.cluster,
      depth: n.depth,
    })),
    memoryEdges: memory.edges.map((e) => ({ from: e.from_, to: e.to })),
  };
}

export async function fetchDashboardMainSlice(): Promise<DashboardMainSlice | null> {
  try {
    const overviewRes = await fetch("/dashboard/overview");
    if (!overviewRes.ok) {
      return null;
    }
    const overview = (await overviewRes.json()) as DashboardOverviewApi;
    return toMainSlice(overview);
  } catch {
    return null;
  }
}

export async function fetchDashboardMemorySlice(): Promise<DashboardMemorySlice | null> {
  try {
    const memoryRes = await fetch("/memory/overview");
    if (!memoryRes.ok) {
      return null;
    }
    const memory = (await memoryRes.json()) as MemoryOverviewApi;
    return toMemorySlice(memory);
  } catch {
    return null;
  }
}

export async function fetchDashboardViewModel(): Promise<DashboardViewModel> {
  const [main, memory] = await Promise.all([fetchDashboardMainSlice(), fetchDashboardMemorySlice()]);

  if (main && memory) {
    return {
      ...main,
      ...memory,
    };
  }

  if (main) {
    return {
      ...main,
      memoryNodes: mockNodes,
      memoryEdges: mockEdges,
    };
  }

  return {
    dataSource: "mock",
    mindState: "reflecting",
    stats: mockStats,
    intent: mockIntent,
    activity: mockActivities,
    memoryNodes: memory?.memoryNodes ?? mockNodes,
    memoryEdges: memory?.memoryEdges ?? mockEdges,
  };
}

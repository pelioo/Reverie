import { useEffect, useState } from "react";
import { ActivityList } from "./components/ActivityList";
import { HeroWave } from "./components/HeroWave";
import { IntentCard } from "./components/IntentCard";
import { MemoryConstellation } from "./components/MemoryConstellation";
import { SoulPanel } from "./components/SoulPanel";
import { StatsGrid } from "./components/StatsGrid";
import { fetchDashboardMainSlice, fetchDashboardMemorySlice, fetchDashboardViewModel } from "./data/api";
import { activities, intent, memoryEdges, memoryNodes, soulLines, stats } from "./data/mock";
import type { DashboardViewModel } from "./data/types";

export default function App() {
  const [dashboard, setDashboard] = useState<DashboardViewModel>(() => ({
    dataSource: "mock",
    mindState: "reflecting",
    stats,
    intent,
    activity: activities,
    memoryNodes,
    memoryEdges,
  }));

  useEffect(() => {
    let disposed = false;

    async function refreshAll() {
      const next = await fetchDashboardViewModel();
      if (!disposed) {
        setDashboard(next);
      }
    }

    async function refreshMain() {
      const next = await fetchDashboardMainSlice();
      if (!disposed && next) {
        setDashboard((prev) => ({ ...prev, ...next }));
      }
    }

    async function refreshMemory() {
      const next = await fetchDashboardMemorySlice();
      if (!disposed && next) {
        setDashboard((prev) => ({ ...prev, ...next }));
      }
    }

    void refreshAll();
    const mainTimer = window.setInterval(() => {
      void refreshMain();
    }, 1500);
    const memoryTimer = window.setInterval(() => {
      void refreshMemory();
    }, 30000);

    return () => {
      disposed = true;
      window.clearInterval(mainTimer);
      window.clearInterval(memoryTimer);
    };
  }, []);

  return (
    <div className="app-shell">
      <div className="bg-grid" />
      <header className="topbar">
        <span className="brand">REVERIE / WEB DASHBOARD</span>
        <nav className="links">
          <a href="https://github.com/XIAODUOLU/Reverie" target="_blank" rel="noreferrer">
            GitHub
          </a>
        </nav>
      </header>

      <main className="dashboard-grid">
        <div className="cell hero-cell">
          <HeroWave mindState={dashboard.mindState} />
        </div>
        <div className="cell stats-cell">
          <StatsGrid items={dashboard.stats} />
        </div>
        <div className="cell intent-cell">
          <IntentCard data={dashboard.intent} />
        </div>
        <div className="cell activity-cell">
          <ActivityList items={dashboard.activity} dataSource={dashboard.dataSource} />
        </div>
        <div className="cell memory-cell">
          <MemoryConstellation nodes={dashboard.memoryNodes} edges={dashboard.memoryEdges} />
        </div>
        <div className="cell soul-cell">
          <SoulPanel lines={soulLines} />
        </div>
      </main>
    </div>
  );
}

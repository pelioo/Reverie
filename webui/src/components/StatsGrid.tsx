import type { StatItem } from "../data/types";

type Props = {
  items: StatItem[];
};

export function StatsGrid({ items }: Props) {
  return (
    <section className="panel">
      <div className="panel-title-row compact">
        <h2>Live Stats</h2>
      </div>
      <div className="stats-grid">
        {items.map((item) => (
          <article className="stat" key={item.label}>
            <p className="stat-label">{item.label}</p>
            <p className="stat-value">{item.value}</p>
            {item.hint ? <p className="stat-hint">{item.hint}</p> : null}
          </article>
        ))}
      </div>
    </section>
  );
}

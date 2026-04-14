import type { ActivityItem } from "../data/types";

type Props = {
  items: ActivityItem[];
  dataSource: "realtime" | "mock";
};

function toSortableTime(value: string): number {
  const direct = Date.parse(value);
  if (!Number.isNaN(direct)) return direct;
  const hms = Date.parse(`1970-01-01T${value}`);
  return Number.isNaN(hms) ? 0 : hms;
}

function formatTime(value: string): { day: string; hm: string } {
  const direct = new Date(value);
  if (!Number.isNaN(direct.getTime())) {
    const mm = `${direct.getMonth() + 1}`.padStart(2, "0");
    const dd = `${direct.getDate()}`.padStart(2, "0");
    const hh = `${direct.getHours()}`.padStart(2, "0");
    const mi = `${direct.getMinutes()}`.padStart(2, "0");
    return { day: `${mm}-${dd}`, hm: `${hh}:${mi}` };
  }

  const m = value.match(/^(\d{4}-\d{2}-\d{2})[T\s](\d{2}:\d{2})/);
  if (m) {
    return { day: m[1].slice(5), hm: m[2] };
  }

  const m2 = value.match(/^(\d{2}:\d{2})/);
  if (m2) {
    return { day: "--", hm: m2[1] };
  }

  return { day: "--", hm: "--:--" };
}

export function ActivityList({ items, dataSource }: Props) {
  const sortedItems = [...items].sort((a, b) => toSortableTime(b.time) - toSortableTime(a.time));

  return (
    <section className="panel activity-panel">
      <div className="panel-title-row compact">
        <h2>Live Activity</h2>
        <span className="mono">{dataSource === "realtime" ? "REALTIME" : "MOCK"}</span>
      </div>
      <ul className="activity-list">
        {sortedItems.map((item) => (
          <li className="activity-item" key={`${item.time}-${item.text}`}>
            <span className="activity-time" title={item.time}>
              <span className="activity-time-day">{formatTime(item.time).day}</span>
              <span className="activity-time-hm">{formatTime(item.time).hm}</span>
            </span>
            <span className="activity-text-wrap">
              <span className={`activity-kind kind-${item.kind}`}>{item.kind}</span>
              <span className="activity-text">{item.text}</span>
            </span>
          </li>
        ))}
      </ul>
    </section>
  );
}

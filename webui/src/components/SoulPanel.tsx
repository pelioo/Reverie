type Props = {
  lines: string[];
};

export function SoulPanel({ lines }: Props) {
  return (
    <section className="panel">
      <div className="panel-title-row compact">
        <h2>Soul Signals</h2>
      </div>
      <div className="soul-lines">
        {lines.map((line) => (
          <p className="soul-line" key={line}>
            {line}
          </p>
        ))}
      </div>
      <p className="soul-note">Memory is not cached text. It is accumulated identity.</p>
    </section>
  );
}


import type { IntentData } from "../data/types";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

type Props = {
  data: IntentData;
};

export function IntentCard({ data }: Props) {
  return (
    <section className="panel">
      <div className="panel-title-row compact">
        <h2>Current Intent</h2>
      </div>
      <article className="intent-card">
        <h3>{data.title}</h3>
        <p className="intent-meta">
          source: {data.source} · priority: {data.priority}
        </p>
        <p className="intent-body">
          <strong>Guidance</strong>
        </p>
        <div className="intent-markdown">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>{data.guidedPrompt || "-"}</ReactMarkdown>
        </div>

        <p className="intent-body">
          <strong>Model Thinking</strong>
        </p>
        <div className="intent-markdown">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>{data.modelThinking || "-"}</ReactMarkdown>
        </div>

        <div className="intent-tool-results">
          <p className="intent-tools-title">Recent Tool Calls</p>
          {data.toolResults.map((result) => (
            <div className="intent-tool-result" key={result.rawPath}>
              <span className={`tool-badge ${result.status}`}>{result.tool}</span>
              <span className="tool-summary">{result.summary}</span>
            </div>
          ))}
        </div>

        <p className="intent-memory-path">memory write → {data.memoryWritePath}</p>
      </article>
    </section>
  );
}

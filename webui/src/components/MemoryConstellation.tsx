import { useMemo, useState, type MouseEvent, type WheelEvent } from "react";
import type { MemoryEdge, MemoryNode } from "../data/types";

type Props = {
  nodes: MemoryNode[];
  edges: MemoryEdge[];
};

const VIEWPORT_W = 760;
const VIEWPORT_H = 440;
const CANVAS_PADDING = 140;

export function MemoryConstellation({ nodes, edges }: Props) {
  const [zoom, setZoom] = useState(0.62);
  const [offsetX, setOffsetX] = useState(0);
  const [offsetY, setOffsetY] = useState(0);
  const [dragging, setDragging] = useState(false);
  const [dragStart, setDragStart] = useState<{ x: number; y: number } | null>(null);
  const [nodeOffsets, setNodeOffsets] = useState<Record<string, { x: number; y: number }>>({});
  const [draggingNodeId, setDraggingNodeId] = useState<string | null>(null);
  const [nodeDragStart, setNodeDragStart] = useState<{
    id: string;
    clientX: number;
    clientY: number;
    originX: number;
    originY: number;
  } | null>(null);

  const renderedNodes = useMemo(() => {
    const used = new Set<string>();
    return nodes.map((node) => {
      let x = node.x;
      let y = node.y;
      let step = 0;
      while (step < 18) {
        const key = `${Math.round(x / 22)}:${Math.round(y / 18)}`;
        if (!used.has(key)) {
          used.add(key);
          break;
        }
        const dx = ((step % 3) - 1) * 18;
        const dy = 14 + Math.floor(step / 3) * 6;
        x += dx;
        y += dy;
        step += 1;
      }

      const nodeId = node.id ?? node.label;
      const offset = nodeOffsets[nodeId] ?? { x: 0, y: 0 };
      return { ...node, x: x + offset.x, y: y + offset.y };
    });
  }, [nodes, nodeOffsets]);

  const layout = useMemo(() => {
    if (!renderedNodes.length) {
      return {
        width: VIEWPORT_W,
        height: VIEWPORT_H,
        nodes: renderedNodes,
      };
    }

    const xs = renderedNodes.map((n) => n.x);
    const ys = renderedNodes.map((n) => n.y);
    const minX = Math.min(...xs);
    const maxX = Math.max(...xs);
    const minY = Math.min(...ys);
    const maxY = Math.max(...ys);

    const shiftX = CANVAS_PADDING - minX;
    const shiftY = CANVAS_PADDING - minY;

    const positionedNodes = renderedNodes.map((n) => ({
      ...n,
      renderX: n.x + shiftX,
      renderY: n.y + shiftY,
    }));

    const width = Math.max(VIEWPORT_W, Math.ceil(maxX - minX + CANVAS_PADDING * 2));
    const height = Math.max(VIEWPORT_H, Math.ceil(maxY - minY + CANVAS_PADDING * 2));

    return {
      width,
      height,
      nodes: positionedNodes,
    };
  }, [renderedNodes]);

  const nodeMap = useMemo(
    () => new Map(layout.nodes.map((n) => [n.id ?? n.label, n])),
    [layout.nodes],
  );
  const clusterList = useMemo(() => {
    const m = new Map<string, number>();
    for (const n of renderedNodes) {
      const key = n.cluster ?? "workspace";
      m.set(key, (m.get(key) ?? 0) + 1);
    }
    return [...m.entries()].sort((a, b) => b[1] - a[1]);
  }, [renderedNodes]);

  function onWheel(e: WheelEvent<HTMLDivElement>) {
    e.preventDefault();
    setZoom((z) => Math.min(1.5, Math.max(0.45, z - e.deltaY * 0.0008)));
  }

  function onMouseDown(e: MouseEvent<HTMLDivElement>) {
    setDragging(true);
    setDragStart({ x: e.clientX - offsetX, y: e.clientY - offsetY });
  }

  function onMouseMove(e: MouseEvent<HTMLDivElement>) {
    if (nodeDragStart) {
      const dx = (e.clientX - nodeDragStart.clientX) / zoom;
      const dy = (e.clientY - nodeDragStart.clientY) / zoom;
      setNodeOffsets((prev) => ({
        ...prev,
        [nodeDragStart.id]: {
          x: nodeDragStart.originX + dx,
          y: nodeDragStart.originY + dy,
        },
      }));
      return;
    }

    if (!dragging || !dragStart) return;
    setOffsetX(e.clientX - dragStart.x);
    setOffsetY(e.clientY - dragStart.y);
  }

  function onMouseUp() {
    setDragging(false);
    setDragStart(null);
    setDraggingNodeId(null);
    setNodeDragStart(null);
  }

  function onNodeMouseDown(e: MouseEvent<HTMLDivElement>, node: MemoryNode) {
    e.stopPropagation();
    e.preventDefault();
    const id = node.id ?? node.label;
    const current = nodeOffsets[id] ?? { x: 0, y: 0 };
    setDraggingNodeId(id);
    setNodeDragStart({
      id,
      clientX: e.clientX,
      clientY: e.clientY,
      originX: current.x,
      originY: current.y,
    });
  }

  function resetView() {
    setZoom(0.62);
    setOffsetX(0);
    setOffsetY(0);
  }

  return (
    <section className="panel">
      <div className="panel-title-row compact">
        <h2>Memory / Artifacts Map</h2>
        <div className="memory-controls">
          <button type="button" onClick={() => setZoom((z) => Math.min(1.5, z + 0.08))}>
            +
          </button>
          <button type="button" onClick={() => setZoom((z) => Math.max(0.45, z - 0.08))}>
            -
          </button>
          <button type="button" onClick={resetView}>
            reset
          </button>
        </div>
      </div>
      <p className="memory-tip">workspace (exclude runtime) · drag node/card to move · drag blank area to pan · wheel to zoom</p>
      <div className="memory-groups">
        {clusterList.slice(0, 8).map(([name, count]) => (
          <span key={name} className="memory-group-chip">
            {name} · {count}
          </span>
        ))}
      </div>

      <div
        className={`constellation ${dragging ? "dragging" : ""}`}
        onWheel={onWheel}
        onMouseDown={onMouseDown}
        onMouseMove={onMouseMove}
        onMouseUp={onMouseUp}
        onMouseLeave={onMouseUp}
      >
        <div
          className="constellation-canvas"
          style={{
            width: layout.width,
            height: layout.height,
            transform: `translate(${offsetX}px, ${offsetY}px) scale(${zoom})`,
            transformOrigin: "0 0",
          }}
        >
          <svg className="memory-edges" width={layout.width} height={layout.height} aria-hidden>
            {edges.map((edge) => {
              const from = nodeMap.get(edge.from);
              const to = nodeMap.get(edge.to);
              if (!from || !to) return null;
              return (
                <line
                  key={`${edge.from}-${edge.to}`}
                  x1={(from as MemoryNode & { renderX?: number }).renderX ?? from.x}
                  y1={(from as MemoryNode & { renderY?: number }).renderY ?? from.y}
                  x2={(to as MemoryNode & { renderX?: number }).renderX ?? to.x}
                  y2={(to as MemoryNode & { renderY?: number }).renderY ?? to.y}
                  className="memory-edge-line"
                />
              );
            })}
          </svg>

          {layout.nodes.map((node) => (
            <div
              key={node.id ?? node.label}
              className={`node node-${node.type} ${draggingNodeId === (node.id ?? node.label) ? "dragging" : ""}`}
              style={{
                left: `${(node as MemoryNode & { renderX?: number }).renderX ?? node.x}px`,
                top: `${(node as MemoryNode & { renderY?: number }).renderY ?? node.y}px`,
              }}
              title={`${node.cluster ?? "-"} / depth=${node.depth ?? 0}`}
              onMouseDown={(e) => onNodeMouseDown(e, node)}
            >
              {node.label}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

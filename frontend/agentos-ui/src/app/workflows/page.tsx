/**
 * File: workflows/page.tsx
 *
 * Visual Workflow Builder — lists workflows and provides a canvas editor
 * for designing, saving, and deploying multi-agent pipelines.
 * Uses a lightweight SVG-based node graph (no external lib required).
 */
"use client";

import { useEffect, useRef, useState } from "react";

// ── Types ────────────────────────────────────────────────────────────────────

type NodeType = "InputNode" | "AgentNode" | "CrewNode" | "ToolNode" | "ConditionNode" | "OutputNode";

type GraphNode = {
  id: string;
  type: NodeType;
  x: number;
  y: number;
  data: { label: string; agentId?: string; model?: string };
};

type GraphEdge = { id: string; source: string; target: string };

type Workflow = {
  id: string;
  name: string;
  description?: string;
  status: "draft" | "deployed";
  version: number;
  graph: { nodes: GraphNode[]; edges: GraphEdge[] };
};

const NODE_COLORS: Record<NodeType, string> = {
  InputNode: "#4ade80",
  AgentNode: "#60a5fa",
  CrewNode: "#a78bfa",
  ToolNode: "#fb923c",
  ConditionNode: "#fbbf24",
  OutputNode: "#f87171",
};

const NODE_W = 140;
const NODE_H = 50;

// ── Component ────────────────────────────────────────────────────────────────

export default function WorkflowsPage() {
  const [workflows, setWorkflows] = useState<Workflow[]>([]);
  const [selected, setSelected] = useState<Workflow | null>(null);
  const [nodes, setNodes] = useState<GraphNode[]>([]);
  const [edges, setEdges] = useState<GraphEdge[]>([]);
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);
  const [dragging, setDragging] = useState<{ id: string; ox: number; oy: number } | null>(null);
  const [edgeFrom, setEdgeFrom] = useState<string | null>(null);
  const [testInput, setTestInput] = useState("");
  const [testOutput, setTestOutput] = useState<string[]>([]);
  const [running, setRunning] = useState(false);
  const [saving, setSaving] = useState(false);
  const [newName, setNewName] = useState("");
  const [creating, setCreating] = useState(false);
  const svgRef = useRef<SVGSVGElement>(null);
  const token = typeof window !== "undefined" ? localStorage.getItem("agentos_token") : null;

  useEffect(() => { loadWorkflows(); }, []); // eslint-disable-line react-hooks/exhaustive-deps

  async function loadWorkflows() {
    try {
      const res = await fetch("/api/v1/workflows", {
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      });
      if (res.ok) { const j = await res.json(); setWorkflows(j.data || []); }
    } catch {}
  }

  function openWorkflow(wf: Workflow) {
    setSelected(wf);
    setNodes(wf.graph?.nodes || []);
    setEdges(wf.graph?.edges || []);
    setSelectedNode(null);
    setTestOutput([]);
  }

  async function createWorkflow() {
    if (!newName.trim()) return;
    setCreating(true);
    try {
      const res = await fetch("/api/v1/workflows", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({
          name: newName.trim(),
          graph: { nodes: [], edges: [] },
        }),
      });
      if (res.ok) {
        const j = await res.json();
        setWorkflows((prev) => [j.data, ...prev]);
        openWorkflow(j.data);
        setNewName("");
      }
    } finally { setCreating(false); }
  }

  async function saveWorkflow() {
    if (!selected) return;
    setSaving(true);
    try {
      await fetch(`/api/v1/workflows/${selected.id}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({ graph: { nodes, edges } }),
      });
      await loadWorkflows();
    } finally { setSaving(false); }
  }

  async function deployWorkflow() {
    if (!selected) return;
    await fetch(`/api/v1/workflows/${selected.id}/deploy`, {
      method: "POST",
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    });
    await loadWorkflows();
  }

  async function runWorkflow() {
    if (!selected || !testInput.trim()) return;
    setRunning(true);
    setTestOutput([]);
    await saveWorkflow();
    try {
      const res = await fetch(`/api/v1/workflows/${selected.id}/run`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({ input: testInput }),
      });
      const reader = res.body?.getReader();
      const decoder = new TextDecoder();
      if (!reader) return;
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        const chunk = decoder.decode(value);
        for (const line of chunk.split("\n")) {
          if (line.startsWith("data:") && line.length > 5) {
            try {
              const event = JSON.parse(line.slice(5).trim());
              if (event.message) setTestOutput((p) => [...p, event.message]);
            } catch {}
          }
        }
      }
    } finally { setRunning(false); }
  }

  function addNode(type: NodeType) {
    const id = `${type}-${Date.now()}`;
    const label = type.replace("Node", "");
    setNodes((prev) => [
      ...prev,
      { id, type, x: 80 + prev.length * 30, y: 80 + prev.length * 20, data: { label } },
    ]);
  }

  function deleteNode(nodeId: string) {
    setNodes((prev) => prev.filter((n) => n.id !== nodeId));
    setEdges((prev) => prev.filter((e) => e.source !== nodeId && e.target !== nodeId));
    if (selectedNode?.id === nodeId) setSelectedNode(null);
  }

  function startEdge(nodeId: string) {
    if (edgeFrom === null) { setEdgeFrom(nodeId); return; }
    if (edgeFrom !== nodeId) {
      const id = `e-${edgeFrom}-${nodeId}`;
      setEdges((prev) => [...prev, { id, source: edgeFrom, target: nodeId }]);
    }
    setEdgeFrom(null);
  }

  function onSvgMouseMove(e: React.MouseEvent<SVGSVGElement>) {
    if (!dragging) return;
    const rect = svgRef.current!.getBoundingClientRect();
    const x = e.clientX - rect.left - dragging.ox;
    const y = e.clientY - rect.top - dragging.oy;
    setNodes((prev) => prev.map((n) => (n.id === dragging.id ? { ...n, x, y } : n)));
  }

  function getNodePos(id: string) {
    const n = nodes.find((n) => n.id === id);
    if (!n) return { x: 0, y: 0 };
    return { x: n.x + NODE_W / 2, y: n.y + NODE_H / 2 };
  }

  // ── Render ────────────────────────────────────────────────────────────────

  return (
    <div className="flex h-[calc(100vh-57px)] overflow-hidden">
      {/* WORKFLOW LIST SIDEBAR */}
      <aside className="flex w-64 flex-col border-r border-zinc-200 bg-white dark:border-zinc-800 dark:bg-zinc-900">
        <div className="border-b border-zinc-200 dark:border-zinc-800 p-4">
          <p className="mb-3 text-sm font-semibold text-zinc-700 dark:text-zinc-300">Workflows</p>
          <div className="flex gap-2">
            <input
              value={newName}
              onChange={(e) => setNewName(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && createWorkflow()}
              placeholder="New workflow name…"
              className="flex-1 rounded-lg border border-zinc-300 px-2 py-1.5 text-xs dark:border-zinc-700 dark:bg-zinc-800 dark:text-zinc-100"
            />
            <button
              onClick={createWorkflow}
              disabled={creating || !newName.trim()}
              className="rounded-lg bg-zinc-900 px-2 py-1.5 text-xs text-white disabled:opacity-50 dark:bg-zinc-100 dark:text-zinc-900"
            >
              +
            </button>
          </div>
        </div>
        <div className="flex-1 overflow-y-auto p-2 space-y-1">
          {workflows.map((wf) => (
            <button
              key={wf.id}
              onClick={() => openWorkflow(wf)}
              className={`w-full rounded-lg px-3 py-2 text-left text-sm transition ${
                selected?.id === wf.id
                  ? "bg-zinc-100 dark:bg-zinc-800"
                  : "text-zinc-600 hover:bg-zinc-50 dark:text-zinc-400 dark:hover:bg-zinc-800"
              }`}
            >
              <div className="flex items-center justify-between">
                <span className="truncate font-medium">{wf.name}</span>
                <span className={`ml-2 rounded-full px-1.5 py-0.5 text-xs ${
                  wf.status === "deployed"
                    ? "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400"
                    : "bg-zinc-100 text-zinc-500 dark:bg-zinc-700"
                }`}>
                  {wf.status}
                </span>
              </div>
              <p className="text-xs text-zinc-400 mt-0.5">v{wf.version}</p>
            </button>
          ))}
          {workflows.length === 0 && (
            <p className="px-2 py-4 text-xs text-zinc-400 text-center">No workflows yet</p>
          )}
        </div>
      </aside>

      {/* CANVAS */}
      {selected ? (
        <div className="flex flex-1 flex-col overflow-hidden">
          {/* Toolbar */}
          <div className="flex items-center gap-2 border-b border-zinc-200 bg-white px-4 py-2 dark:border-zinc-800 dark:bg-zinc-900">
            <span className="text-sm font-semibold text-zinc-700 dark:text-zinc-300 mr-2">{selected.name}</span>
            {(["InputNode","AgentNode","CrewNode","ToolNode","ConditionNode","OutputNode"] as NodeType[]).map((t) => (
              <button
                key={t}
                onClick={() => addNode(t)}
                style={{ borderColor: NODE_COLORS[t] }}
                className="rounded-lg border px-2 py-1 text-xs text-zinc-600 hover:bg-zinc-50 dark:text-zinc-300 dark:hover:bg-zinc-800"
              >
                + {t.replace("Node","")}
              </button>
            ))}
            <div className="ml-auto flex gap-2">
              {edgeFrom && (
                <span className="rounded-lg bg-yellow-100 px-2 py-1 text-xs text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-300">
                  Click target node to connect from &quot;{edgeFrom}&quot;
                </span>
              )}
              <button
                onClick={saveWorkflow}
                disabled={saving}
                className="rounded-lg border border-zinc-300 px-3 py-1 text-xs text-zinc-600 hover:bg-zinc-50 dark:border-zinc-700 dark:text-zinc-300"
              >
                {saving ? "Saving…" : "Save"}
              </button>
              <button
                onClick={deployWorkflow}
                className="rounded-lg bg-green-600 px-3 py-1 text-xs text-white hover:bg-green-700"
              >
                Deploy
              </button>
            </div>
          </div>

          {/* Split: canvas + right panel */}
          <div className="flex flex-1 overflow-hidden">
            {/* SVG Canvas */}
            <svg
              ref={svgRef}
              className="flex-1 bg-zinc-50 dark:bg-zinc-950 cursor-default"
              onMouseMove={onSvgMouseMove}
              onMouseUp={() => setDragging(null)}
            >
              {/* Grid dots */}
              <defs>
                <pattern id="grid" width="24" height="24" patternUnits="userSpaceOnUse">
                  <circle cx="1" cy="1" r="0.5" fill="#d4d4d8" />
                </pattern>
              </defs>
              <rect width="100%" height="100%" fill="url(#grid)" />

              {/* Edges */}
              {edges.map((edge) => {
                const s = getNodePos(edge.source);
                const t = getNodePos(edge.target);
                return (
                  <g key={edge.id}>
                    <line
                      x1={s.x} y1={s.y} x2={t.x} y2={t.y}
                      stroke="#94a3b8" strokeWidth={2}
                      markerEnd="url(#arrow)"
                    />
                  </g>
                );
              })}
              <defs>
                <marker id="arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto">
                  <path d="M0,0 L0,6 L8,3 z" fill="#94a3b8" />
                </marker>
              </defs>

              {/* Nodes */}
              {nodes.map((node) => (
                <g
                  key={node.id}
                  transform={`translate(${node.x},${node.y})`}
                  onMouseDown={(e) => {
                    e.stopPropagation();
                    const rect = svgRef.current!.getBoundingClientRect();
                    setDragging({ id: node.id, ox: e.clientX - rect.left - node.x, oy: e.clientY - rect.top - node.y });
                    setSelectedNode(node);
                  }}
                  onClick={(e) => { e.stopPropagation(); setSelectedNode(node); }}
                  className="cursor-grab"
                >
                  <rect
                    width={NODE_W} height={NODE_H} rx={8}
                    fill={NODE_COLORS[node.type]}
                    opacity={0.15}
                    stroke={NODE_COLORS[node.type]}
                    strokeWidth={selectedNode?.id === node.id ? 2.5 : 1.5}
                  />
                  <text x={NODE_W / 2} y={NODE_H / 2 - 5} textAnchor="middle"
                    fontSize={11} fontWeight={600}
                    fill={typeof window !== "undefined" && document.documentElement.classList.contains("dark") ? "#f4f4f5" : "#1e293b"}
                  >
                    {node.data.label}
                  </text>
                  <text x={NODE_W / 2} y={NODE_H / 2 + 10} textAnchor="middle"
                    fontSize={9} fill="#6b7280"
                  >
                    {node.type}
                  </text>
                  {/* Connect port */}
                  <circle
                    cx={NODE_W} cy={NODE_H / 2} r={5}
                    fill={edgeFrom === node.id ? NODE_COLORS[node.type] : "#94a3b8"}
                    className="cursor-crosshair"
                    onClick={(e) => { e.stopPropagation(); startEdge(node.id); }}
                  />
                </g>
              ))}
            </svg>

            {/* Right panel */}
            <div className="w-64 flex-shrink-0 border-l border-zinc-200 bg-white dark:border-zinc-800 dark:bg-zinc-900 overflow-y-auto">
              {selectedNode ? (
                <div className="p-4 space-y-4">
                  <div className="flex items-center justify-between">
                    <p className="text-sm font-semibold text-zinc-700 dark:text-zinc-300">Node Config</p>
                    <button
                      onClick={() => deleteNode(selectedNode.id)}
                      className="rounded px-2 py-0.5 text-xs text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20"
                    >
                      Delete
                    </button>
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-zinc-500 mb-1">Label</label>
                    <input
                      value={selectedNode.data.label}
                      onChange={(e) => {
                        const label = e.target.value;
                        setNodes((prev) =>
                          prev.map((n) => n.id === selectedNode.id ? { ...n, data: { ...n.data, label } } : n)
                        );
                        setSelectedNode((prev) => prev ? { ...prev, data: { ...prev.data, label } } : prev);
                      }}
                      className="w-full rounded-lg border border-zinc-300 px-3 py-1.5 text-sm dark:border-zinc-700 dark:bg-zinc-800 dark:text-zinc-100"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-zinc-500 mb-1">Type</label>
                    <p className="text-sm text-zinc-700 dark:text-zinc-300">{selectedNode.type}</p>
                  </div>
                  {selectedNode.type === "AgentNode" && (
                    <div>
                      <label className="block text-xs font-medium text-zinc-500 mb-1">Model</label>
                      <select
                        value={selectedNode.data.model || "gpt-4o-mini"}
                        onChange={(e) => {
                          const model = e.target.value;
                          setNodes((prev) =>
                            prev.map((n) => n.id === selectedNode.id ? { ...n, data: { ...n.data, model } } : n)
                          );
                        }}
                        className="w-full rounded-lg border border-zinc-300 px-3 py-1.5 text-sm dark:border-zinc-700 dark:bg-zinc-800 dark:text-zinc-100"
                      >
                        <option value="gpt-4o-mini">gpt-4o-mini</option>
                        <option value="gpt-4o">gpt-4o</option>
                        <option value="claude-3-5-sonnet-20241022">claude-3-5-sonnet</option>
                      </select>
                    </div>
                  )}
                  <div>
                    <p className="text-xs font-medium text-zinc-500 mb-1">Connections from this node</p>
                    {edges.filter((e) => e.source === selectedNode.id).map((e) => (
                      <div key={e.id} className="flex items-center justify-between">
                        <span className="text-xs text-zinc-600 dark:text-zinc-400">→ {e.target}</span>
                        <button
                          onClick={() => setEdges((prev) => prev.filter((ed) => ed.id !== e.id))}
                          className="text-xs text-red-400 hover:text-red-600"
                        >
                          ✕
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              ) : (
                <div className="p-4">
                  <p className="text-sm font-semibold text-zinc-700 dark:text-zinc-300 mb-3">Test Run</p>
                  <textarea
                    value={testInput}
                    onChange={(e) => setTestInput(e.target.value)}
                    placeholder="Enter test input…"
                    rows={3}
                    className="w-full rounded-lg border border-zinc-300 px-3 py-2 text-sm dark:border-zinc-700 dark:bg-zinc-800 dark:text-zinc-100"
                  />
                  <button
                    onClick={runWorkflow}
                    disabled={running || !testInput.trim()}
                    className="mt-2 w-full rounded-lg bg-zinc-900 py-2 text-sm text-white disabled:opacity-50 dark:bg-zinc-100 dark:text-zinc-900"
                  >
                    {running ? "Running…" : "▶ Run"}
                  </button>
                  {testOutput.length > 0 && (
                    <div className="mt-3 rounded-lg bg-zinc-50 border border-zinc-200 p-3 dark:bg-zinc-800 dark:border-zinc-700">
                      <p className="mb-1 text-xs font-semibold text-zinc-500">Output</p>
                      {testOutput.map((line, i) => (
                        <p key={i} className="text-xs text-zinc-700 dark:text-zinc-300">{line}</p>
                      ))}
                    </div>
                  )}
                  <div className="mt-4">
                    <p className="text-xs text-zinc-400">
                      Click a node to configure it. Click the ● port on a node, then click another node to draw an edge.
                    </p>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      ) : (
        <div className="flex flex-1 items-center justify-center bg-zinc-50 dark:bg-zinc-950">
          <div className="text-center">
            <p className="text-2xl font-semibold text-zinc-700 dark:text-zinc-300">Workflow Builder</p>
            <p className="mt-2 text-sm text-zinc-500">Create or select a workflow from the sidebar</p>
          </div>
        </div>
      )}
    </div>
  );
}

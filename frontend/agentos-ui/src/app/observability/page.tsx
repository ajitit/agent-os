/**
 * File: observability/page.tsx
 *
 * Observability Dashboard — KPI cards, run trace table, span timeline, log panel.
 */
"use client";

import { useEffect, useState, useCallback } from "react";

type Metrics = {
  totalRuns24h: number;
  successRate: number;
  failureRate: number;
  activeRuns: number;
  avgDurationMs: number;
  totalTokens: number;
};

type Run = {
  runId: string;
  workflowId: string;
  userId: string;
  status: string;
  startedAt: string;
  endedAt?: string;
  durationMs?: number;
  totalTokens?: number;
  error?: string;
};

type Span = {
  spanId: string;
  nodeType: string;
  nodeName: string;
  startedAt: string;
  endedAt?: string;
  durationMs?: number;
  input?: Record<string, unknown>;
  output?: Record<string, unknown>;
  error?: { message: string };
  llmCalls?: { model: string; promptTokens: number; completionTokens: number; latencyMs: number }[];
};

type Log = {
  timestamp: string;
  level: "debug" | "info" | "warn" | "error";
  message: string;
  runId?: string;
};

const STATUS_BADGE: Record<string, string> = {
  running: "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300",
  complete: "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300",
  failed: "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300",
};

const LOG_LEVEL_COLOR: Record<string, string> = {
  debug: "text-zinc-400",
  info: "text-blue-500",
  warn: "text-yellow-500",
  error: "text-red-500",
};

type Tab = "overview" | "traces" | "logs";

export default function ObservabilityPage() {
  const [tab, setTab] = useState<Tab>("overview");
  const [metrics, setMetrics] = useState<Metrics | null>(null);
  const [runs, setRuns] = useState<Run[]>([]);
  const [selectedRun, setSelectedRun] = useState<Run | null>(null);
  const [spans, setSpans] = useState<Span[]>([]);
  const [logs, setLogs] = useState<Log[]>([]);
  const [logLevel, setLogLevel] = useState<string>("");
  const [statusFilter, setStatusFilter] = useState<string>("");
  const token = typeof window !== "undefined" ? localStorage.getItem("agentos_token") : null;

  const authHeader: Record<string, string> = token ? { Authorization: `Bearer ${token}` } : {};

  const fetchMetrics = useCallback(async () => {
    try {
      const res = await fetch("/api/v1/observability/metrics", { headers: authHeader });
      if (res.ok) { const j = await res.json(); setMetrics(j.data); }
    } catch {}
  }, [token]); // eslint-disable-line react-hooks/exhaustive-deps

  const fetchRuns = useCallback(async () => {
    try {
      const params = statusFilter ? `?status=${statusFilter}` : "";
      const res = await fetch(`/api/v1/observability/runs${params}`, { headers: authHeader });
      if (res.ok) { const j = await res.json(); setRuns(j.data || []); }
    } catch {}
  }, [token, statusFilter]); // eslint-disable-line react-hooks/exhaustive-deps

  const fetchLogs = useCallback(async () => {
    try {
      const params = logLevel ? `?level=${logLevel}` : "";
      const res = await fetch(`/api/v1/observability/logs${params}`, { headers: authHeader });
      if (res.ok) { const j = await res.json(); setLogs(j.data || []); }
    } catch {}
  }, [token, logLevel]); // eslint-disable-line react-hooks/exhaustive-deps

  async function fetchRunDetail(run: Run) {
    setSelectedRun(run);
    try {
      const res = await fetch(`/api/v1/observability/runs/${run.runId}`, { headers: authHeader });
      if (res.ok) {
        const j = await res.json();
        setSpans(j.data?.spans || []);
      }
    } catch {}
  }

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    fetchMetrics(); fetchRuns();
    const interval = setInterval(() => { fetchMetrics(); fetchRuns(); }, 10000);
    return () => clearInterval(interval);
  }, [fetchMetrics, fetchRuns]);

  useEffect(() => { if (tab === "logs") fetchLogs(); }, [tab, fetchLogs]); // eslint-disable-line react-hooks/set-state-in-effect

  // ── Render ────────────────────────────────────────────────────────────────

  return (
    <div className="mx-auto max-w-7xl px-6 py-8">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-zinc-900 dark:text-zinc-100">Observability</h1>
          <p className="text-sm text-zinc-500 mt-1">Real-time agent execution monitoring</p>
        </div>
        <button
          onClick={() => { fetchMetrics(); fetchRuns(); }}
          className="rounded-lg border border-zinc-300 px-3 py-1.5 text-sm text-zinc-600 hover:bg-zinc-50 dark:border-zinc-700 dark:text-zinc-300"
        >
          ↻ Refresh
        </button>
      </div>

      {/* Tabs */}
      <div className="mb-6 flex gap-1 rounded-xl border border-zinc-200 bg-zinc-50 p-1 w-fit dark:border-zinc-800 dark:bg-zinc-900">
        {(["overview", "traces", "logs"] as Tab[]).map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`rounded-lg px-4 py-1.5 text-sm font-medium capitalize transition ${
              tab === t
                ? "bg-white shadow text-zinc-900 dark:bg-zinc-800 dark:text-zinc-100"
                : "text-zinc-500 hover:text-zinc-700 dark:text-zinc-400"
            }`}
          >
            {t}
          </button>
        ))}
      </div>

      {/* ── OVERVIEW TAB ─────────────────────────────────────────────────── */}
      {tab === "overview" && (
        <div className="space-y-6">
          {/* KPI Cards */}
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-6">
            {[
              { label: "Total Runs", value: metrics?.totalRuns24h ?? "—" },
              { label: "Success Rate", value: metrics ? `${metrics.successRate}%` : "—" },
              { label: "Failure Rate", value: metrics ? `${metrics.failureRate}%` : "—" },
              { label: "Active Now", value: metrics?.activeRuns ?? "—" },
              { label: "Avg Duration", value: metrics ? `${metrics.avgDurationMs}ms` : "—" },
              { label: "Total Tokens", value: metrics ? metrics.totalTokens.toLocaleString() : "—" },
            ].map(({ label, value }) => (
              <div key={label} className="rounded-xl border border-zinc-200 bg-white p-4 dark:border-zinc-800 dark:bg-zinc-900">
                <p className="text-xs text-zinc-500">{label}</p>
                <p className="mt-1 text-2xl font-bold text-zinc-900 dark:text-zinc-100">{value}</p>
              </div>
            ))}
          </div>

          {/* Recent runs table preview */}
          <div className="rounded-xl border border-zinc-200 bg-white dark:border-zinc-800 dark:bg-zinc-900">
            <div className="border-b border-zinc-200 dark:border-zinc-800 px-4 py-3">
              <p className="text-sm font-semibold text-zinc-700 dark:text-zinc-300">Recent Runs</p>
            </div>
            <RunTable runs={runs.slice(0, 10)} onSelect={fetchRunDetail} />
          </div>
        </div>
      )}

      {/* ── TRACES TAB ───────────────────────────────────────────────────── */}
      {tab === "traces" && (
        <div className="flex gap-6">
          <div className="flex-1 min-w-0">
            <div className="mb-3 flex items-center gap-3">
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="rounded-lg border border-zinc-300 px-3 py-1.5 text-sm dark:border-zinc-700 dark:bg-zinc-800 dark:text-zinc-100"
              >
                <option value="">All statuses</option>
                <option value="running">Running</option>
                <option value="complete">Complete</option>
                <option value="failed">Failed</option>
              </select>
              <button onClick={fetchRuns} className="rounded-lg border border-zinc-300 px-3 py-1.5 text-sm text-zinc-600 hover:bg-zinc-50 dark:border-zinc-700 dark:text-zinc-300">
                Apply
              </button>
            </div>
            <div className="rounded-xl border border-zinc-200 bg-white dark:border-zinc-800 dark:bg-zinc-900">
              <RunTable runs={runs} onSelect={fetchRunDetail} />
            </div>
          </div>

          {/* Trace detail */}
          {selectedRun && (
            <div className="w-96 flex-shrink-0 rounded-xl border border-zinc-200 bg-white dark:border-zinc-800 dark:bg-zinc-900 overflow-hidden">
              <div className="border-b border-zinc-200 dark:border-zinc-800 px-4 py-3 flex items-center justify-between">
                <p className="text-sm font-semibold text-zinc-700 dark:text-zinc-300">Trace: {selectedRun.runId.slice(0, 8)}…</p>
                <button onClick={() => setSelectedRun(null)} className="text-zinc-400 hover:text-zinc-600">✕</button>
              </div>
              <div className="p-4 overflow-y-auto max-h-[60vh] space-y-3">
                {spans.length === 0 ? (
                  <p className="text-sm text-zinc-400">No spans recorded for this run</p>
                ) : (
                  spans.map((span) => (
                    <div key={span.spanId} className="rounded-lg border border-zinc-200 p-3 dark:border-zinc-700">
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-xs font-semibold text-zinc-700 dark:text-zinc-300">{span.nodeName}</span>
                        <span className="text-xs text-zinc-400">{span.durationMs ? `${span.durationMs}ms` : "…"}</span>
                      </div>
                      <p className="text-xs text-zinc-500 capitalize">{span.nodeType}</p>
                      {span.error && (
                        <p className="mt-1 text-xs text-red-500">{span.error.message}</p>
                      )}
                      {span.llmCalls && span.llmCalls.length > 0 && (
                        <p className="mt-1 text-xs text-zinc-400">
                          {span.llmCalls[0].model} · {span.llmCalls[0].promptTokens + span.llmCalls[0].completionTokens} tokens
                        </p>
                      )}
                    </div>
                  ))
                )}
              </div>
            </div>
          )}
        </div>
      )}

      {/* ── LOGS TAB ─────────────────────────────────────────────────────── */}
      {tab === "logs" && (
        <div>
          <div className="mb-3 flex items-center gap-3">
            <select
              value={logLevel}
              onChange={(e) => setLogLevel(e.target.value)}
              className="rounded-lg border border-zinc-300 px-3 py-1.5 text-sm dark:border-zinc-700 dark:bg-zinc-800 dark:text-zinc-100"
            >
              <option value="">All levels</option>
              <option value="debug">Debug</option>
              <option value="info">Info</option>
              <option value="warn">Warn</option>
              <option value="error">Error</option>
            </select>
            <button onClick={fetchLogs} className="rounded-lg border border-zinc-300 px-3 py-1.5 text-sm text-zinc-600 hover:bg-zinc-50 dark:border-zinc-700 dark:text-zinc-300">
              Apply
            </button>
          </div>
          <div className="rounded-xl border border-zinc-200 bg-zinc-900 dark:border-zinc-700">
            <div className="overflow-y-auto max-h-[60vh] p-4 font-mono text-xs space-y-1">
              {logs.length === 0 ? (
                <p className="text-zinc-400">No logs found</p>
              ) : (
                logs.map((log, i) => (
                  <div key={i} className="flex gap-3">
                    <span className="text-zinc-500 shrink-0">{new Date(log.timestamp).toLocaleTimeString()}</span>
                    <span className={`shrink-0 uppercase w-10 ${LOG_LEVEL_COLOR[log.level]}`}>{log.level}</span>
                    <span className="text-zinc-200">{log.message}</span>
                    {log.runId && <span className="text-zinc-500 shrink-0">{log.runId.slice(0, 8)}</span>}
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function RunTable({ runs, onSelect }: { runs: Run[]; onSelect: (r: Run) => void }) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-zinc-200 dark:border-zinc-800 text-xs text-zinc-500">
            <th className="px-4 py-3 text-left font-medium">Run ID</th>
            <th className="px-4 py-3 text-left font-medium">Workflow</th>
            <th className="px-4 py-3 text-left font-medium">Status</th>
            <th className="px-4 py-3 text-left font-medium">Duration</th>
            <th className="px-4 py-3 text-left font-medium">Tokens</th>
            <th className="px-4 py-3 text-left font-medium">Started</th>
          </tr>
        </thead>
        <tbody>
          {runs.length === 0 ? (
            <tr>
              <td colSpan={6} className="px-4 py-8 text-center text-zinc-400 text-sm">
                No runs recorded yet — send a message in Chat to see traces here.
              </td>
            </tr>
          ) : (
            runs.map((run) => (
              <tr
                key={run.runId}
                onClick={() => onSelect(run)}
                className="border-b border-zinc-100 hover:bg-zinc-50 cursor-pointer dark:border-zinc-800 dark:hover:bg-zinc-800/50"
              >
                <td className="px-4 py-3 font-mono text-xs text-zinc-600 dark:text-zinc-400">
                  {run.runId.slice(0, 8)}…
                </td>
                <td className="px-4 py-3 text-zinc-700 dark:text-zinc-300">
                  {run.workflowId || "—"}
                </td>
                <td className="px-4 py-3">
                  <span className={`inline-block rounded-full px-2 py-0.5 text-xs font-medium ${STATUS_BADGE[run.status] || "bg-zinc-100 text-zinc-500"}`}>
                    {run.status}
                  </span>
                </td>
                <td className="px-4 py-3 text-zinc-600 dark:text-zinc-400">
                  {run.durationMs ? `${run.durationMs}ms` : "—"}
                </td>
                <td className="px-4 py-3 text-zinc-600 dark:text-zinc-400">
                  {run.totalTokens ?? "—"}
                </td>
                <td className="px-4 py-3 text-zinc-500 text-xs">
                  {run.startedAt ? new Date(run.startedAt).toLocaleTimeString() : "—"}
                </td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
}

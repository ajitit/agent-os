"use client";

import { useState, useEffect, useCallback } from "react";

interface AuditEvent {
  id: string;
  timestamp: string;
  actorType: string;
  actorId: string;
  actorName?: string;
  action: string;
  resourceType?: string;
  resourceId?: string;
  resourceName?: string;
  outcome: string;
  durationMs?: number;
  ip?: string;
  details?: Record<string, unknown>;
}

interface AuditStats {
  total: number;
  by_actor_type: Record<string, number>;
  by_outcome: Record<string, number>;
  daily_counts: Record<string, number>;
}

const API = "/api/v1";

function getToken(): string {
  return typeof window !== "undefined" ? localStorage.getItem("vishwakarma_token") ?? "" : "";
}

async function apiFetch<T>(path: string, opts?: RequestInit): Promise<T> {
  const res = await fetch(`${API}${path}`, {
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${getToken()}`,
      ...(opts?.headers ?? {}),
    },
    ...opts,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail ?? `HTTP ${res.status}`);
  }
  const json = await res.json();
  return (json.data ?? json) as T;
}

const ACTOR_STYLES: Record<string, string> = {
  human:  "bg-blue-900/60 text-blue-300 border-blue-800/50",
  agent:  "bg-purple-900/60 text-purple-300 border-purple-800/50",
  crew:   "bg-amber-900/60 text-amber-300 border-amber-800/50",
  system: "bg-slate-700/60 text-slate-300 border-slate-600/50",
};

const ACTOR_ICONS: Record<string, string> = {
  human: "👤", agent: "🤖", crew: "👥", system: "⚙️",
};

const OUTCOME_STYLES: Record<string, string> = {
  success: "text-emerald-400",
  failure: "text-red-400",
  error:   "text-red-400",
};

export default function AuditPage() {
  const [events, setEvents] = useState<AuditEvent[]>([]);
  const [stats, setStats] = useState<AuditStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [expanded, setExpanded] = useState<string | null>(null);

  // Filters
  const [actorType, setActorType] = useState("");
  const [action, setAction] = useState("");
  const [resourceType, setResourceType] = useState("");
  const [limit] = useState(200);

  const buildQuery = () => {
    const p = new URLSearchParams();
    if (actorType) p.set("actor_type", actorType);
    if (action) p.set("action", action);
    if (resourceType) p.set("resource_type", resourceType);
    p.set("limit", String(limit));
    return p.toString() ? `?${p.toString()}` : "";
  };

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const [evts, st] = await Promise.all([
        apiFetch<AuditEvent[]>(`/audit${buildQuery()}`),
        apiFetch<AuditStats>("/audit/stats"),
      ]);
      setEvents(evts);
      setStats(st);
    } catch {
      // silently ignore
    } finally {
      setLoading(false);
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [actorType, action, resourceType, limit]);

  useEffect(() => { load(); }, [load]);

  const exportCsv = () => {
    const p = new URLSearchParams();
    if (actorType) p.set("actor_type", actorType);
    if (action) p.set("action", action);
    if (resourceType) p.set("resource_type", resourceType);
    window.open(`${API}/audit/export?${p.toString()}&limit=10000`, "_blank");
  };

  return (
    <div className="min-h-screen bg-[#0d0f14] text-slate-100 font-mono">
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-orange-700 to-amber-900 flex items-center justify-center text-xl">📋</div>
            <div>
              <h1 className="text-2xl font-bold text-white tracking-tight font-sans">Audit Log</h1>
              <p className="text-sm text-slate-400 font-sans">Immutable record of all human, agent & system actions</p>
            </div>
          </div>
          <button
            onClick={exportCsv}
            className="px-4 py-2 bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-300 text-xs font-semibold rounded-xl transition-colors font-sans"
          >
            ↓ Export CSV
          </button>
        </div>

        {/* Stats bar */}
        {stats && (
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-6">
            <div className="rounded-xl bg-slate-900 border border-slate-800 p-4">
              <div className="text-2xl font-bold text-white">{stats.total.toLocaleString()}</div>
              <div className="text-xs text-slate-500 mt-0.5 font-sans">Total Events</div>
            </div>
            {Object.entries(stats.by_actor_type).map(([type, count]) => (
              <div key={type} className="rounded-xl bg-slate-900 border border-slate-800 p-4">
                <div className="text-2xl font-bold text-white">{count.toLocaleString()}</div>
                <div className="flex items-center gap-1 mt-0.5">
                  <span>{ACTOR_ICONS[type] ?? "?"}</span>
                  <span className="text-xs text-slate-500 capitalize font-sans">{type}</span>
                </div>
              </div>
            ))}
            <div className="rounded-xl bg-slate-900 border border-slate-800 p-4">
              <div className="text-2xl font-bold text-emerald-400">{stats.by_outcome?.success ?? 0}</div>
              <div className="text-xs text-slate-500 mt-0.5 font-sans">Successes</div>
            </div>
          </div>
        )}

        {/* Filters */}
        <div className="flex flex-wrap gap-2 mb-4">
          <select
            value={actorType}
            onChange={(e) => setActorType(e.target.value)}
            className="bg-slate-900 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-slate-300 focus:outline-none focus:border-orange-600 font-sans"
          >
            <option value="">All actors</option>
            <option value="human">Human</option>
            <option value="agent">Agent</option>
            <option value="crew">Crew</option>
            <option value="system">System</option>
          </select>

          <select
            value={resourceType}
            onChange={(e) => setResourceType(e.target.value)}
            className="bg-slate-900 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-slate-300 focus:outline-none focus:border-orange-600 font-sans"
          >
            <option value="">All resources</option>
            <option value="agent">Agent</option>
            <option value="plan">Plan</option>
            <option value="run">Run</option>
            <option value="workflow">Workflow</option>
            <option value="skill">Skill</option>
            <option value="tool">Tool</option>
            <option value="model">Model</option>
          </select>

          <input
            type="text"
            value={action}
            onChange={(e) => setAction(e.target.value)}
            placeholder="Filter action…"
            className="bg-slate-900 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-slate-300 focus:outline-none focus:border-orange-600 placeholder-slate-600 font-sans w-40"
          />

          <button onClick={load} className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-400 text-xs rounded-lg border border-slate-700 font-sans">
            ↻ Refresh
          </button>

          {(actorType || action || resourceType) && (
            <button onClick={() => { setActorType(""); setAction(""); setResourceType(""); }} className="px-3 py-1.5 bg-slate-900 text-orange-500 text-xs rounded-lg border border-slate-800 font-sans">
              ✕ Clear
            </button>
          )}
        </div>

        {/* Event count */}
        <div className="text-xs text-slate-600 mb-3 font-sans">
          {loading ? "Loading…" : `${events.length} events`}
        </div>

        {/* Events table */}
        <div className="rounded-xl border border-slate-800 overflow-hidden">
          {/* Table header */}
          <div className="grid grid-cols-12 gap-2 px-4 py-2 bg-slate-900/80 border-b border-slate-800 text-xs text-slate-500 uppercase tracking-wider">
            <div className="col-span-2">Timestamp</div>
            <div className="col-span-2">Actor</div>
            <div className="col-span-3">Action</div>
            <div className="col-span-2">Resource</div>
            <div className="col-span-1">Outcome</div>
            <div className="col-span-2">Duration</div>
          </div>

          {events.length === 0 && !loading ? (
            <div className="py-16 text-center text-slate-500 font-sans text-sm">
              No audit events found.{actorType || action ? " Try clearing filters." : ""}
            </div>
          ) : (
            <div className="divide-y divide-slate-800/50 max-h-[600px] overflow-y-auto">
              {events.map((ev) => (
                <div key={ev.id}>
                  <button
                    className={`w-full grid grid-cols-12 gap-2 px-4 py-2.5 text-left hover:bg-slate-800/30 transition-colors text-xs ${expanded === ev.id ? "bg-slate-800/40" : ""}`}
                    onClick={() => setExpanded(expanded === ev.id ? null : ev.id)}
                  >
                    <div className="col-span-2 text-slate-500 truncate">
                      {new Date(ev.timestamp).toLocaleTimeString()}<br />
                      <span className="text-slate-700">{new Date(ev.timestamp).toLocaleDateString()}</span>
                    </div>
                    <div className="col-span-2">
                      <span className={`inline-flex items-center gap-1 px-1.5 py-0.5 rounded border text-xs font-sans ${ACTOR_STYLES[ev.actorType] ?? "bg-slate-800 text-slate-300"}`}>
                        {ACTOR_ICONS[ev.actorType] ?? "?"} {ev.actorName || ev.actorId.slice(0, 8)}
                      </span>
                    </div>
                    <div className="col-span-3 text-slate-300 font-medium truncate">{ev.action}</div>
                    <div className="col-span-2 text-slate-500 truncate">
                      {ev.resourceType && <span className="text-slate-600">{ev.resourceType}/</span>}
                      {ev.resourceName || (ev.resourceId ? ev.resourceId.slice(0, 8) + "…" : "—")}
                    </div>
                    <div className={`col-span-1 font-medium ${OUTCOME_STYLES[ev.outcome] ?? "text-slate-400"}`}>
                      {ev.outcome === "success" ? "✓" : "✗"}
                    </div>
                    <div className="col-span-2 text-slate-600">
                      {ev.durationMs !== undefined ? `${ev.durationMs}ms` : "—"}
                    </div>
                  </button>

                  {/* Expanded detail */}
                  {expanded === ev.id && (
                    <div className="bg-slate-900/60 border-t border-slate-800/50 px-4 py-3">
                      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs mb-3 font-sans">
                        {[
                          ["Event ID", ev.id],
                          ["Actor ID", ev.actorId],
                          ["Resource ID", ev.resourceId || "—"],
                          ["IP", ev.ip || "—"],
                        ].map(([k, v]) => (
                          <div key={k}>
                            <div className="text-slate-600">{k}</div>
                            <div className="text-slate-300 font-mono mt-0.5 break-all">{v}</div>
                          </div>
                        ))}
                      </div>
                      {ev.details && Object.keys(ev.details).length > 0 && (
                        <div>
                          <div className="text-xs text-slate-600 mb-1 font-sans">Details</div>
                          <pre className="text-xs text-slate-300 bg-slate-950 rounded-lg p-3 overflow-x-auto border border-slate-800">
                            {JSON.stringify(ev.details, null, 2)}
                          </pre>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

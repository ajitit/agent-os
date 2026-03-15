"use client";

import { useState, useCallback, useEffect } from "react";

// ── Types ─────────────────────────────────────────────────────────────────────

type FilterVerdict = "pass" | "junk" | "personal" | "confidential" | "blocked";
type PipelineStatus =
  | "pending"
  | "running"
  | "awaiting_review"
  | "approved"
  | "rejected"
  | "complete"
  | "blocked"
  | "failed";

interface ProcessResponse {
  run_id: string;
  status: PipelineStatus;
  filter_verdict: FilterVerdict | null;
  filter_reason: string | null;
  entity_count: number;
  mask_count: number;
  category: string | null;
  intent: string | null;
  route_primary: string | null;
  final_result: string | null;
  stage_errors: Record<string, string>;
  blocked_message: string | null;
}

interface FilterPattern {
  id: string;
  name: string;
  verdict: string;
  pattern: string;
  description: string;
  enabled: boolean;
}

interface MaskPattern {
  id: string;
  name: string;
  pattern: string;
  placeholder: string;
  description: string;
  enabled: boolean;
}

interface OntologyConcept {
  id: string;
  label: string;
  domain: string;
  entity_types: string[];
  aliases: string[];
  description: string;
  enabled: boolean;
}

interface PipelineRun {
  run_id: string;
  status: PipelineStatus;
  filter_verdict: string | null;
  category: string | null;
  intent: string | null;
  entity_count: number;
  mask_count: number;
  final_result: string | null;
  created_at: string;
}

interface PendingReview {
  run_id: string;
  status: string;
  summary: string;
}

// ── Constants ─────────────────────────────────────────────────────────────────

const API = "/api/v1";

const STAGES = [
  { id: 1, key: "filter", label: "Filter", icon: "🛡️", desc: "Block junk, personal & confidential data" },
  { id: 2, key: "extract", label: "Extract", icon: "🔍", desc: "Named entity recognition" },
  { id: 3, key: "map", label: "Map", icon: "🗺️", desc: "Entity → ontology concept mapping" },
  { id: 4, key: "mask", label: "Mask", icon: "🎭", desc: "Redact sensitive tokens" },
  { id: 5, key: "route", label: "Route", icon: "🔀", desc: "Select target agents" },
  { id: 6, key: "classify", label: "Classify", icon: "🏷️", desc: "Intent, category & sentiment" },
  { id: 7, key: "aggregate", label: "Aggregate", icon: "⚗️", desc: "Synthesise agent outputs" },
  { id: 8, key: "result", label: "Result", icon: "✅", desc: "Compose final response" },
  { id: 9, key: "review", label: "Review", icon: "👁️", desc: "Human-in-the-loop approval" },
];

// ── Helpers ───────────────────────────────────────────────────────────────────

function getToken(): string {
  return typeof window !== "undefined"
    ? localStorage.getItem("agentos_token") ?? ""
    : "";
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
    throw new Error(err.detail ?? err.error ?? `HTTP ${res.status}`);
  }
  const json = await res.json();
  return (json.data ?? json) as T;
}

function statusColor(status: PipelineStatus): string {
  const map: Record<PipelineStatus, string> = {
    pending: "bg-slate-700 text-slate-200",
    running: "bg-blue-800 text-blue-200",
    awaiting_review: "bg-amber-800 text-amber-200",
    approved: "bg-emerald-800 text-emerald-200",
    rejected: "bg-red-800 text-red-200",
    complete: "bg-emerald-800 text-emerald-200",
    blocked: "bg-red-800 text-red-200",
    failed: "bg-red-900 text-red-200",
  };
  return map[status] ?? "bg-slate-700 text-slate-200";
}

function verdictColor(v: FilterVerdict | null): string {
  if (!v || v === "pass") return "text-emerald-400";
  if (v === "junk") return "text-amber-400";
  return "text-red-400";
}

function getActiveStage(result: ProcessResponse | null): number {
  if (!result) return 0;
  if (result.status === "blocked") return 1;
  if (result.status === "awaiting_review") return 9;
  if (result.status === "complete" || result.status === "approved" || result.status === "rejected") return 9;
  return 8;
}

// ── Sub-components ────────────────────────────────────────────────────────────

function StageIndicator({ result, active }: { result: ProcessResponse | null; active: boolean }) {
  const reached = getActiveStage(result);
  return (
    <div className="flex items-center gap-0 mb-6 overflow-x-auto pb-1">
      {STAGES.map((stage, idx) => {
        const done = result && reached >= stage.id && result.status !== "running";
        const isBlocked = result?.status === "blocked" && stage.id === 1;
        const isCurrent = active && stage.id === reached;
        const isAwaiting = result?.status === "awaiting_review" && stage.id === 9;

        return (
          <div key={stage.key} className="flex items-center">
            <div className="flex flex-col items-center min-w-[64px]">
              <div
                className={`w-10 h-10 rounded-full flex items-center justify-center text-lg font-bold transition-all duration-300 ${
                  isBlocked
                    ? "bg-red-800 ring-2 ring-red-500"
                    : isAwaiting
                    ? "bg-amber-700 ring-2 ring-amber-400 animate-pulse"
                    : isCurrent
                    ? "bg-blue-700 ring-2 ring-blue-400 animate-pulse"
                    : done
                    ? "bg-emerald-800 ring-1 ring-emerald-600"
                    : "bg-slate-800 ring-1 ring-slate-600 opacity-50"
                }`}
                title={stage.desc}
              >
                {stage.icon}
              </div>
              <span className="text-[10px] mt-1 text-slate-400 text-center leading-tight">
                {stage.label}
              </span>
            </div>
            {idx < STAGES.length - 1 && (
              <div
                className={`h-[2px] w-4 mx-0.5 mb-4 transition-colors duration-500 ${
                  done && reached > stage.id ? "bg-emerald-700" : "bg-slate-700"
                }`}
              />
            )}
          </div>
        );
      })}
    </div>
  );
}

function ResultCard({ result }: { result: ProcessResponse }) {
  const isBlocked = result.status === "blocked";
  return (
    <div
      className={`rounded-xl border p-5 mt-4 ${
        isBlocked
          ? "border-red-800 bg-red-950/40"
          : result.status === "complete" || result.status === "approved"
          ? "border-emerald-800 bg-emerald-950/30"
          : "border-amber-800 bg-amber-950/30"
      }`}
    >
      <div className="flex items-center gap-3 mb-4">
        <span className="text-xl">{isBlocked ? "🚫" : result.status === "complete" ? "✅" : "⏳"}</span>
        <div>
          <span
            className={`text-xs font-mono px-2 py-0.5 rounded-full ${statusColor(result.status)}`}
          >
            {result.status.toUpperCase()}
          </span>
          <span className="text-xs text-slate-500 ml-2 font-mono">{result.run_id.slice(0, 8)}…</span>
        </div>
      </div>

      {isBlocked ? (
        <p className="text-red-300 text-sm">{result.blocked_message}</p>
      ) : (
        <>
          {/* Stage summary pills */}
          <div className="flex flex-wrap gap-2 mb-4">
            <Pill label="Filter" value={result.filter_verdict ?? "—"} color={verdictColor(result.filter_verdict)} />
            <Pill label="Entities" value={String(result.entity_count)} color="text-cyan-400" />
            <Pill label="Masked" value={String(result.mask_count)} color="text-purple-400" />
            {result.category && <Pill label="Category" value={result.category} color="text-blue-400" />}
            {result.intent && <Pill label="Intent" value={result.intent} color="text-indigo-400" />}
            {result.route_primary && <Pill label="Routed to" value={result.route_primary} color="text-amber-400" />}
          </div>

          {/* Final output */}
          {result.final_result && (
            <div className="bg-slate-900 rounded-lg p-4 font-mono text-sm text-slate-200 whitespace-pre-wrap border border-slate-700">
              {result.final_result}
            </div>
          )}

          {/* Stage errors */}
          {Object.keys(result.stage_errors).length > 0 && (
            <div className="mt-3 space-y-1">
              {Object.entries(result.stage_errors).map(([stage, err]) => (
                <p key={stage} className="text-xs text-amber-400">
                  ⚠ {stage}: {err}
                </p>
              ))}
            </div>
          )}
        </>
      )}
    </div>
  );
}

function Pill({ label, value, color }: { label: string; value: string; color: string }) {
  return (
    <div className="flex items-center gap-1.5 bg-slate-800 rounded-full px-3 py-1 text-xs border border-slate-700">
      <span className="text-slate-400">{label}:</span>
      <span className={`font-semibold ${color}`}>{value}</span>
    </div>
  );
}

// ── Tabs ──────────────────────────────────────────────────────────────────────

function ProcessTab() {
  const [text, setText] = useState("");
  const [requireReview, setRequireReview] = useState(false);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ProcessResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = useCallback(async () => {
    if (!text.trim() || loading) return;
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const res = await apiFetch<ProcessResponse>("/pipeline/process", {
        method: "POST",
        body: JSON.stringify({ text: text.trim(), require_review: requireReview }),
      });
      setResult(res);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  }, [text, requireReview, loading]);

  return (
    <div className="space-y-6">
      <StageIndicator result={result} active={loading} />

      <div className="space-y-3">
        <label className="block text-sm font-medium text-slate-300">Input Text</label>
        <textarea
          className="w-full bg-slate-900 border border-slate-700 rounded-xl p-4 text-sm text-slate-100 font-mono resize-none focus:outline-none focus:border-blue-500 transition-colors placeholder-slate-600"
          rows={6}
          placeholder="Enter text to process through the 9-stage pipeline…"
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) handleSubmit();
          }}
        />
      </div>

      <div className="flex items-center justify-between">
        <label className="flex items-center gap-2.5 cursor-pointer select-none">
          <div
            className={`w-10 h-5 rounded-full transition-colors relative ${requireReview ? "bg-amber-700" : "bg-slate-700"}`}
            onClick={() => setRequireReview(!requireReview)}
          >
            <div
              className={`absolute top-0.5 left-0.5 w-4 h-4 rounded-full bg-white transition-transform ${requireReview ? "translate-x-5" : ""}`}
            />
          </div>
          <span className="text-sm text-slate-300">
            Require human review (Stage 9)
          </span>
        </label>
        <button
          onClick={handleSubmit}
          disabled={!text.trim() || loading}
          className="px-5 py-2.5 rounded-xl bg-blue-700 hover:bg-blue-600 disabled:opacity-40 text-white text-sm font-semibold transition-all flex items-center gap-2"
        >
          {loading ? (
            <>
              <span className="w-4 h-4 border-2 border-blue-300 border-t-transparent rounded-full animate-spin" />
              Processing…
            </>
          ) : (
            <>▶ Run Pipeline</>
          )}
        </button>
      </div>

      {error && (
        <div className="bg-red-950/50 border border-red-800 rounded-xl p-4 text-sm text-red-300">
          {error}
        </div>
      )}

      {result && <ResultCard result={result} />}
    </div>
  );
}

function RunsTab() {
  const [runs, setRuns] = useState<PipelineRun[]>([]);
  const [loading, setLoading] = useState(true);
  const [selected, setSelected] = useState<PipelineRun | null>(null);

  const load = useCallback(async () => {
    try {
      const data = await apiFetch<PipelineRun[]>("/pipeline/runs?limit=50");
      setRuns(data);
    } catch {
      setRuns([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
    const id = setInterval(load, 15000);
    return () => clearInterval(id);
  }, [load]);

  return (
    <div className="flex gap-4">
      <div className="flex-1 space-y-2">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-sm font-medium text-slate-300">Recent Runs</h3>
          <button onClick={load} className="text-xs text-slate-500 hover:text-slate-300 transition-colors">↻ Refresh</button>
        </div>
        {loading ? (
          <div className="text-slate-500 text-sm">Loading…</div>
        ) : runs.length === 0 ? (
          <div className="text-slate-500 text-sm">No runs yet. Submit input on the Process tab.</div>
        ) : (
          runs.map((run) => (
            <button
              key={run.run_id}
              onClick={() => setSelected(run)}
              className={`w-full text-left rounded-xl border p-3 transition-all ${
                selected?.run_id === run.run_id
                  ? "border-blue-600 bg-blue-950/30"
                  : "border-slate-700 bg-slate-800/40 hover:border-slate-600"
              }`}
            >
              <div className="flex items-center justify-between mb-1">
                <span className="font-mono text-xs text-slate-400">{run.run_id.slice(0, 12)}…</span>
                <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${statusColor(run.status)}`}>
                  {run.status}
                </span>
              </div>
              <div className="flex flex-wrap gap-2 mt-1">
                {run.category && <Pill label="Cat" value={run.category} color="text-blue-400" />}
                {run.intent && <Pill label="Intent" value={run.intent} color="text-indigo-400" />}
                <Pill label="Entities" value={String(run.entity_count)} color="text-cyan-400" />
              </div>
            </button>
          ))
        )}
      </div>
      {selected && (
        <div className="w-80 shrink-0 bg-slate-800/60 rounded-xl border border-slate-700 p-4 space-y-3">
          <h4 className="text-sm font-semibold text-slate-200">Run Detail</h4>
          <div className="space-y-2 text-xs font-mono">
            {[
              ["ID", selected.run_id],
              ["Status", selected.status],
              ["Filter", selected.filter_verdict ?? "—"],
              ["Category", selected.category ?? "—"],
              ["Intent", selected.intent ?? "—"],
              ["Entities", String(selected.entity_count)],
              ["Masked", String(selected.mask_count)],
            ].map(([k, v]) => (
              <div key={k} className="flex justify-between gap-2">
                <span className="text-slate-500">{k}</span>
                <span className="text-slate-300 text-right break-all">{v}</span>
              </div>
            ))}
          </div>
          {selected.final_result && (
            <div className="bg-slate-900 rounded-lg p-3 text-xs text-slate-300 whitespace-pre-wrap border border-slate-700 max-h-40 overflow-y-auto">
              {selected.final_result}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function ReviewTab() {
  const [pending, setPending] = useState<PendingReview[]>([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState<string | null>(null);
  const [comment, setComment] = useState<Record<string, string>>({});

  const load = useCallback(async () => {
    try {
      const data = await apiFetch<PendingReview[]>("/pipeline/review/pending");
      setPending(data);
    } catch {
      setPending([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
    const id = setInterval(load, 5000);
    return () => clearInterval(id);
  }, [load]);

  const respond = useCallback(async (runId: string, approved: boolean) => {
    setSubmitting(runId);
    try {
      await apiFetch(`/pipeline/review/${runId}/respond`, {
        method: "POST",
        body: JSON.stringify({ approved, comment: comment[runId] ?? null }),
      });
      await load();
    } catch {
      // ignore
    } finally {
      setSubmitting(null);
    }
  }, [comment, load]);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-medium text-slate-300">Pending Reviews</h3>
        <div className="flex items-center gap-2">
          {pending.length > 0 && (
            <span className="text-xs bg-amber-800 text-amber-200 px-2 py-0.5 rounded-full font-medium">
              {pending.length} waiting
            </span>
          )}
          <button onClick={load} className="text-xs text-slate-500 hover:text-slate-300 transition-colors">↻</button>
        </div>
      </div>

      {loading ? (
        <div className="text-slate-500 text-sm">Loading…</div>
      ) : pending.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-12 text-center">
          <span className="text-4xl mb-3">👁️</span>
          <p className="text-slate-400 text-sm">No pipelines awaiting review.</p>
          <p className="text-slate-600 text-xs mt-1">Run a pipeline with &quot;Require human review&quot; enabled.</p>
        </div>
      ) : (
        pending.map((review) => (
          <div key={review.run_id} className="rounded-xl border border-amber-800/60 bg-amber-950/20 p-4 space-y-3">
            <div className="flex items-center gap-2">
              <span className="text-amber-400 text-lg">⏳</span>
              <div>
                <div className="text-sm font-medium text-slate-200">Review Required</div>
                <div className="text-xs font-mono text-slate-500">{review.run_id.slice(0, 16)}…</div>
              </div>
            </div>
            {review.summary && (
              <div className="bg-slate-900 rounded-lg p-3 text-xs text-slate-300 font-mono border border-slate-700 max-h-32 overflow-y-auto">
                {review.summary}
              </div>
            )}
            <textarea
              className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2.5 text-xs text-slate-300 resize-none focus:outline-none focus:border-amber-600"
              rows={2}
              placeholder="Optional reviewer comment…"
              value={comment[review.run_id] ?? ""}
              onChange={(e) => setComment(prev => ({ ...prev, [review.run_id]: e.target.value }))}
            />
            <div className="flex gap-2">
              <button
                onClick={() => respond(review.run_id, true)}
                disabled={submitting === review.run_id}
                className="flex-1 py-2 rounded-lg bg-emerald-800 hover:bg-emerald-700 text-emerald-200 text-xs font-semibold transition-colors disabled:opacity-50"
              >
                ✓ Approve
              </button>
              <button
                onClick={() => respond(review.run_id, false)}
                disabled={submitting === review.run_id}
                className="flex-1 py-2 rounded-lg bg-red-900 hover:bg-red-800 text-red-200 text-xs font-semibold transition-colors disabled:opacity-50"
              >
                ✗ Reject
              </button>
            </div>
          </div>
        ))
      )}
    </div>
  );
}

function MemoryTab() {
  const [tab, setTab] = useState<"filter" | "mask">("filter");
  const [filters, setFilters] = useState<FilterPattern[]>([]);
  const [masks, setMasks] = useState<MaskPattern[]>([]);
  const [loading, setLoading] = useState(true);

  const loadFilters = useCallback(async () => {
    try {
      const data = await apiFetch<FilterPattern[]>("/pipeline/memory/filter");
      setFilters(data);
    } catch { setFilters([]); }
  }, []);

  const loadMasks = useCallback(async () => {
    try {
      const data = await apiFetch<MaskPattern[]>("/pipeline/memory/mask");
      setMasks(data);
    } catch { setMasks([]); }
  }, []);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    Promise.all([loadFilters(), loadMasks()]).finally(() => setLoading(false));
  }, [loadFilters, loadMasks]);

  const toggleFilter = useCallback(async (p: FilterPattern) => {
    try {
      await apiFetch(`/pipeline/memory/filter/${p.id}`, {
        method: "PUT",
        body: JSON.stringify({ enabled: !p.enabled }),
      });
      await loadFilters();
    } catch { }
  }, [loadFilters]);

  const toggleMask = useCallback(async (p: MaskPattern) => {
    try {
      await apiFetch(`/pipeline/memory/mask/${p.id}`, {
        method: "PUT",
        body: JSON.stringify({ enabled: !p.enabled }),
      });
      await loadMasks();
    } catch { }
  }, [loadMasks]);

  const verdictBadge: Record<string, string> = {
    junk: "bg-amber-900 text-amber-300",
    personal: "bg-blue-900 text-blue-300",
    confidential: "bg-red-900 text-red-300",
    blocked: "bg-red-950 text-red-400",
  };

  return (
    <div className="space-y-4">
      <div className="flex gap-2">
        {(["filter", "mask"] as const).map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`px-4 py-2 rounded-lg text-xs font-semibold capitalize transition-colors ${
              tab === t ? "bg-blue-800 text-blue-100" : "bg-slate-800 text-slate-400 hover:bg-slate-700"
            }`}
          >
            {t === "filter" ? "🛡️ Filter Patterns" : "🎭 Mask Patterns"}
          </button>
        ))}
      </div>

      {loading ? (
        <div className="text-slate-500 text-sm">Loading…</div>
      ) : tab === "filter" ? (
        <div className="space-y-2">
          <p className="text-xs text-slate-500 mb-3">
            Filter patterns define what content is blocked before processing. Click to toggle.
          </p>
          {filters.map((p) => (
            <div
              key={p.id}
              className={`rounded-xl border p-3 transition-all cursor-pointer ${
                p.enabled ? "border-slate-600 bg-slate-800/50" : "border-slate-800 bg-slate-900/30 opacity-50"
              }`}
              onClick={() => toggleFilter(p)}
            >
              <div className="flex items-center justify-between mb-1">
                <span className="text-sm font-medium text-slate-200">{p.name}</span>
                <div className="flex items-center gap-2">
                  <span className={`text-xs px-2 py-0.5 rounded-full ${verdictBadge[p.verdict] ?? "bg-slate-700 text-slate-300"}`}>
                    {p.verdict}
                  </span>
                  <div className={`w-8 h-4 rounded-full ${p.enabled ? "bg-emerald-700" : "bg-slate-700"}`} />
                </div>
              </div>
              <p className="text-xs text-slate-500">{p.description}</p>
              <code className="text-xs text-purple-400 font-mono mt-1 block truncate">{p.pattern}</code>
            </div>
          ))}
        </div>
      ) : (
        <div className="space-y-2">
          <p className="text-xs text-slate-500 mb-3">
            Mask patterns define what gets redacted. Click to toggle.
          </p>
          {masks.map((p) => (
            <div
              key={p.id}
              className={`rounded-xl border p-3 transition-all cursor-pointer ${
                p.enabled ? "border-slate-600 bg-slate-800/50" : "border-slate-800 bg-slate-900/30 opacity-50"
              }`}
              onClick={() => toggleMask(p)}
            >
              <div className="flex items-center justify-between mb-1">
                <span className="text-sm font-medium text-slate-200">{p.name}</span>
                <div className="flex items-center gap-2">
                  <span className="text-xs px-2 py-0.5 rounded-full bg-purple-900 text-purple-300 font-mono">
                    {p.placeholder}
                  </span>
                  <div className={`w-8 h-4 rounded-full ${p.enabled ? "bg-emerald-700" : "bg-slate-700"}`} />
                </div>
              </div>
              <p className="text-xs text-slate-500">{p.description}</p>
              <code className="text-xs text-purple-400 font-mono mt-1 block truncate">{p.pattern}</code>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function OntologyTab() {
  const [concepts, setConcepts] = useState<OntologyConcept[]>([]);
  const [domain, setDomain] = useState<string>("all");
  const [loading, setLoading] = useState(true);
  const [selected, setSelected] = useState<OntologyConcept | null>(null);

  const load = useCallback(async (d?: string) => {
    setLoading(true);
    try {
      const q = d && d !== "all" ? `?domain=${d}` : "";
      const data = await apiFetch<OntologyConcept[]>(`/pipeline/ontology${q}`);
      setConcepts(data);
    } catch { setConcepts([]); }
    setLoading(false);
  }, []);

  useEffect(() => { load(); }, [load]); // eslint-disable-line react-hooks/set-state-in-effect

  const domainColor: Record<string, string> = {
    healthcare: "bg-emerald-900 text-emerald-300",
    finance: "bg-blue-900 text-blue-300",
    technology: "bg-purple-900 text-purple-300",
    general: "bg-slate-700 text-slate-300",
  };

  const domains = ["all", "healthcare", "finance", "technology", "general"];

  return (
    <div className="space-y-4">
      <div className="flex gap-2 flex-wrap">
        {domains.map((d) => (
          <button
            key={d}
            onClick={() => { setDomain(d); load(d); }}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium capitalize transition-colors ${
              domain === d ? "bg-blue-800 text-blue-100" : "bg-slate-800 text-slate-400 hover:bg-slate-700"
            }`}
          >
            {d}
          </button>
        ))}
      </div>

      {loading ? (
        <div className="text-slate-500 text-sm">Loading…</div>
      ) : (
        <div className="grid grid-cols-1 gap-2">
          {concepts.map((c) => (
            <div
              key={c.id}
              className={`rounded-xl border p-3 cursor-pointer transition-all ${
                selected?.id === c.id
                  ? "border-blue-600 bg-blue-950/30"
                  : "border-slate-700 bg-slate-800/40 hover:border-slate-600"
              }`}
              onClick={() => setSelected(selected?.id === c.id ? null : c)}
            >
              <div className="flex items-start justify-between gap-2">
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <span className="font-mono text-xs text-slate-500">{c.id}</span>
                    <span className={`text-xs px-2 py-0.5 rounded-full ${domainColor[c.domain] ?? "bg-slate-700 text-slate-300"}`}>
                      {c.domain}
                    </span>
                  </div>
                  <span className="text-sm font-medium text-slate-200">{c.label}</span>
                  {c.description && (
                    <p className="text-xs text-slate-500 mt-0.5">{c.description}</p>
                  )}
                </div>
              </div>
              {selected?.id === c.id && (
                <div className="mt-3 space-y-2 text-xs">
                  <div>
                    <span className="text-slate-500">Entity Types: </span>
                    {c.entity_types.map((t) => (
                      <span key={t} className="bg-slate-700 text-slate-300 px-1.5 py-0.5 rounded mr-1 font-mono">
                        {t}
                      </span>
                    ))}
                  </div>
                  {c.aliases.length > 0 && (
                    <div>
                      <span className="text-slate-500">Aliases: </span>
                      <span className="text-slate-300">{c.aliases.join(", ")}</span>
                    </div>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// ── Main Page ─────────────────────────────────────────────────────────────────

const TABS = [
  { key: "process", label: "▶ Process", desc: "Run input through pipeline" },
  { key: "runs", label: "📋 Runs", desc: "History" },
  { key: "review", label: "👁️ Review", desc: "Human-in-the-loop" },
  { key: "memory", label: "🧠 Memory", desc: "Filter & mask patterns" },
  { key: "ontology", label: "🗺️ Ontology", desc: "Concept store" },
];

export default function PipelinePage() {
  const [activeTab, setActiveTab] = useState("process");
  const [pendingCount, setPendingCount] = useState(0);

  useEffect(() => {
    const check = async () => {
      try {
        const data = await apiFetch<PendingReview[]>("/pipeline/review/pending");
        setPendingCount(data.length);
      } catch { setPendingCount(0); }
    };
    check();
    const id = setInterval(check, 10000);
    return () => clearInterval(id);
  }, []);

  return (
    <div className="min-h-screen bg-[#0d0f14] text-slate-100">
      <div className="max-w-5xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-2">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-700 to-indigo-900 flex items-center justify-center text-xl">
              ⚙️
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white tracking-tight">Input Pipeline</h1>
              <p className="text-sm text-slate-400">9-stage processing · filter · extract · mask · route · classify · aggregate · review</p>
            </div>
          </div>
        </div>

        {/* Stage overview strip */}
        <div className="grid grid-cols-9 gap-1 mb-6">
          {STAGES.map((stage) => (
            <div key={stage.key} className="flex flex-col items-center bg-slate-900 rounded-lg p-2 border border-slate-800">
              <span className="text-lg mb-0.5">{stage.icon}</span>
              <span className="text-[10px] text-slate-500 text-center leading-tight">{stage.label}</span>
            </div>
          ))}
        </div>

        {/* Tabs */}
        <div className="flex gap-1 bg-slate-900/80 p-1 rounded-xl border border-slate-800 mb-6">
          {TABS.map((tab) => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key)}
              className={`relative flex-1 py-2 px-3 rounded-lg text-xs font-medium transition-all ${
                activeTab === tab.key
                  ? "bg-slate-700 text-white shadow-sm"
                  : "text-slate-500 hover:text-slate-300 hover:bg-slate-800/50"
              }`}
            >
              {tab.label}
              {tab.key === "review" && pendingCount > 0 && (
                <span className="absolute -top-1 -right-1 w-4 h-4 bg-amber-500 rounded-full text-[10px] font-bold text-black flex items-center justify-center">
                  {pendingCount}
                </span>
              )}
            </button>
          ))}
        </div>

        {/* Tab content */}
        <div className="bg-slate-900/60 rounded-2xl border border-slate-800 p-6">
          {activeTab === "process" && <ProcessTab />}
          {activeTab === "runs" && <RunsTab />}
          {activeTab === "review" && <ReviewTab />}
          {activeTab === "memory" && <MemoryTab />}
          {activeTab === "ontology" && <OntologyTab />}
        </div>
      </div>
    </div>
  );
}

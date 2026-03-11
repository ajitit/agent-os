"use client";

import { useState, useEffect, useCallback } from "react";

// ── Types ─────────────────────────────────────────────────────────────────────

interface SkillEntry {
  id: string;
  name: string;
  description: string;
  category: string;
  author: string;
  version: string;
  tags: string[];
  status: string;
  installs: number;
  readme?: string;
  configSchema?: Record<string, unknown>;
  createdAt: string;
}

interface ModelEntry {
  id: string;
  name: string;
  provider: string;
  type: string;
  contextWindow: number;
  description: string;
  tags: string[];
  status: string;
  installs: number;
}

interface ToolEntry {
  id: string;
  name: string;
  category: string;
  description: string;
  author: string;
  version: string;
  tags: string[];
  status: string;
  installs: number;
}

type Tab = "skills" | "models" | "tools";

// ── Constants ────────────────────────────────────────────────────────────────

const API = "/api/v1/marketplace";

const PROVIDER_COLORS: Record<string, string> = {
  OpenAI: "bg-emerald-900/50 text-emerald-300 border-emerald-800/50",
  Anthropic: "bg-orange-900/50 text-orange-300 border-orange-800/50",
  Meta: "bg-blue-900/50 text-blue-300 border-blue-800/50",
  AgentOS: "bg-violet-900/50 text-violet-300 border-violet-800/50",
};

const TYPE_ICONS: Record<string, string> = {
  chat: "💬",
  embedding: "🔢",
  image: "🖼️",
  audio: "🎵",
  vision: "👁️",
};

const CATEGORY_ICONS: Record<string, string> = {
  search: "🔍",
  code: "💻",
  files: "📁",
  communication: "📧",
  database: "🗄️",
  media: "🎨",
  productivity: "📅",
  research: "🔬",
  analysis: "📊",
  writing: "✍️",
  default: "🔧",
};

// ── Helpers ──────────────────────────────────────────────────────────────────

function getToken(): string {
  return typeof window !== "undefined" ? localStorage.getItem("agentos_token") ?? "" : "";
}

async function apiFetch<T>(url: string, opts?: RequestInit): Promise<T> {
  const res = await fetch(url, {
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${getToken()}`,
      ...(opts?.headers ?? {}),
    },
    ...opts,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error((err as { detail?: string }).detail ?? `HTTP ${res.status}`);
  }
  const json = await res.json();
  return ((json as { data?: T }).data ?? json) as T;
}

// ── Sub-components ────────────────────────────────────────────────────────────

function TagPill({ tag }: { tag: string }) {
  return (
    <span className="text-xs bg-slate-800 text-slate-400 px-2 py-0.5 rounded-full border border-slate-700">
      {tag}
    </span>
  );
}

function InstallButton({
  id,
  type,
  onInstalled,
}: {
  id: string;
  type: Tab;
  onInstalled: () => void;
}) {
  const [loading, setLoading] = useState(false);
  const [done, setDone] = useState(false);

  const handleInstall = async () => {
    setLoading(true);
    try {
      await apiFetch(`${API}/${type}/${id}/install`, { method: "POST" });
      setDone(true);
      onInstalled();
    } catch {
      // silently ignore
    } finally {
      setLoading(false);
    }
  };

  return (
    <button
      onClick={handleInstall}
      disabled={loading || done}
      className={`px-3 py-1.5 text-xs font-semibold rounded-lg transition-all ${
        done
          ? "bg-emerald-900/50 text-emerald-400 border border-emerald-800"
          : "bg-violet-800 hover:bg-violet-700 text-white disabled:opacity-40"
      }`}
    >
      {loading ? "…" : done ? "✓ Installed" : "Install"}
    </button>
  );
}

function DetailDrawer({
  item,
  type,
  onClose,
  onInstalled,
}: {
  item: SkillEntry | ModelEntry | ToolEntry;
  type: Tab;
  onClose: () => void;
  onInstalled: () => void;
}) {
  const isModel = type === "models";
  const isSkill = type === "skills";
  const model = item as ModelEntry;
  const skill = item as SkillEntry;

  return (
    <div className="fixed inset-0 bg-black/60 flex items-end sm:items-center justify-center z-50" onClick={onClose}>
      <div
        className="bg-[#161b27] border border-slate-700 rounded-2xl w-full max-w-2xl max-h-[80vh] overflow-y-auto mx-4 mb-4 sm:mb-0"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="p-6">
          {/* Header */}
          <div className="flex items-start justify-between gap-4 mb-4">
            <div>
              <div className="flex items-center gap-2 mb-1">
                <span className="text-2xl">
                  {isModel
                    ? TYPE_ICONS[model.type] ?? "🤖"
                    : CATEGORY_ICONS[(item as ToolEntry).category] ?? "🔧"}
                </span>
                <h2 className="text-xl font-bold text-white">{item.name}</h2>
              </div>
              {isModel && (
                <span className={`text-xs px-2 py-0.5 rounded-full border ${PROVIDER_COLORS[model.provider] ?? "bg-slate-800 text-slate-300 border-slate-700"}`}>
                  {model.provider}
                </span>
              )}
            </div>
            <button onClick={onClose} className="text-slate-500 hover:text-slate-300 text-xl font-bold">×</button>
          </div>

          <p className="text-slate-300 text-sm mb-4">{item.description}</p>

          {/* Metadata */}
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 mb-4 text-xs">
            {isModel && (
              <>
                <div className="bg-slate-800/60 rounded-lg p-2.5">
                  <div className="text-slate-500">Type</div>
                  <div className="text-white mt-0.5 font-medium capitalize">{model.type}</div>
                </div>
                <div className="bg-slate-800/60 rounded-lg p-2.5">
                  <div className="text-slate-500">Context Window</div>
                  <div className="text-white mt-0.5 font-medium">{model.contextWindow.toLocaleString()} tokens</div>
                </div>
              </>
            )}
            {!isModel && (
              <div className="bg-slate-800/60 rounded-lg p-2.5">
                <div className="text-slate-500">Version</div>
                <div className="text-white mt-0.5 font-medium">{(item as SkillEntry).version}</div>
              </div>
            )}
            <div className="bg-slate-800/60 rounded-lg p-2.5">
              <div className="text-slate-500">Installs</div>
              <div className="text-white mt-0.5 font-medium">{item.installs.toLocaleString()}</div>
            </div>
            <div className="bg-slate-800/60 rounded-lg p-2.5">
              <div className="text-slate-500">Status</div>
              <div className={`mt-0.5 font-medium capitalize ${item.status === "active" ? "text-emerald-400" : "text-slate-400"}`}>{item.status}</div>
            </div>
          </div>

          {/* Tags */}
          {item.tags?.length > 0 && (
            <div className="flex flex-wrap gap-1.5 mb-4">
              {item.tags.map((t) => <TagPill key={t} tag={t} />)}
            </div>
          )}

          {/* README */}
          {isSkill && skill.readme && (
            <div className="bg-slate-900 rounded-lg p-3 text-xs text-slate-300 border border-slate-800 mb-4 max-h-40 overflow-y-auto">
              <pre className="whitespace-pre-wrap font-mono">{skill.readme}</pre>
            </div>
          )}

          {/* Install */}
          <div className="flex justify-end">
            <InstallButton id={item.id} type={type} onInstalled={onInstalled} />
          </div>
        </div>
      </div>
    </div>
  );
}

// ── Skill card ────────────────────────────────────────────────────────────────

function SkillCard({
  skill,
  onView,
  onInstalled,
}: {
  skill: SkillEntry;
  onView: () => void;
  onInstalled: () => void;
}) {
  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900/60 hover:border-slate-600 transition-all p-5 flex flex-col gap-3">
      <div className="flex items-start justify-between gap-2">
        <div className="flex items-center gap-2">
          <span className="text-xl">{CATEGORY_ICONS[skill.category] ?? "🔧"}</span>
          <div>
            <div className="text-sm font-bold text-white">{skill.name}</div>
            <div className="text-xs text-slate-500">by {skill.author || "Unknown"} · v{skill.version}</div>
          </div>
        </div>
        <span className={`text-xs px-1.5 py-0.5 rounded border ${skill.status === "active" ? "bg-emerald-950/40 text-emerald-400 border-emerald-900" : "bg-slate-800 text-slate-500 border-slate-700"}`}>
          {skill.status}
        </span>
      </div>
      <p className="text-xs text-slate-400 leading-relaxed line-clamp-2">{skill.description}</p>
      <div className="flex flex-wrap gap-1">
        {skill.tags.slice(0, 3).map((t) => <TagPill key={t} tag={t} />)}
      </div>
      <div className="flex items-center justify-between mt-auto pt-2 border-t border-slate-800">
        <span className="text-xs text-slate-600">↓ {skill.installs.toLocaleString()}</span>
        <div className="flex gap-2">
          <button onClick={onView} className="px-3 py-1.5 text-xs text-slate-400 hover:text-white border border-slate-700 rounded-lg transition-colors">
            View
          </button>
          <InstallButton id={skill.id} type="skills" onInstalled={onInstalled} />
        </div>
      </div>
    </div>
  );
}

// ── Model card ────────────────────────────────────────────────────────────────

function ModelCard({
  model,
  onView,
  onInstalled,
}: {
  model: ModelEntry;
  onView: () => void;
  onInstalled: () => void;
}) {
  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900/60 hover:border-slate-600 transition-all p-5 flex flex-col gap-3">
      <div className="flex items-start justify-between gap-2">
        <div className="flex items-center gap-2">
          <span className="text-xl">{TYPE_ICONS[model.type] ?? "🤖"}</span>
          <div>
            <div className="text-sm font-bold text-white">{model.name}</div>
            <span className={`text-xs px-1.5 py-0.5 rounded border ${PROVIDER_COLORS[model.provider] ?? "bg-slate-800 text-slate-400 border-slate-700"}`}>
              {model.provider}
            </span>
          </div>
        </div>
        <div className="text-right">
          <div className="text-xs text-slate-500 capitalize">{model.type}</div>
          <div className="text-xs text-slate-600">{(model.contextWindow / 1000).toFixed(0)}K ctx</div>
        </div>
      </div>
      <p className="text-xs text-slate-400 leading-relaxed line-clamp-2">{model.description}</p>
      <div className="flex flex-wrap gap-1">
        {model.tags.slice(0, 3).map((t) => <TagPill key={t} tag={t} />)}
      </div>
      <div className="flex items-center justify-between mt-auto pt-2 border-t border-slate-800">
        <span className="text-xs text-slate-600">↓ {model.installs.toLocaleString()}</span>
        <div className="flex gap-2">
          <button onClick={onView} className="px-3 py-1.5 text-xs text-slate-400 hover:text-white border border-slate-700 rounded-lg transition-colors">
            View
          </button>
          <InstallButton id={model.id} type="models" onInstalled={onInstalled} />
        </div>
      </div>
    </div>
  );
}

// ── Tool card ─────────────────────────────────────────────────────────────────

function ToolCard({
  tool,
  onView,
  onInstalled,
}: {
  tool: ToolEntry;
  onView: () => void;
  onInstalled: () => void;
}) {
  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900/60 hover:border-slate-600 transition-all p-5 flex flex-col gap-3">
      <div className="flex items-start justify-between gap-2">
        <div className="flex items-center gap-2">
          <span className="text-xl">{CATEGORY_ICONS[tool.category] ?? "🔧"}</span>
          <div>
            <div className="text-sm font-bold text-white font-mono">{tool.name}</div>
            <div className="text-xs text-slate-500 capitalize">{tool.category} · v{tool.version}</div>
          </div>
        </div>
        <span className={`text-xs px-1.5 py-0.5 rounded border ${tool.status === "active" ? "bg-emerald-950/40 text-emerald-400 border-emerald-900" : "bg-slate-800 text-slate-500 border-slate-700"}`}>
          {tool.status}
        </span>
      </div>
      <p className="text-xs text-slate-400 leading-relaxed line-clamp-2">{tool.description}</p>
      <div className="flex flex-wrap gap-1">
        {tool.tags.slice(0, 3).map((t) => <TagPill key={t} tag={t} />)}
      </div>
      <div className="flex items-center justify-between mt-auto pt-2 border-t border-slate-800">
        <span className="text-xs text-slate-600">↓ {tool.installs.toLocaleString()}</span>
        <div className="flex gap-2">
          <button onClick={onView} className="px-3 py-1.5 text-xs text-slate-400 hover:text-white border border-slate-700 rounded-lg transition-colors">
            View
          </button>
          <InstallButton id={tool.id} type="tools" onInstalled={onInstalled} />
        </div>
      </div>
    </div>
  );
}

// ── Main page ─────────────────────────────────────────────────────────────────

export default function MarketplacePage() {
  const [tab, setTab] = useState<Tab>("models");
  const [skills, setSkills] = useState<SkillEntry[]>([]);
  const [models, setModels] = useState<ModelEntry[]>([]);
  const [tools, setTools] = useState<ToolEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [categoryFilter, setCategoryFilter] = useState("");
  const [detail, setDetail] = useState<SkillEntry | ModelEntry | ToolEntry | null>(null);

  const loadAll = useCallback(async () => {
    setLoading(true);
    try {
      const [sk, md, tl] = await Promise.all([
        apiFetch<SkillEntry[]>(`${API}/skills`),
        apiFetch<ModelEntry[]>(`${API}/models`),
        apiFetch<ToolEntry[]>(`${API}/tools`),
      ]);
      setSkills(sk);
      setModels(md);
      setTools(tl);
    } catch {
      // silently ignore
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { loadAll(); }, [loadAll]);

  const filterItems = <T extends { name: string; description: string; tags: string[]; category?: string; type?: string }>(
    items: T[]
  ): T[] => {
    let result = items;
    if (search) {
      const q = search.toLowerCase();
      result = result.filter(
        (i) =>
          i.name.toLowerCase().includes(q) ||
          i.description.toLowerCase().includes(q) ||
          i.tags.some((t) => t.toLowerCase().includes(q))
      );
    }
    if (categoryFilter) {
      result = result.filter(
        (i) => (i.category ?? i.type ?? "") === categoryFilter
      );
    }
    return result;
  };

  const filteredSkills = filterItems(skills);
  const filteredModels = filterItems(models);
  const filteredTools = filterItems(tools);

  const categories: string[] =
    tab === "skills"
      ? [...new Set(skills.map((s) => s.category))]
      : tab === "models"
      ? [...new Set(models.map((m) => m.type))]
      : [...new Set(tools.map((t) => t.category))];

  const TAB_CONFIG: { id: Tab; label: string; count: number; icon: string }[] = [
    { id: "models", label: "Models", count: models.length, icon: "🤖" },
    { id: "skills", label: "Skills", count: skills.length, icon: "🧠" },
    { id: "tools", label: "Tools", count: tools.length, icon: "🔧" },
  ];

  return (
    <div className="min-h-screen bg-[#0d0f14] text-slate-100">
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="flex items-center gap-3 mb-8">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-700 to-violet-900 flex items-center justify-center text-xl">🛒</div>
          <div>
            <h1 className="text-2xl font-bold text-white tracking-tight">Marketplace</h1>
            <p className="text-sm text-slate-400">Browse and install Skills, Models, and Tools</p>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex gap-1 mb-6 bg-slate-900/60 rounded-xl p-1 border border-slate-800 w-fit">
          {TAB_CONFIG.map(({ id, label, count, icon }) => (
            <button
              key={id}
              onClick={() => { setTab(id); setCategoryFilter(""); setSearch(""); }}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                tab === id
                  ? "bg-violet-800 text-white shadow"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              <span>{icon}</span>
              <span>{label}</span>
              <span className={`text-xs px-1.5 py-0.5 rounded-full ${tab === id ? "bg-violet-600 text-violet-100" : "bg-slate-800 text-slate-500"}`}>
                {count}
              </span>
            </button>
          ))}
        </div>

        {/* Search + filter */}
        <div className="flex flex-wrap gap-2 mb-6">
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search…"
            className="bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-violet-500 placeholder-slate-600 w-48"
          />
          <select
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
            className="bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-300 focus:outline-none focus:border-violet-500"
          >
            <option value="">All {tab === "models" ? "types" : "categories"}</option>
            {categories.map((c) => (
              <option key={c} value={c}>{c}</option>
            ))}
          </select>
          {(search || categoryFilter) && (
            <button
              onClick={() => { setSearch(""); setCategoryFilter(""); }}
              className="px-3 py-2 bg-slate-800 text-slate-400 text-xs rounded-lg border border-slate-700 hover:text-white"
            >
              ✕ Clear
            </button>
          )}
          <div className="ml-auto text-xs text-slate-600 self-center">
            {loading ? "Loading…" : `${(tab === "skills" ? filteredSkills : tab === "models" ? filteredModels : filteredTools).length} items`}
          </div>
        </div>

        {/* Grid */}
        {loading ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {Array.from({ length: 6 }).map((_, i) => (
              <div key={i} className="h-52 rounded-2xl bg-slate-900/40 border border-slate-800 animate-pulse" />
            ))}
          </div>
        ) : (
          <>
            {tab === "models" && (
              filteredModels.length === 0 ? (
                <EmptyState tab={tab} />
              ) : (
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                  {filteredModels.map((m) => (
                    <ModelCard key={m.id} model={m} onView={() => setDetail(m)} onInstalled={loadAll} />
                  ))}
                </div>
              )
            )}
            {tab === "skills" && (
              filteredSkills.length === 0 ? (
                <EmptyState tab={tab} />
              ) : (
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                  {filteredSkills.map((s) => (
                    <SkillCard key={s.id} skill={s} onView={() => setDetail(s)} onInstalled={loadAll} />
                  ))}
                </div>
              )
            )}
            {tab === "tools" && (
              filteredTools.length === 0 ? (
                <EmptyState tab={tab} />
              ) : (
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                  {filteredTools.map((t) => (
                    <ToolCard key={t.id} tool={t} onView={() => setDetail(t)} onInstalled={loadAll} />
                  ))}
                </div>
              )
            )}
          </>
        )}
      </div>

      {/* Detail drawer */}
      {detail && (
        <DetailDrawer
          item={detail}
          type={tab}
          onClose={() => setDetail(null)}
          onInstalled={loadAll}
        />
      )}
    </div>
  );
}

function EmptyState({ tab }: { tab: Tab }) {
  return (
    <div className="flex flex-col items-center justify-center py-20 text-center">
      <span className="text-5xl mb-4">{tab === "models" ? "🤖" : tab === "skills" ? "🧠" : "🔧"}</span>
      <p className="text-slate-400">No {tab} found.</p>
      <p className="text-slate-600 text-sm mt-1">Try clearing your search filters.</p>
    </div>
  );
}

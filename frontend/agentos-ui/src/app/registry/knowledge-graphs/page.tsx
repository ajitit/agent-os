"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";

type KG = {
  id: string;
  name: string;
  description?: string;
  category?: string;
  endpointUrl: string;
  authType: string;
  status: string;
  tags: string[];
};

type KGGroup = {
  id: string;
  name: string;
  description?: string;
  members: string[];
};

const STATUS_COLORS: Record<string, string> = {
  active: "bg-emerald-900/40 text-emerald-300 border border-emerald-700/40",
  inactive: "bg-amber-900/40 text-amber-300 border border-amber-700/40",
  draft: "bg-zinc-800 text-zinc-400 border border-zinc-700",
};

export default function KnowledgeGraphRegistryPage() {
  const [kgs, setKgs] = useState<KG[]>([]);
  const [groups, setGroups] = useState<KGGroup[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editKg, setEditKg] = useState<KG | null>(null);
  const [showGroupModal, setShowGroupModal] = useState(false);
  const [deleteId, setDeleteId] = useState<string | null>(null);
  const [search, setSearch] = useState("");
  const [form, setForm] = useState({ name: "", description: "", category: "", endpointUrl: "", authType: "none", status: "active", tags: "" });
  const [groupForm, setGroupForm] = useState({ name: "", description: "" });
  const [error, setError] = useState("");

  const load = async () => {
    try {
      const [k, g] = await Promise.all([
        api.get<{ data: KG[] }>("/registry/knowledge-graphs"),
        api.get<{ data: KGGroup[] }>("/registry/knowledge-graphs/groups"),
      ]);
      setKgs(k.data);
      setGroups(g.data);
    } catch { /* ignore */ } finally { setLoading(false); }
  };

  useEffect(() => { load(); }, []);

  const openCreate = () => {
    setEditKg(null);
    setForm({ name: "", description: "", category: "", endpointUrl: "", authType: "none", status: "active", tags: "" });
    setError(""); setShowModal(true);
  };

  const openEdit = (k: KG) => {
    setEditKg(k);
    setForm({ name: k.name, description: k.description || "", category: k.category || "", endpointUrl: k.endpointUrl, authType: k.authType, status: k.status, tags: (k.tags || []).join(", ") });
    setError(""); setShowModal(true);
  };

  const saveKg = async () => {
    if (!form.name.trim() || !form.endpointUrl.trim()) { setError("Name and endpoint URL are required."); return; }
    const body = { ...form, tags: form.tags.split(",").map(t => t.trim()).filter(Boolean) };
    try {
      if (editKg) { await api.put(`/registry/knowledge-graphs/${editKg.id}`, body); }
      else { await api.post("/registry/knowledge-graphs", body); }
      setShowModal(false); load();
    } catch (e: unknown) { setError(e instanceof Error ? e.message : "Failed to save."); }
  };

  const deleteKg = async (id: string) => {
    try { await api.delete(`/registry/knowledge-graphs/${id}`); setDeleteId(null); load(); } catch { /* ignore */ }
  };

  const saveGroup = async () => {
    if (!groupForm.name.trim()) return;
    try { await api.post("/registry/knowledge-graphs/groups", groupForm); setShowGroupModal(false); setGroupForm({ name: "", description: "" }); load(); } catch { /* ignore */ }
  };

  const deleteGroup = async (id: string) => {
    try { await api.delete(`/registry/knowledge-graphs/groups/${id}`); load(); } catch { /* ignore */ }
  };

  const filtered = kgs.filter(k =>
    k.name.toLowerCase().includes(search.toLowerCase()) ||
    (k.category || "").toLowerCase().includes(search.toLowerCase()) ||
    (k.description || "").toLowerCase().includes(search.toLowerCase()) ||
    k.endpointUrl.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100">
      <div className="mx-auto max-w-7xl px-6 py-8">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-2xl font-bold text-white">Knowledge Graph Registry</h1>
            <p className="text-zinc-500 text-sm mt-1">Manage remote knowledge graphs and assign to agents</p>
          </div>
          <button onClick={openCreate} className="bg-violet-600 hover:bg-violet-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors">+ New Knowledge Graph</button>
        </div>

        <div className="flex gap-6">
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-3 mb-4">
              <input value={search} onChange={e => setSearch(e.target.value)} placeholder="Search knowledge graphs..." className="flex-1 bg-zinc-900 border border-zinc-800 rounded-lg px-3 py-2 text-sm text-zinc-100 placeholder-zinc-600 focus:outline-none focus:border-zinc-600" />
              <span className="text-zinc-500 text-sm">{filtered.length} knowledge graphs</span>
            </div>
            {loading ? (
              <div className="text-zinc-500 text-sm py-8 text-center">Loading...</div>
            ) : (
              <div className="rounded-xl border border-zinc-800 overflow-hidden">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-zinc-800 bg-zinc-900/50">
                      <th className="text-left px-4 py-3 text-zinc-400 font-medium">Name</th>
                      <th className="text-left px-4 py-3 text-zinc-400 font-medium">Category</th>
                      <th className="text-left px-4 py-3 text-zinc-400 font-medium">Endpoint URL</th>
                      <th className="text-left px-4 py-3 text-zinc-400 font-medium">Auth</th>
                      <th className="text-left px-4 py-3 text-zinc-400 font-medium">Status</th>
                      <th className="px-4 py-3"></th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-zinc-800/50">
                    {filtered.length === 0 && <tr><td colSpan={6} className="px-4 py-8 text-center text-zinc-600">No knowledge graphs found</td></tr>}
                    {filtered.map(k => (
                      <tr key={k.id} className="hover:bg-zinc-900/50 transition-colors">
                        <td className="px-4 py-3">
                          <div className="font-medium text-zinc-100">{k.name}</div>
                          {k.description && <div className="text-zinc-500 text-xs mt-0.5 truncate max-w-xs">{k.description}</div>}
                        </td>
                        <td className="px-4 py-3 text-zinc-400">{k.category || "—"}</td>
                        <td className="px-4 py-3 text-zinc-500 font-mono text-xs truncate max-w-[200px]">{k.endpointUrl}</td>
                        <td className="px-4 py-3 text-zinc-400">{k.authType}</td>
                        <td className="px-4 py-3">
                          <span className={`inline-flex rounded-full px-2 py-0.5 text-xs font-medium ${STATUS_COLORS[k.status] ?? STATUS_COLORS.draft}`}>{k.status}</span>
                        </td>
                        <td className="px-4 py-3">
                          <div className="flex items-center gap-2 justify-end">
                            <button onClick={() => openEdit(k)} className="text-zinc-500 hover:text-zinc-200 text-xs px-2 py-1 rounded hover:bg-zinc-800 transition-colors">Edit</button>
                            {deleteId === k.id ? (
                              <div className="flex items-center gap-1">
                                <button onClick={() => deleteKg(k.id)} className="text-red-400 hover:text-red-300 text-xs px-2 py-1 rounded hover:bg-red-900/20">Confirm</button>
                                <button onClick={() => setDeleteId(null)} className="text-zinc-500 text-xs px-2 py-1 rounded hover:bg-zinc-800">Cancel</button>
                              </div>
                            ) : (
                              <button onClick={() => setDeleteId(k.id)} className="text-zinc-600 hover:text-red-400 text-xs px-2 py-1 rounded hover:bg-zinc-800 transition-colors">Delete</button>
                            )}
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>

          <div className="w-64 shrink-0">
            <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-4">
              <div className="flex items-center justify-between mb-3">
                <h2 className="text-sm font-semibold text-zinc-200">Groups</h2>
                <button onClick={() => setShowGroupModal(true)} className="text-xs text-violet-400 hover:text-violet-300 transition-colors">+ New</button>
              </div>
              {groups.length === 0 && <p className="text-zinc-600 text-xs">No groups yet</p>}
              <div className="space-y-2">
                {groups.map(g => (
                  <div key={g.id} className="bg-zinc-800/50 rounded-lg p-3">
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-zinc-200 font-medium">{g.name}</span>
                      <button onClick={() => deleteGroup(g.id)} className="text-zinc-600 hover:text-red-400 text-xs transition-colors">×</button>
                    </div>
                    {g.description && <p className="text-zinc-500 text-xs mt-0.5">{g.description}</p>}
                    <div className="text-zinc-600 text-xs mt-1">{(g.members || []).length} members</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>

      {showModal && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-zinc-900 border border-zinc-800 rounded-2xl w-full max-w-lg shadow-2xl">
            <div className="flex items-center justify-between px-6 py-4 border-b border-zinc-800">
              <h2 className="text-base font-semibold text-white">{editKg ? "Edit Knowledge Graph" : "New Knowledge Graph"}</h2>
              <button onClick={() => setShowModal(false)} className="text-zinc-500 hover:text-zinc-300 text-xl leading-none">×</button>
            </div>
            <div className="p-6 space-y-4">
              {error && <div className="bg-red-900/20 border border-red-800/40 rounded-lg px-3 py-2 text-red-400 text-sm">{error}</div>}
              <div className="grid grid-cols-2 gap-4">
                <div className="col-span-2">
                  <label className="block text-xs text-zinc-400 mb-1.5">Name *</label>
                  <input value={form.name} onChange={e => setForm(f => ({ ...f, name: e.target.value }))} className="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-3 py-2 text-sm text-zinc-100 focus:outline-none focus:border-violet-500" placeholder="my-knowledge-graph" />
                </div>
                <div className="col-span-2">
                  <label className="block text-xs text-zinc-400 mb-1.5">Description</label>
                  <textarea value={form.description} onChange={e => setForm(f => ({ ...f, description: e.target.value }))} rows={2} className="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-3 py-2 text-sm text-zinc-100 focus:outline-none focus:border-violet-500 resize-none" placeholder="What does this knowledge graph contain?" />
                </div>
                <div>
                  <label className="block text-xs text-zinc-400 mb-1.5">Category</label>
                  <input value={form.category} onChange={e => setForm(f => ({ ...f, category: e.target.value }))} className="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-3 py-2 text-sm text-zinc-100 focus:outline-none focus:border-violet-500" placeholder="research" />
                </div>
                <div>
                  <label className="block text-xs text-zinc-400 mb-1.5">Status</label>
                  <select value={form.status} onChange={e => setForm(f => ({ ...f, status: e.target.value }))} className="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-3 py-2 text-sm text-zinc-100 focus:outline-none focus:border-violet-500">
                    <option value="active">Active</option>
                    <option value="inactive">Inactive</option>
                    <option value="draft">Draft</option>
                  </select>
                </div>
                <div className="col-span-2">
                  <label className="block text-xs text-zinc-400 mb-1.5">Endpoint URL *</label>
                  <input value={form.endpointUrl} onChange={e => setForm(f => ({ ...f, endpointUrl: e.target.value }))} className="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-3 py-2 text-sm text-zinc-100 focus:outline-none focus:border-violet-500" placeholder="https://api.example.com/kg" />
                </div>
                <div className="col-span-2">
                  <label className="block text-xs text-zinc-400 mb-1.5">Auth Type</label>
                  <select value={form.authType} onChange={e => setForm(f => ({ ...f, authType: e.target.value }))} className="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-3 py-2 text-sm text-zinc-100 focus:outline-none focus:border-violet-500">
                    <option value="none">None</option>
                    <option value="api_key">API Key</option>
                    <option value="oauth2">OAuth2</option>
                    <option value="basic">Basic</option>
                  </select>
                </div>
                <div className="col-span-2">
                  <label className="block text-xs text-zinc-400 mb-1.5">Tags (comma-separated)</label>
                  <input value={form.tags} onChange={e => setForm(f => ({ ...f, tags: e.target.value }))} className="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-3 py-2 text-sm text-zinc-100 focus:outline-none focus:border-violet-500" placeholder="graph, knowledge, semantic" />
                </div>
              </div>
            </div>
            <div className="flex justify-end gap-2 px-6 py-4 border-t border-zinc-800">
              <button onClick={() => setShowModal(false)} className="px-4 py-2 rounded-lg text-sm text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800 transition-colors">Cancel</button>
              <button onClick={saveKg} className="px-4 py-2 rounded-lg text-sm bg-violet-600 hover:bg-violet-700 text-white font-medium transition-colors">{editKg ? "Save Changes" : "Create Knowledge Graph"}</button>
            </div>
          </div>
        </div>
      )}

      {showGroupModal && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-zinc-900 border border-zinc-800 rounded-2xl w-full max-w-md shadow-2xl">
            <div className="flex items-center justify-between px-6 py-4 border-b border-zinc-800">
              <h2 className="text-base font-semibold text-white">New Knowledge Graph Group</h2>
              <button onClick={() => setShowGroupModal(false)} className="text-zinc-500 hover:text-zinc-300 text-xl leading-none">×</button>
            </div>
            <div className="p-6 space-y-4">
              <div>
                <label className="block text-xs text-zinc-400 mb-1.5">Group Name *</label>
                <input value={groupForm.name} onChange={e => setGroupForm(f => ({ ...f, name: e.target.value }))} className="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-3 py-2 text-sm text-zinc-100 focus:outline-none focus:border-violet-500" placeholder="Core Knowledge Graphs" />
              </div>
              <div>
                <label className="block text-xs text-zinc-400 mb-1.5">Description</label>
                <textarea value={groupForm.description} onChange={e => setGroupForm(f => ({ ...f, description: e.target.value }))} rows={2} className="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-3 py-2 text-sm text-zinc-100 focus:outline-none focus:border-violet-500 resize-none" />
              </div>
            </div>
            <div className="flex justify-end gap-2 px-6 py-4 border-t border-zinc-800">
              <button onClick={() => setShowGroupModal(false)} className="px-4 py-2 rounded-lg text-sm text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800 transition-colors">Cancel</button>
              <button onClick={saveGroup} className="px-4 py-2 rounded-lg text-sm bg-violet-600 hover:bg-violet-700 text-white font-medium transition-colors">Create Group</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

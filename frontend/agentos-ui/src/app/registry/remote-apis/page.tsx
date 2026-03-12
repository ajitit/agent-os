"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";

type RemoteAPI = {
  id: string;
  name: string;
  description?: string;
  category?: string;
  baseUrl?: string;
  apiType?: string;
  authType?: string;
  tags?: string[];
  status?: string;
  groupId?: string;
};

type Group = {
  id: string;
  name: string;
  description?: string;
};

const STATUS_COLORS: Record<string, string> = {
  active: "bg-emerald-900/40 text-emerald-300 border border-emerald-700/40",
  inactive: "bg-zinc-800 text-zinc-400 border border-zinc-700",
  deprecated: "bg-amber-900/40 text-amber-300 border border-amber-700/40",
};

const API_TYPES = ["rest", "graphql", "grpc", "soap"];
const AUTH_TYPES = ["none", "api_key", "oauth2", "basic", "bearer"];

const emptyForm = {
  name: "",
  description: "",
  category: "",
  baseUrl: "",
  apiType: "rest",
  authType: "none",
  tags: "",
  status: "active",
  groupId: "",
};

export default function RemoteAPIsPage() {
  const [apis, setApis] = useState<RemoteAPI[]>([]);
  const [groups, setGroups] = useState<Group[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editApi, setEditApi] = useState<RemoteAPI | null>(null);
  const [deleteId, setDeleteId] = useState<string | null>(null);
  const [search, setSearch] = useState("");
  const [selectedGroup, setSelectedGroup] = useState<string | null>(null);
  const [form, setForm] = useState({ ...emptyForm });
  const [error, setError] = useState("");
  const [showGroupModal, setShowGroupModal] = useState(false);
  const [groupForm, setGroupForm] = useState({ name: "", description: "" });
  const [groupError, setGroupError] = useState("");

  const load = async () => {
    try {
      const [apisRes, groupsRes] = await Promise.all([
        api.get<{ data: RemoteAPI[] }>("/registry/remote-apis"),
        api.get<{ data: Group[] }>("/registry/remote-apis/groups"),
      ]);
      setApis(apisRes.data);
      setGroups(groupsRes.data);
    } catch { /* ignore */ }
    finally { setLoading(false); }
  };

  useEffect(() => { load(); }, []);

  const openCreate = () => {
    setEditApi(null);
    setForm({ ...emptyForm, groupId: selectedGroup ?? "" });
    setError("");
    setShowModal(true);
  };

  const openEdit = (a: RemoteAPI) => {
    setEditApi(a);
    setForm({
      name: a.name,
      description: a.description || "",
      category: a.category || "",
      baseUrl: a.baseUrl || "",
      apiType: a.apiType || "rest",
      authType: a.authType || "none",
      tags: (a.tags || []).join(", "),
      status: a.status || "active",
      groupId: a.groupId || "",
    });
    setError("");
    setShowModal(true);
  };

  const save = async () => {
    if (!form.name.trim()) { setError("Name is required."); return; }
    if (!form.baseUrl.trim()) { setError("Base URL is required."); return; }
    const payload = {
      ...form,
      tags: form.tags.split(",").map(t => t.trim()).filter(Boolean),
    };
    try {
      if (editApi) {
        await api.put(`/registry/remote-apis/${editApi.id}`, payload);
      } else {
        await api.post("/registry/remote-apis", payload);
      }
      setShowModal(false);
      load();
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : "Failed to save.";
      setError(msg);
    }
  };

  const deleteApi = async (id: string) => {
    try { await api.delete(`/registry/remote-apis/${id}`); setDeleteId(null); load(); } catch { /* ignore */ }
  };

  const saveGroup = async () => {
    if (!groupForm.name.trim()) { setGroupError("Group name is required."); return; }
    try {
      await api.post("/registry/remote-apis/groups", groupForm);
      setShowGroupModal(false);
      setGroupForm({ name: "", description: "" });
      load();
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : "Failed to save group.";
      setGroupError(msg);
    }
  };

  const deleteGroup = async (id: string) => {
    try { await api.delete(`/registry/remote-apis/groups/${id}`); load(); } catch { /* ignore */ }
  };

  const filtered = apis.filter(a => {
    const matchesGroup = selectedGroup === null || a.groupId === selectedGroup;
    const matchesSearch =
      a.name.toLowerCase().includes(search.toLowerCase()) ||
      (a.baseUrl || "").toLowerCase().includes(search.toLowerCase()) ||
      (a.category || "").toLowerCase().includes(search.toLowerCase());
    return matchesGroup && matchesSearch;
  });

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100">
      <div className="mx-auto max-w-7xl px-6 py-8">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-2xl font-bold text-white">Remote API Registry</h1>
            <p className="text-zinc-500 text-sm mt-1">Manage external API integrations and endpoints</p>
          </div>
          <button
            onClick={openCreate}
            className="bg-violet-600 hover:bg-violet-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
          >
            + New API
          </button>
        </div>

        <div className="flex gap-6">
          {/* Groups sidebar */}
          <div className="w-52 shrink-0">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-medium text-zinc-500 uppercase tracking-wider">Groups</span>
              <button
                onClick={() => { setGroupForm({ name: "", description: "" }); setGroupError(""); setShowGroupModal(true); }}
                className="text-zinc-600 hover:text-zinc-300 text-lg leading-none transition-colors"
                title="Add group"
              >
                +
              </button>
            </div>
            <div className="space-y-0.5">
              <button
                onClick={() => setSelectedGroup(null)}
                className={`w-full text-left px-3 py-2 rounded-lg text-sm transition-colors ${
                  selectedGroup === null
                    ? "bg-zinc-800 text-zinc-100 font-medium"
                    : "text-zinc-400 hover:bg-zinc-900 hover:text-zinc-200"
                }`}
              >
                All APIs
                <span className="float-right text-zinc-600 text-xs">{apis.length}</span>
              </button>
              {groups.map(g => (
                <div key={g.id} className="group/item relative">
                  <button
                    onClick={() => setSelectedGroup(g.id)}
                    className={`w-full text-left px-3 py-2 rounded-lg text-sm transition-colors pr-8 ${
                      selectedGroup === g.id
                        ? "bg-zinc-800 text-zinc-100 font-medium"
                        : "text-zinc-400 hover:bg-zinc-900 hover:text-zinc-200"
                    }`}
                  >
                    {g.name}
                    <span className="float-right text-zinc-600 text-xs">
                      {apis.filter(a => a.groupId === g.id).length}
                    </span>
                  </button>
                  <button
                    onClick={() => deleteGroup(g.id)}
                    className="absolute right-2 top-1/2 -translate-y-1/2 opacity-0 group-hover/item:opacity-100 text-zinc-600 hover:text-red-400 text-xs transition-all"
                    title="Delete group"
                  >
                    ×
                  </button>
                </div>
              ))}
            </div>
          </div>

          {/* Main content */}
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-3 mb-4">
              <input
                value={search}
                onChange={e => setSearch(e.target.value)}
                placeholder="Search APIs..."
                className="flex-1 bg-zinc-900 border border-zinc-800 rounded-lg px-3 py-2 text-sm text-zinc-100 placeholder-zinc-600 focus:outline-none focus:border-zinc-600"
              />
              <span className="text-zinc-500 text-sm">{filtered.length} APIs</span>
            </div>

            {loading ? (
              <div className="text-zinc-500 text-sm py-8 text-center">Loading...</div>
            ) : (
              <div className="rounded-xl border border-zinc-800 overflow-hidden">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-zinc-800 bg-zinc-900/50">
                      <th className="text-left px-4 py-3 text-zinc-400 font-medium">Name</th>
                      <th className="text-left px-4 py-3 text-zinc-400 font-medium">Base URL</th>
                      <th className="text-left px-4 py-3 text-zinc-400 font-medium">Type</th>
                      <th className="text-left px-4 py-3 text-zinc-400 font-medium">Auth</th>
                      <th className="text-left px-4 py-3 text-zinc-400 font-medium">Status</th>
                      <th className="px-4 py-3"></th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-zinc-800/50">
                    {filtered.length === 0 && (
                      <tr>
                        <td colSpan={6} className="px-4 py-8 text-center text-zinc-600">
                          No APIs found. Add your first remote API.
                        </td>
                      </tr>
                    )}
                    {filtered.map(a => (
                      <tr key={a.id} className="hover:bg-zinc-900/50 transition-colors">
                        <td className="px-4 py-3">
                          <div className="font-medium text-zinc-100">{a.name}</div>
                          {a.description && (
                            <div className="text-zinc-500 text-xs mt-0.5">{a.description}</div>
                          )}
                          {a.category && (
                            <div className="text-zinc-600 text-xs mt-0.5">{a.category}</div>
                          )}
                        </td>
                        <td className="px-4 py-3 text-zinc-400 font-mono text-xs max-w-[200px] truncate">
                          {a.baseUrl || "—"}
                        </td>
                        <td className="px-4 py-3">
                          <span className="text-zinc-400 text-xs uppercase font-mono">
                            {a.apiType || "—"}
                          </span>
                        </td>
                        <td className="px-4 py-3">
                          <span className="text-zinc-500 text-xs">
                            {a.authType || "none"}
                          </span>
                        </td>
                        <td className="px-4 py-3">
                          <span className={`inline-flex rounded-full px-2 py-0.5 text-xs font-medium ${STATUS_COLORS[a.status ?? "active"] ?? STATUS_COLORS.active}`}>
                            {a.status ?? "active"}
                          </span>
                        </td>
                        <td className="px-4 py-3">
                          <div className="flex items-center gap-2 justify-end">
                            <button
                              onClick={() => openEdit(a)}
                              className="text-zinc-500 hover:text-zinc-200 text-xs px-2 py-1 rounded hover:bg-zinc-800 transition-colors"
                            >
                              Edit
                            </button>
                            {deleteId === a.id ? (
                              <div className="flex items-center gap-1">
                                <button
                                  onClick={() => deleteApi(a.id)}
                                  className="text-red-400 hover:text-red-300 text-xs px-2 py-1 rounded hover:bg-red-900/20"
                                >
                                  Confirm
                                </button>
                                <button
                                  onClick={() => setDeleteId(null)}
                                  className="text-zinc-500 text-xs px-2 py-1 rounded hover:bg-zinc-800"
                                >
                                  Cancel
                                </button>
                              </div>
                            ) : (
                              <button
                                onClick={() => setDeleteId(a.id)}
                                className="text-zinc-600 hover:text-red-400 text-xs px-2 py-1 rounded hover:bg-zinc-800 transition-colors"
                              >
                                Delete
                              </button>
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
        </div>
      </div>

      {/* Create/Edit Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-zinc-900 border border-zinc-800 rounded-2xl w-full max-w-lg shadow-2xl max-h-[90vh] flex flex-col">
            <div className="flex items-center justify-between px-6 py-4 border-b border-zinc-800 shrink-0">
              <h2 className="text-base font-semibold text-white">
                {editApi ? "Edit Remote API" : "New Remote API"}
              </h2>
              <button
                onClick={() => setShowModal(false)}
                className="text-zinc-500 hover:text-zinc-300 text-xl leading-none"
              >
                ×
              </button>
            </div>
            <div className="p-6 space-y-4 overflow-y-auto">
              {error && (
                <div className="bg-red-900/20 border border-red-800/40 rounded-lg px-3 py-2 text-red-400 text-sm">
                  {error}
                </div>
              )}
              <div>
                <label className="block text-xs text-zinc-400 mb-1.5">Name *</label>
                <input
                  value={form.name}
                  onChange={e => setForm(f => ({ ...f, name: e.target.value }))}
                  className="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-3 py-2 text-sm text-zinc-100 focus:outline-none focus:border-violet-500"
                  placeholder="my-remote-api"
                />
              </div>
              <div>
                <label className="block text-xs text-zinc-400 mb-1.5">Base URL *</label>
                <input
                  value={form.baseUrl}
                  onChange={e => setForm(f => ({ ...f, baseUrl: e.target.value }))}
                  className="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-3 py-2 text-sm text-zinc-100 focus:outline-none focus:border-violet-500"
                  placeholder="https://api.example.com/v1"
                />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs text-zinc-400 mb-1.5">API Type</label>
                  <select
                    value={form.apiType}
                    onChange={e => setForm(f => ({ ...f, apiType: e.target.value }))}
                    className="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-3 py-2 text-sm text-zinc-100 focus:outline-none focus:border-violet-500"
                  >
                    {API_TYPES.map(t => (
                      <option key={t} value={t}>{t}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-xs text-zinc-400 mb-1.5">Auth Type</label>
                  <select
                    value={form.authType}
                    onChange={e => setForm(f => ({ ...f, authType: e.target.value }))}
                    className="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-3 py-2 text-sm text-zinc-100 focus:outline-none focus:border-violet-500"
                  >
                    {AUTH_TYPES.map(t => (
                      <option key={t} value={t}>{t}</option>
                    ))}
                  </select>
                </div>
              </div>
              <div>
                <label className="block text-xs text-zinc-400 mb-1.5">Category</label>
                <input
                  value={form.category}
                  onChange={e => setForm(f => ({ ...f, category: e.target.value }))}
                  className="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-3 py-2 text-sm text-zinc-100 focus:outline-none focus:border-violet-500"
                  placeholder="e.g. payment, analytics, communication"
                />
              </div>
              <div>
                <label className="block text-xs text-zinc-400 mb-1.5">Description</label>
                <textarea
                  value={form.description}
                  onChange={e => setForm(f => ({ ...f, description: e.target.value }))}
                  rows={2}
                  className="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-3 py-2 text-sm text-zinc-100 focus:outline-none focus:border-violet-500 resize-none"
                />
              </div>
              <div>
                <label className="block text-xs text-zinc-400 mb-1.5">Tags (comma-separated)</label>
                <input
                  value={form.tags}
                  onChange={e => setForm(f => ({ ...f, tags: e.target.value }))}
                  className="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-3 py-2 text-sm text-zinc-100 focus:outline-none focus:border-violet-500"
                  placeholder="payments, billing, stripe"
                />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs text-zinc-400 mb-1.5">Status</label>
                  <select
                    value={form.status}
                    onChange={e => setForm(f => ({ ...f, status: e.target.value }))}
                    className="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-3 py-2 text-sm text-zinc-100 focus:outline-none focus:border-violet-500"
                  >
                    <option value="active">Active</option>
                    <option value="inactive">Inactive</option>
                    <option value="deprecated">Deprecated</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs text-zinc-400 mb-1.5">Group</label>
                  <select
                    value={form.groupId}
                    onChange={e => setForm(f => ({ ...f, groupId: e.target.value }))}
                    className="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-3 py-2 text-sm text-zinc-100 focus:outline-none focus:border-violet-500"
                  >
                    <option value="">No group</option>
                    {groups.map(g => (
                      <option key={g.id} value={g.id}>{g.name}</option>
                    ))}
                  </select>
                </div>
              </div>
            </div>
            <div className="flex justify-end gap-2 px-6 py-4 border-t border-zinc-800 shrink-0">
              <button
                onClick={() => setShowModal(false)}
                className="px-4 py-2 rounded-lg text-sm text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={save}
                className="px-4 py-2 rounded-lg text-sm bg-violet-600 hover:bg-violet-700 text-white font-medium transition-colors"
              >
                {editApi ? "Save Changes" : "Create API"}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Create Group Modal */}
      {showGroupModal && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-zinc-900 border border-zinc-800 rounded-2xl w-full max-w-sm shadow-2xl">
            <div className="flex items-center justify-between px-6 py-4 border-b border-zinc-800">
              <h2 className="text-base font-semibold text-white">New Group</h2>
              <button
                onClick={() => setShowGroupModal(false)}
                className="text-zinc-500 hover:text-zinc-300 text-xl leading-none"
              >
                ×
              </button>
            </div>
            <div className="p-6 space-y-4">
              {groupError && (
                <div className="bg-red-900/20 border border-red-800/40 rounded-lg px-3 py-2 text-red-400 text-sm">
                  {groupError}
                </div>
              )}
              <div>
                <label className="block text-xs text-zinc-400 mb-1.5">Group Name *</label>
                <input
                  value={groupForm.name}
                  onChange={e => setGroupForm(f => ({ ...f, name: e.target.value }))}
                  className="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-3 py-2 text-sm text-zinc-100 focus:outline-none focus:border-violet-500"
                  placeholder="Internal APIs"
                />
              </div>
              <div>
                <label className="block text-xs text-zinc-400 mb-1.5">Description</label>
                <input
                  value={groupForm.description}
                  onChange={e => setGroupForm(f => ({ ...f, description: e.target.value }))}
                  className="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-3 py-2 text-sm text-zinc-100 focus:outline-none focus:border-violet-500"
                  placeholder="Optional description"
                />
              </div>
            </div>
            <div className="flex justify-end gap-2 px-6 py-4 border-t border-zinc-800">
              <button
                onClick={() => setShowGroupModal(false)}
                className="px-4 py-2 rounded-lg text-sm text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={saveGroup}
                className="px-4 py-2 rounded-lg text-sm bg-violet-600 hover:bg-violet-700 text-white font-medium transition-colors"
              >
                Create Group
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

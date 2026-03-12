"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";

type DataSource = {
  id: string;
  name: string;
  description?: string;
  type?: string;
  host?: string;
  port?: number;
  database?: string;
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
  maintenance: "bg-amber-900/40 text-amber-300 border border-amber-700/40",
};

const SOURCE_TYPES = [
  "postgresql",
  "mysql",
  "sqlite",
  "mongodb",
  "redis",
  "s3",
  "gcs",
  "azure_blob",
  "sftp",
  "nfs",
  "sharepoint",
  "local",
];

const TYPE_LABELS: Record<string, string> = {
  postgresql: "PostgreSQL",
  mysql: "MySQL",
  sqlite: "SQLite",
  mongodb: "MongoDB",
  redis: "Redis",
  s3: "S3",
  gcs: "GCS",
  azure_blob: "Azure Blob",
  sftp: "SFTP",
  nfs: "NFS",
  sharepoint: "SharePoint",
  local: "Local",
};

const emptyForm = {
  name: "",
  description: "",
  type: "postgresql",
  host: "",
  port: "",
  database: "",
  tags: "",
  status: "active",
  groupId: "",
};

export default function DataSourcesPage() {
  const [sources, setSources] = useState<DataSource[]>([]);
  const [groups, setGroups] = useState<Group[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editSource, setEditSource] = useState<DataSource | null>(null);
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
      const [sourcesRes, groupsRes] = await Promise.all([
        api.get<{ data: DataSource[] }>("/registry/data-sources"),
        api.get<{ data: Group[] }>("/registry/data-sources/groups"),
      ]);
      setSources(sourcesRes.data);
      setGroups(groupsRes.data);
    } catch { /* ignore */ }
    finally { setLoading(false); }
  };

  useEffect(() => { load(); }, []);

  const openCreate = () => {
    setEditSource(null);
    setForm({ ...emptyForm, groupId: selectedGroup ?? "" });
    setError("");
    setShowModal(true);
  };

  const openEdit = (s: DataSource) => {
    setEditSource(s);
    setForm({
      name: s.name,
      description: s.description || "",
      type: s.type || "postgresql",
      host: s.host || "",
      port: s.port !== undefined ? String(s.port) : "",
      database: s.database || "",
      tags: (s.tags || []).join(", "),
      status: s.status || "active",
      groupId: s.groupId || "",
    });
    setError("");
    setShowModal(true);
  };

  const save = async () => {
    if (!form.name.trim()) { setError("Name is required."); return; }
    const payload = {
      ...form,
      port: form.port ? parseInt(form.port, 10) : undefined,
      tags: form.tags.split(",").map(t => t.trim()).filter(Boolean),
    };
    try {
      if (editSource) {
        await api.put(`/registry/data-sources/${editSource.id}`, payload);
      } else {
        await api.post("/registry/data-sources", payload);
      }
      setShowModal(false);
      load();
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : "Failed to save.";
      setError(msg);
    }
  };

  const deleteSource = async (id: string) => {
    try { await api.delete(`/registry/data-sources/${id}`); setDeleteId(null); load(); } catch { /* ignore */ }
  };

  const saveGroup = async () => {
    if (!groupForm.name.trim()) { setGroupError("Group name is required."); return; }
    try {
      await api.post("/registry/data-sources/groups", groupForm);
      setShowGroupModal(false);
      setGroupForm({ name: "", description: "" });
      load();
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : "Failed to save group.";
      setGroupError(msg);
    }
  };

  const deleteGroup = async (id: string) => {
    try { await api.delete(`/registry/data-sources/groups/${id}`); load(); } catch { /* ignore */ }
  };

  const getHostDisplay = (s: DataSource) => {
    if (!s.host) return "—";
    if (s.port) return `${s.host}:${s.port}`;
    return s.host;
  };

  const filtered = sources.filter(s => {
    const matchesGroup = selectedGroup === null || s.groupId === selectedGroup;
    const matchesSearch =
      s.name.toLowerCase().includes(search.toLowerCase()) ||
      (s.host || "").toLowerCase().includes(search.toLowerCase()) ||
      (s.database || "").toLowerCase().includes(search.toLowerCase()) ||
      (s.type || "").toLowerCase().includes(search.toLowerCase());
    return matchesGroup && matchesSearch;
  });

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100">
      <div className="mx-auto max-w-7xl px-6 py-8">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-2xl font-bold text-white">Data Source Registry</h1>
            <p className="text-zinc-500 text-sm mt-1">Manage databases, storage, and file system connections</p>
          </div>
          <button
            onClick={openCreate}
            className="bg-violet-600 hover:bg-violet-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
          >
            + New Data Source
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
                All Sources
                <span className="float-right text-zinc-600 text-xs">{sources.length}</span>
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
                      {sources.filter(s => s.groupId === g.id).length}
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
                placeholder="Search data sources..."
                className="flex-1 bg-zinc-900 border border-zinc-800 rounded-lg px-3 py-2 text-sm text-zinc-100 placeholder-zinc-600 focus:outline-none focus:border-zinc-600"
              />
              <span className="text-zinc-500 text-sm">{filtered.length} sources</span>
            </div>

            {loading ? (
              <div className="text-zinc-500 text-sm py-8 text-center">Loading...</div>
            ) : (
              <div className="rounded-xl border border-zinc-800 overflow-hidden">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-zinc-800 bg-zinc-900/50">
                      <th className="text-left px-4 py-3 text-zinc-400 font-medium">Name</th>
                      <th className="text-left px-4 py-3 text-zinc-400 font-medium">Type</th>
                      <th className="text-left px-4 py-3 text-zinc-400 font-medium">Host / Location</th>
                      <th className="text-left px-4 py-3 text-zinc-400 font-medium">Status</th>
                      <th className="px-4 py-3"></th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-zinc-800/50">
                    {filtered.length === 0 && (
                      <tr>
                        <td colSpan={5} className="px-4 py-8 text-center text-zinc-600">
                          No data sources found. Add your first data source.
                        </td>
                      </tr>
                    )}
                    {filtered.map(s => (
                      <tr key={s.id} className="hover:bg-zinc-900/50 transition-colors">
                        <td className="px-4 py-3">
                          <div className="font-medium text-zinc-100">{s.name}</div>
                          {s.description && (
                            <div className="text-zinc-500 text-xs mt-0.5">{s.description}</div>
                          )}
                          {s.database && (
                            <div className="text-zinc-600 text-xs mt-0.5 font-mono">{s.database}</div>
                          )}
                        </td>
                        <td className="px-4 py-3">
                          <span className="text-zinc-300 text-xs font-medium">
                            {TYPE_LABELS[s.type || ""] || s.type || "—"}
                          </span>
                        </td>
                        <td className="px-4 py-3 text-zinc-400 font-mono text-xs">
                          {getHostDisplay(s)}
                        </td>
                        <td className="px-4 py-3">
                          <span className={`inline-flex rounded-full px-2 py-0.5 text-xs font-medium ${STATUS_COLORS[s.status ?? "active"] ?? STATUS_COLORS.active}`}>
                            {s.status ?? "active"}
                          </span>
                        </td>
                        <td className="px-4 py-3">
                          <div className="flex items-center gap-2 justify-end">
                            <button
                              onClick={() => openEdit(s)}
                              className="text-zinc-500 hover:text-zinc-200 text-xs px-2 py-1 rounded hover:bg-zinc-800 transition-colors"
                            >
                              Edit
                            </button>
                            {deleteId === s.id ? (
                              <div className="flex items-center gap-1">
                                <button
                                  onClick={() => deleteSource(s.id)}
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
                                onClick={() => setDeleteId(s.id)}
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
                {editSource ? "Edit Data Source" : "New Data Source"}
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
                  placeholder="production-db"
                />
              </div>
              <div>
                <label className="block text-xs text-zinc-400 mb-1.5">Type</label>
                <select
                  value={form.type}
                  onChange={e => setForm(f => ({ ...f, type: e.target.value }))}
                  className="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-3 py-2 text-sm text-zinc-100 focus:outline-none focus:border-violet-500"
                >
                  {SOURCE_TYPES.map(t => (
                    <option key={t} value={t}>{TYPE_LABELS[t] || t}</option>
                  ))}
                </select>
              </div>
              <div className="grid grid-cols-3 gap-3">
                <div className="col-span-2">
                  <label className="block text-xs text-zinc-400 mb-1.5">Host</label>
                  <input
                    value={form.host}
                    onChange={e => setForm(f => ({ ...f, host: e.target.value }))}
                    className="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-3 py-2 text-sm text-zinc-100 focus:outline-none focus:border-violet-500"
                    placeholder="localhost"
                  />
                </div>
                <div>
                  <label className="block text-xs text-zinc-400 mb-1.5">Port</label>
                  <input
                    type="number"
                    value={form.port}
                    onChange={e => setForm(f => ({ ...f, port: e.target.value }))}
                    className="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-3 py-2 text-sm text-zinc-100 focus:outline-none focus:border-violet-500"
                    placeholder="5432"
                  />
                </div>
              </div>
              <div>
                <label className="block text-xs text-zinc-400 mb-1.5">Database / Path</label>
                <input
                  value={form.database}
                  onChange={e => setForm(f => ({ ...f, database: e.target.value }))}
                  className="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-3 py-2 text-sm text-zinc-100 focus:outline-none focus:border-violet-500"
                  placeholder="my_database"
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
                  placeholder="production, analytics"
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
                    <option value="maintenance">Maintenance</option>
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
                {editSource ? "Save Changes" : "Create Data Source"}
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
                  placeholder="Production Databases"
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

"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";

type MCPServer = {
  id: string;
  name: string;
  url?: string;
  command?: string;
  description?: string;
  status?: string;
};

const STATUS_COLORS: Record<string, string> = {
  active: "bg-emerald-900/40 text-emerald-300 border border-emerald-700/40",
  inactive: "bg-zinc-800 text-zinc-400 border border-zinc-700",
};

export default function MCPServersPage() {
  const [servers, setServers] = useState<MCPServer[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editServer, setEditServer] = useState<MCPServer | null>(null);
  const [deleteId, setDeleteId] = useState<string | null>(null);
  const [search, setSearch] = useState("");
  const [form, setForm] = useState({ name: "", url: "", command: "", description: "", status: "active" });
  const [error, setError] = useState("");

  const load = async () => {
    try {
      const res = await api.get<{ data: MCPServer[] }>("/mcp-servers");
      setServers(res.data);
    } catch { /* ignore */ }
    finally { setLoading(false); }
  };

  useEffect(() => { load(); }, []);

  const openCreate = () => {
    setEditServer(null);
    setForm({ name: "", url: "", command: "", description: "", status: "active" });
    setError("");
    setShowModal(true);
  };

  const openEdit = (s: MCPServer) => {
    setEditServer(s);
    setForm({ name: s.name, url: s.url || "", command: s.command || "", description: s.description || "", status: s.status || "active" });
    setError("");
    setShowModal(true);
  };

  const save = async () => {
    if (!form.name.trim()) { setError("Name is required."); return; }
    if (!form.url.trim() && !form.command.trim()) { setError("Either URL or command is required."); return; }
    try {
      if (editServer) {
        await api.put(`/mcp-servers/${editServer.id}`, form);
      } else {
        await api.post("/mcp-servers", form);
      }
      setShowModal(false);
      load();
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : "Failed to save.";
      setError(msg);
    }
  };

  const deleteServer = async (id: string) => {
    try { await api.delete(`/mcp-servers/${id}`); setDeleteId(null); load(); } catch { /* ignore */ }
  };

  const filtered = servers.filter(s =>
    s.name.toLowerCase().includes(search.toLowerCase()) ||
    (s.url || "").toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100">
      <div className="mx-auto max-w-6xl px-6 py-8">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-2xl font-bold text-white">MCP Server Registry</h1>
            <p className="text-zinc-500 text-sm mt-1">Manage Model Context Protocol servers</p>
          </div>
          <button
            onClick={openCreate}
            className="bg-violet-600 hover:bg-violet-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
          >
            + New Server
          </button>
        </div>

        <div className="flex items-center gap-3 mb-4">
          <input
            value={search}
            onChange={e => setSearch(e.target.value)}
            placeholder="Search servers..."
            className="flex-1 bg-zinc-900 border border-zinc-800 rounded-lg px-3 py-2 text-sm text-zinc-100 placeholder-zinc-600 focus:outline-none focus:border-zinc-600"
          />
          <span className="text-zinc-500 text-sm">{filtered.length} servers</span>
        </div>

        {loading ? (
          <div className="text-zinc-500 text-sm py-8 text-center">Loading...</div>
        ) : (
          <div className="rounded-xl border border-zinc-800 overflow-hidden">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-zinc-800 bg-zinc-900/50">
                  <th className="text-left px-4 py-3 text-zinc-400 font-medium">Name</th>
                  <th className="text-left px-4 py-3 text-zinc-400 font-medium">URL / Command</th>
                  <th className="text-left px-4 py-3 text-zinc-400 font-medium">Status</th>
                  <th className="px-4 py-3"></th>
                </tr>
              </thead>
              <tbody className="divide-y divide-zinc-800/50">
                {filtered.length === 0 && (
                  <tr>
                    <td colSpan={4} className="px-4 py-8 text-center text-zinc-600">
                      No servers found. Add your first MCP server.
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
                    </td>
                    <td className="px-4 py-3 text-zinc-400 font-mono text-xs">
                      {s.url || s.command || "—"}
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
                              onClick={() => deleteServer(s.id)}
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

      {showModal && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-zinc-900 border border-zinc-800 rounded-2xl w-full max-w-lg shadow-2xl">
            <div className="flex items-center justify-between px-6 py-4 border-b border-zinc-800">
              <h2 className="text-base font-semibold text-white">
                {editServer ? "Edit MCP Server" : "New MCP Server"}
              </h2>
              <button
                onClick={() => setShowModal(false)}
                className="text-zinc-500 hover:text-zinc-300 text-xl leading-none"
              >
                ×
              </button>
            </div>
            <div className="p-6 space-y-4">
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
                  placeholder="my-mcp-server"
                />
              </div>
              <div>
                <label className="block text-xs text-zinc-400 mb-1.5">URL (for HTTP servers)</label>
                <input
                  value={form.url}
                  onChange={e => setForm(f => ({ ...f, url: e.target.value }))}
                  className="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-3 py-2 text-sm text-zinc-100 focus:outline-none focus:border-violet-500"
                  placeholder="http://localhost:3000/mcp"
                />
              </div>
              <div>
                <label className="block text-xs text-zinc-400 mb-1.5">Command (for stdio servers)</label>
                <input
                  value={form.command}
                  onChange={e => setForm(f => ({ ...f, command: e.target.value }))}
                  className="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-3 py-2 text-sm text-zinc-100 focus:outline-none focus:border-violet-500"
                  placeholder="npx my-mcp-server"
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
                <label className="block text-xs text-zinc-400 mb-1.5">Status</label>
                <select
                  value={form.status}
                  onChange={e => setForm(f => ({ ...f, status: e.target.value }))}
                  className="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-3 py-2 text-sm text-zinc-100 focus:outline-none focus:border-violet-500"
                >
                  <option value="active">Active</option>
                  <option value="inactive">Inactive</option>
                </select>
              </div>
            </div>
            <div className="flex justify-end gap-2 px-6 py-4 border-t border-zinc-800">
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
                {editServer ? "Save Changes" : "Create Server"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

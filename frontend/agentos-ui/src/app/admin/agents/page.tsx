"use client";

import { useCallback, useEffect, useState } from "react";
import { api, type Agent } from "@/lib/api";

export default function AgentsPage() {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [modal, setModal] = useState<"create" | "edit" | null>(null);
  const [editing, setEditing] = useState<Agent | null>(null);
  const [form, setForm] = useState({ name: "", role: "", model: "gpt-4", system_prompt: "", temperature: 0.7, status: "active" });

  const load = useCallback(() => {
    api.get<Agent[]>("/agents").then(setAgents).catch(() => {}).finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const filtered = agents.filter(
    (a) =>
      a.name.toLowerCase().includes(search.toLowerCase()) ||
      (a.role ?? "").toLowerCase().includes(search.toLowerCase())
  );

  const openCreate = () => {
    setForm({ name: "", role: "", model: "gpt-4", system_prompt: "", temperature: 0.7, status: "active" });
    setEditing(null);
    setModal("create");
  };

  const openEdit = (a: Agent) => {
    setForm({
      name: a.name,
      role: a.role ?? "",
      model: a.model ?? "gpt-4",
      system_prompt: a.system_prompt ?? "",
      temperature: a.temperature ?? 0.7,
      status: a.status ?? "active",
    });
    setEditing(a);
    setModal("edit");
  };

  const save = async () => {
    const payload = {
      name: form.name,
      role: form.role || undefined,
      model: form.model,
      system_prompt: form.system_prompt || undefined,
      temperature: form.temperature,
      status: form.status,
    };
    try {
      if (editing) {
        setAgents((prev) =>
          prev.map((a) =>
            a.id === editing.id ? { ...a, ...payload } : a
          )
        );
        await api.put(`/agents/${editing.id}`, payload);
      } else {
        const created = await api.post<Agent>("/agents", payload);
        setAgents((prev) => [...prev, created]);
      }
      setModal(null);
    } catch (e) {
      console.error(e);
    }
  };

  const remove = async (id: string) => {
    if (!confirm("Delete this agent?")) return;
    setAgents((prev) => prev.filter((a) => a.id !== id));
    try {
      await api.delete(`/agents/${id}`);
    } catch {
      load();
    }
  };

  return (
    <div className="mx-auto max-w-6xl px-6 py-8">
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-bold text-zinc-900 dark:text-zinc-100">
          Agent Management
        </h1>
        <button
          type="button"
          onClick={openCreate}
          className="rounded-lg bg-zinc-900 px-4 py-2 text-sm font-medium text-white dark:bg-zinc-100 dark:text-zinc-900"
        >
          Create New Agent
        </button>
      </div>

      <input
        type="search"
        placeholder="Search by name or role..."
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        className="mb-6 w-full max-w-md rounded-lg border border-zinc-200 bg-white px-4 py-2 dark:border-zinc-700 dark:bg-zinc-800 dark:text-zinc-100"
      />

      {loading ? (
        <div className="text-zinc-500">Loading...</div>
      ) : (
        <div className="overflow-x-auto rounded-lg border border-zinc-200 bg-white dark:border-zinc-800 dark:bg-zinc-900">
          <table className="w-full text-left">
            <thead>
              <tr className="border-b border-zinc-200 dark:border-zinc-800">
                <th className="px-4 py-3 font-medium">Name</th>
                <th className="px-4 py-3 font-medium">Role</th>
                <th className="px-4 py-3 font-medium">Model</th>
                <th className="px-4 py-3 font-medium">Status</th>
                <th className="px-4 py-3 font-medium">Actions</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((a) => (
                <tr key={a.id} className="border-b border-zinc-100 dark:border-zinc-800">
                  <td className="px-4 py-3">{a.name}</td>
                  <td className="px-4 py-3 text-zinc-600 dark:text-zinc-400">{a.role ?? "-"}</td>
                  <td className="px-4 py-3">{a.model ?? "-"}</td>
                  <td className="px-4 py-3">
                    <span
                      className={
                        a.status === "active"
                          ? "rounded bg-green-100 px-2 py-0.5 text-green-800 dark:bg-green-900/30 dark:text-green-400"
                          : "rounded bg-zinc-100 px-2 py-0.5 dark:bg-zinc-700 dark:text-zinc-400"
                      }
                    >
                      {a.status ?? "active"}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <button
                      type="button"
                      onClick={() => openEdit(a)}
                      className="mr-2 text-zinc-600 hover:text-zinc-900 dark:text-zinc-400 dark:hover:text-zinc-100"
                    >
                      Edit
                    </button>
                    <button
                      type="button"
                      onClick={() => remove(a.id)}
                      className="text-red-600 hover:text-red-800 dark:text-red-400"
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {modal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="w-full max-w-lg rounded-xl bg-white p-6 shadow-xl dark:bg-zinc-900">
            <h2 className="text-lg font-semibold">
              {modal === "create" ? "Create Agent" : "Edit Agent"}
            </h2>
            <div className="mt-4 space-y-4">
              <input
                placeholder="Name"
                value={form.name}
                onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
                className="w-full rounded border px-3 py-2 dark:bg-zinc-800 dark:text-zinc-100"
              />
              <input
                placeholder="Role"
                value={form.role}
                onChange={(e) => setForm((f) => ({ ...f, role: e.target.value }))}
                className="w-full rounded border px-3 py-2 dark:bg-zinc-800 dark:text-zinc-100"
              />
              <select
                value={form.model}
                onChange={(e) => setForm((f) => ({ ...f, model: e.target.value }))}
                className="w-full rounded border px-3 py-2 dark:bg-zinc-800 dark:text-zinc-100"
              >
                <option value="gpt-4">GPT-4</option>
                <option value="claude-3-5-sonnet">Claude 3.5 Sonnet</option>
                <option value="gemini-1.5-pro">Gemini 1.5 Pro</option>
              </select>
              <textarea
                placeholder="System prompt"
                value={form.system_prompt}
                onChange={(e) => setForm((f) => ({ ...f, system_prompt: e.target.value }))}
                rows={3}
                className="w-full rounded border px-3 py-2 dark:bg-zinc-800 dark:text-zinc-100"
              />
              <input
                type="number"
                step={0.1}
                min={0}
                max={2}
                placeholder="Temperature"
                value={form.temperature}
                onChange={(e) => setForm((f) => ({ ...f, temperature: parseFloat(e.target.value) || 0 }))}
                className="w-full rounded border px-3 py-2 dark:bg-zinc-800 dark:text-zinc-100"
              />
              <select
                value={form.status}
                onChange={(e) => setForm((f) => ({ ...f, status: e.target.value }))}
                className="w-full rounded border px-3 py-2 dark:bg-zinc-800 dark:text-zinc-100"
              >
                <option value="active">Active</option>
                <option value="inactive">Inactive</option>
                <option value="draft">Draft</option>
              </select>
            </div>
            <div className="mt-6 flex justify-end gap-2">
              <button
                type="button"
                onClick={() => setModal(null)}
                className="rounded px-4 py-2 text-zinc-600 hover:bg-zinc-100 dark:hover:bg-zinc-800"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={save}
                disabled={!form.name}
                className="rounded bg-zinc-900 px-4 py-2 text-white disabled:opacity-50 dark:bg-zinc-100 dark:text-zinc-900"
              >
                Save
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

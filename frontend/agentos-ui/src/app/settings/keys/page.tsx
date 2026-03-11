/**
 * File: settings/keys/page.tsx
 * API Key management — create, list, revoke named API keys.
 */
"use client";

import { useEffect, useState } from "react";

type APIKey = { id: string; name: string; key: string; createdAt: string };

export default function APIKeysPage() {
  const [keys, setKeys] = useState<APIKey[]>([]);
  const [newName, setNewName] = useState("");
  const [creating, setCreating] = useState(false);
  const [revealed, setRevealed] = useState<string | null>(null);
  const token = typeof window !== "undefined" ? localStorage.getItem("agentos_token") : null;

  async function loadKeys() {
    if (!token) return;
    const res = await fetch("/api/v1/auth/keys", { headers: { Authorization: `Bearer ${token}` } });
    if (res.ok) { const j = await res.json(); setKeys(j.data || []); }
  }

  useEffect(() => { loadKeys(); }, [token]);

  async function createKey() {
    if (!token || !newName.trim()) return;
    setCreating(true);
    try {
      const res = await fetch("/api/v1/auth/keys", {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify({ name: newName.trim() }),
      });
      if (res.ok) {
        const j = await res.json();
        setKeys((prev) => [...prev, j.data]);
        setRevealed(j.data.id);
        setNewName("");
      }
    } finally { setCreating(false); }
  }

  async function deleteKey(id: string) {
    if (!token) return;
    await fetch(`/api/v1/auth/keys/${id}`, {
      method: "DELETE",
      headers: { Authorization: `Bearer ${token}` },
    });
    setKeys((prev) => prev.filter((k) => k.id !== id));
    if (revealed === id) setRevealed(null);
  }

  if (!token) {
    return (
      <div className="mx-auto max-w-2xl px-6 py-16 text-center">
        <p className="text-zinc-600 dark:text-zinc-400">Please <a href="/profile" className="underline text-zinc-900 dark:text-zinc-100">sign in</a> to manage API keys.</p>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-2xl px-6 py-10">
      <h1 className="mb-2 text-2xl font-bold text-zinc-900 dark:text-zinc-100">API Keys</h1>
      <p className="mb-8 text-sm text-zinc-500">Create named keys for programmatic access to the AgentOS API.</p>

      {/* Create new key */}
      <div className="mb-8 rounded-xl border border-zinc-200 bg-white p-6 dark:border-zinc-800 dark:bg-zinc-900">
        <h2 className="mb-4 text-sm font-semibold text-zinc-700 dark:text-zinc-300">Create New Key</h2>
        <div className="flex gap-3">
          <input
            value={newName}
            onChange={(e) => setNewName(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && createKey()}
            placeholder="Key name (e.g. production-api)"
            className="flex-1 rounded-xl border border-zinc-300 px-4 py-2.5 text-sm dark:border-zinc-700 dark:bg-zinc-800 dark:text-zinc-100"
          />
          <button
            onClick={createKey}
            disabled={creating || !newName.trim()}
            className="rounded-xl bg-zinc-900 px-5 py-2.5 text-sm font-medium text-white disabled:opacity-50 dark:bg-zinc-100 dark:text-zinc-900"
          >
            {creating ? "Creating…" : "Create"}
          </button>
        </div>
      </div>

      {/* Key list */}
      <div className="rounded-xl border border-zinc-200 bg-white dark:border-zinc-800 dark:bg-zinc-900">
        <div className="border-b border-zinc-200 px-6 py-4 dark:border-zinc-800">
          <p className="text-sm font-semibold text-zinc-700 dark:text-zinc-300">Your API Keys ({keys.length})</p>
        </div>
        {keys.length === 0 ? (
          <p className="px-6 py-8 text-center text-sm text-zinc-400">No API keys yet</p>
        ) : (
          <div className="divide-y divide-zinc-100 dark:divide-zinc-800">
            {keys.map((key) => (
              <div key={key.id} className="px-6 py-4">
                <div className="flex items-start justify-between">
                  <div>
                    <p className="text-sm font-medium text-zinc-800 dark:text-zinc-200">{key.name}</p>
                    <p className="text-xs text-zinc-400 mt-0.5">
                      Created {new Date(key.createdAt).toLocaleDateString()}
                    </p>
                  </div>
                  <button
                    onClick={() => deleteKey(key.id)}
                    className="rounded-lg border border-red-200 px-3 py-1 text-xs text-red-500 hover:bg-red-50 dark:border-red-800 dark:hover:bg-red-900/20"
                  >
                    Revoke
                  </button>
                </div>
                <div className="mt-2 flex items-center gap-2">
                  <code className="flex-1 rounded-lg bg-zinc-50 px-3 py-1.5 text-xs font-mono text-zinc-600 dark:bg-zinc-800 dark:text-zinc-400 truncate">
                    {revealed === key.id ? key.key : `${key.key.slice(0, 12)}${"•".repeat(24)}`}
                  </code>
                  <button
                    onClick={() => setRevealed(revealed === key.id ? null : key.id)}
                    className="shrink-0 text-xs text-zinc-500 hover:text-zinc-700 dark:hover:text-zinc-300"
                  >
                    {revealed === key.id ? "Hide" : "Show"}
                  </button>
                  <button
                    onClick={() => navigator.clipboard.writeText(key.key)}
                    className="shrink-0 text-xs text-zinc-500 hover:text-zinc-700 dark:hover:text-zinc-300"
                  >
                    Copy
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

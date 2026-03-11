/**
 * File: page.tsx (API Keys)
 * 
 * Purpose:
 * Provides an interface for users to generate, view, and revoke personal API keys
 * for programmatic access to the AgentOS platform.
 */
"use client";

import { useState, useEffect } from "react";
import { api, APIKey, APIResponse } from "@/lib/api";

export default function APIKeysPage() {
  const [keys, setKeys] = useState<APIKey[]>([]);
  const [loading, setLoading] = useState(true);
  const [newKeyName, setNewKeyName] = useState("");
  const [isCreating, setIsCreating] = useState(false);

  useEffect(() => {
    api.get<APIResponse<APIKey[]>>("/auth/keys")
      .then(res => setKeys(res.data))
      .finally(() => setLoading(false));
  }, []);

  const createKey = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newKeyName) return;
    setIsCreating(true);
    try {
      const res = await api.post<APIResponse<APIKey>>("/auth/keys", { name: newKeyName });
      setKeys([...keys, res.data]);
      setNewKeyName("");
    } catch {
      alert("Failed to create API key");
    } finally {
      setIsCreating(false);
    }
  };

  const deleteKey = async (id: string) => {
    if (!confirm("Are you sure you want to revoke this API key?")) return;
    try {
      await api.delete(`/auth/keys/${id}`);
      setKeys(keys.filter(k => k.id !== id));
    } catch {
      alert("Failed to delete API key");
    }
  };

  if (loading) return <div className="p-8 text-center text-zinc-500">Loading API keys...</div>;

  return (
    <main className="mx-auto max-w-5xl p-8">
      <div className="mb-10">
        <h1 className="text-3xl font-bold tracking-tight text-zinc-900 dark:text-zinc-100">API Keys</h1>
        <p className="mt-2 text-zinc-500">Manage keys for programmatic access to your agents and workflows.</p>
      </div>

      <div className="mb-12 rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
        <h2 className="mb-4 text-sm font-semibold text-zinc-900 dark:text-zinc-100">Create New Key</h2>
        <form onSubmit={createKey} className="flex gap-3">
          <input
            type="text"
            placeholder="Key Name (e.g. Production-Backend)"
            value={newKeyName}
            onChange={(e) => setNewKeyName(e.target.value)}
            className="flex-1 rounded-lg border border-zinc-200 bg-zinc-50 px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-zinc-900/10 dark:border-zinc-800 dark:bg-zinc-950 dark:focus:ring-zinc-100/10"
          />
          <button
            type="submit"
            disabled={isCreating}
            className="rounded-lg bg-zinc-900 px-6 py-2 text-sm font-medium text-white transition-opacity hover:opacity-90 disabled:opacity-50 dark:bg-zinc-100 dark:text-zinc-900"
          >
            {isCreating ? "Generating..." : "Generate Key"}
          </button>
        </form>
      </div>

      <div className="overflow-hidden rounded-2xl border border-zinc-200 bg-white shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
        <table className="w-full text-left text-sm">
          <thead className="border-b border-zinc-100 bg-zinc-50 dark:border-zinc-800 dark:bg-zinc-950">
            <tr>
              <th className="px-6 py-4 font-semibold text-zinc-900 dark:text-zinc-100">Name</th>
              <th className="px-6 py-4 font-semibold text-zinc-900 dark:text-zinc-100">Secret Key</th>
              <th className="px-6 py-4 font-semibold text-zinc-900 dark:text-zinc-100">Created</th>
              <th className="px-6 py-4 font-semibold text-zinc-900 dark:text-zinc-100">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-zinc-100 dark:divide-zinc-800">
            {keys.length === 0 ? (
              <tr>
                <td colSpan={4} className="px-6 py-10 text-center text-zinc-500">No API keys found.</td>
              </tr>
            ) : (
              keys.map((key) => (
                <tr key={key.id} className="hover:bg-zinc-50 dark:hover:bg-zinc-950">
                  <td className="px-6 py-4 font-medium text-zinc-900 dark:text-zinc-100">{key.name}</td>
                  <td className="px-6 py-4">
                    <code className="rounded bg-zinc-100 px-2 py-0.5 font-mono text-xs dark:bg-zinc-800">{key.key}</code>
                  </td>
                  <td className="px-6 py-4 text-zinc-500">{new Date(key.createdAt).toLocaleDateString()}</td>
                  <td className="px-6 py-4">
                    <button
                      onClick={() => deleteKey(key.id)}
                      className="text-red-600 hover:text-red-700 dark:text-red-400 dark:hover:text-red-300"
                    >
                      Revoke
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </main>
  );
}

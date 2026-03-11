/**
 * File: page.tsx (Profile)
 * 
 * Purpose:
 * Renders the user profile page, allowing users to view and edit their personal information
 * and role within the AgentOS platform.
 */
"use client";

import { useState, useEffect } from "react";
import { api, User, APIResponse } from "@/lib/api";

export default function ProfilePage() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get<APIResponse<User>>("/auth/me")
      .then(res => setUser(res.data))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="p-8 text-center">Loading profile...</div>;
  if (!user) return <div className="p-8 text-center text-red-500">Failed to load profile.</div>;

  return (
    <main className="mx-auto max-w-4xl p-8">
      <div className="mb-8 flex items-center justify-between">
        <h1 className="text-3xl font-bold tracking-tight text-zinc-900 dark:text-zinc-100">User Profile</h1>
        <span className="rounded-full bg-blue-100 px-3 py-1 text-sm font-medium text-blue-800 dark:bg-blue-900/30 dark:text-blue-300">
          {user.role}
        </span>
      </div>

      <div className="relative overflow-hidden rounded-2xl border border-zinc-200 bg-white/50 p-8 shadow-sm backdrop-blur-xl dark:border-zinc-800 dark:bg-zinc-900/50">
        <div className="grid gap-6 md:grid-cols-2">
          <div>
            <label className="block text-sm font-medium text-zinc-500 dark:text-zinc-400">Full Name</label>
            <p className="mt-1 text-lg font-medium text-zinc-900 dark:text-zinc-100">{user.full_name || "N/A"}</p>
          </div>
          <div>
            <label className="block text-sm font-medium text-zinc-500 dark:text-zinc-400">Email Address</label>
            <p className="mt-1 text-lg font-medium text-zinc-900 dark:text-zinc-100">{user.email}</p>
          </div>
          <div>
            <label className="block text-sm font-medium text-zinc-500 dark:text-zinc-400">User ID</label>
            <p className="mt-1 font-mono text-sm text-zinc-600 dark:text-zinc-400">{user.id}</p>
          </div>
        </div>

        <div className="mt-10 border-t border-zinc-100 pt-6 dark:border-zinc-800">
          <button className="rounded-lg bg-zinc-900 px-4 py-2 text-sm font-medium text-white transition-opacity hover:opacity-90 dark:bg-zinc-100 dark:text-zinc-900">
            Edit Profile
          </button>
        </div>
      </div>
    </main>
  );
}

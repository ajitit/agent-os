/**
 * File: profile/page.tsx
 *
 * User auth page — login, register, and profile management.
 * Stores JWT in localStorage for use across the app.
 */
"use client";

import { useEffect, useState } from "react";

type User = {
  id: string;
  email: string;
  full_name?: string;
  role: "admin" | "developer" | "operator" | "viewer";
};

type View = "login" | "register" | "profile";

export default function ProfilePage() {
  const [view, setView] = useState<View>("login");
  const [user, setUser] = useState<User | null>(null);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [role, setRole] = useState<User["role"]>("operator");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem("vishwakarma_token");
    if (token) loadMe(token);
  }, []);

  async function loadMe(token: string) {
    try {
      const res = await fetch("/api/v1/auth/me", {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.ok) {
        const j = await res.json();
        setUser(j.data);
        setView("profile");
      }
    } catch {}
  }

  async function handleLogin() {
    setLoading(true); setError("");
    try {
      const form = new URLSearchParams();
      form.append("username", email);
      form.append("password", password);
      const res = await fetch("/api/v1/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: form.toString(),
      });
      const j = await res.json();
      if (!res.ok) { setError(j.detail || "Login failed"); return; }
      const token = j.data?.access_token;
      if (token) {
        localStorage.setItem("vishwakarma_token", token);
        await loadMe(token);
      }
    } finally { setLoading(false); }
  }

  async function handleRegister() {
    setLoading(true); setError("");
    try {
      const res = await fetch("/api/v1/auth/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password, full_name: fullName, role }),
      });
      const j = await res.json();
      if (!res.ok) { setError(j.detail || "Registration failed"); return; }
      setView("login");
      setError("Registered! Please log in.");
    } finally { setLoading(false); }
  }

  function handleLogout() {
    localStorage.removeItem("vishwakarma_token");
    setUser(null);
    setView("login");
    setEmail(""); setPassword("");
  }

  const ROLE_BADGE: Record<string, string> = {
    admin: "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300",
    developer: "bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-300",
    operator: "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300",
    viewer: "bg-zinc-100 text-zinc-600 dark:bg-zinc-700 dark:text-zinc-300",
  };

  return (
    <div className="mx-auto max-w-md px-6 py-16">
      {view === "profile" && user ? (
        <div className="rounded-2xl border border-zinc-200 bg-white p-8 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
          <div className="flex items-center gap-4 mb-6">
            <div className="flex h-16 w-16 items-center justify-center rounded-full bg-zinc-100 text-2xl font-bold text-zinc-700 dark:bg-zinc-800 dark:text-zinc-300">
              {user.email[0].toUpperCase()}
            </div>
            <div>
              <p className="font-semibold text-zinc-900 dark:text-zinc-100">{user.full_name || user.email}</p>
              <p className="text-sm text-zinc-500">{user.email}</p>
              <span className={`mt-1 inline-block rounded-full px-2 py-0.5 text-xs font-medium ${ROLE_BADGE[user.role]}`}>
                {user.role}
              </span>
            </div>
          </div>
          <div className="space-y-3 border-t border-zinc-200 pt-4 dark:border-zinc-800">
            <div className="flex justify-between text-sm">
              <span className="text-zinc-500">User ID</span>
              <span className="font-mono text-xs text-zinc-600 dark:text-zinc-400">{user.id.slice(0, 16)}…</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-zinc-500">Role</span>
              <span className="text-zinc-700 dark:text-zinc-300 capitalize">{user.role}</span>
            </div>
          </div>
          <div className="mt-6 flex gap-3">
            <a href="/settings/preferences" className="flex-1 rounded-xl border border-zinc-300 py-2 text-center text-sm text-zinc-600 hover:bg-zinc-50 dark:border-zinc-700 dark:text-zinc-300">
              Preferences
            </a>
            <a href="/settings/keys" className="flex-1 rounded-xl border border-zinc-300 py-2 text-center text-sm text-zinc-600 hover:bg-zinc-50 dark:border-zinc-700 dark:text-zinc-300">
              API Keys
            </a>
          </div>
          <button
            onClick={handleLogout}
            className="mt-3 w-full rounded-xl border border-red-200 py-2 text-sm text-red-600 hover:bg-red-50 dark:border-red-800 dark:text-red-400"
          >
            Sign Out
          </button>
        </div>
      ) : view === "login" ? (
        <div className="rounded-2xl border border-zinc-200 bg-white p-8 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
          <h1 className="mb-6 text-2xl font-bold text-zinc-900 dark:text-zinc-100">Sign In</h1>
          {error && <p className="mb-4 rounded-lg bg-red-50 px-4 py-3 text-sm text-red-600 dark:bg-red-900/20 dark:text-red-400">{error}</p>}
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1">Email</label>
              <input
                type="email" value={email}
                onChange={(e) => setEmail(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleLogin()}
                className="w-full rounded-xl border border-zinc-300 px-4 py-2.5 text-sm dark:border-zinc-700 dark:bg-zinc-800 dark:text-zinc-100"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1">Password</label>
              <input
                type="password" value={password}
                onChange={(e) => setPassword(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleLogin()}
                className="w-full rounded-xl border border-zinc-300 px-4 py-2.5 text-sm dark:border-zinc-700 dark:bg-zinc-800 dark:text-zinc-100"
              />
            </div>
            <button
              onClick={handleLogin}
              disabled={loading || !email || !password}
              className="w-full rounded-xl bg-zinc-900 py-2.5 text-sm font-medium text-white disabled:opacity-50 dark:bg-zinc-100 dark:text-zinc-900"
            >
              {loading ? "Signing in…" : "Sign In"}
            </button>
          </div>
          <p className="mt-4 text-center text-sm text-zinc-500">
            No account?{" "}
            <button onClick={() => { setView("register"); setError(""); }} className="text-zinc-900 underline dark:text-zinc-100">
              Register
            </button>
          </p>
        </div>
      ) : (
        <div className="rounded-2xl border border-zinc-200 bg-white p-8 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
          <h1 className="mb-6 text-2xl font-bold text-zinc-900 dark:text-zinc-100">Create Account</h1>
          {error && <p className="mb-4 rounded-lg bg-red-50 px-4 py-3 text-sm text-red-600 dark:bg-red-900/20 dark:text-red-400">{error}</p>}
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1">Full Name</label>
              <input
                type="text" value={fullName} onChange={(e) => setFullName(e.target.value)}
                className="w-full rounded-xl border border-zinc-300 px-4 py-2.5 text-sm dark:border-zinc-700 dark:bg-zinc-800 dark:text-zinc-100"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1">Email</label>
              <input
                type="email" value={email} onChange={(e) => setEmail(e.target.value)}
                className="w-full rounded-xl border border-zinc-300 px-4 py-2.5 text-sm dark:border-zinc-700 dark:bg-zinc-800 dark:text-zinc-100"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1">Password</label>
              <input
                type="password" value={password} onChange={(e) => setPassword(e.target.value)}
                className="w-full rounded-xl border border-zinc-300 px-4 py-2.5 text-sm dark:border-zinc-700 dark:bg-zinc-800 dark:text-zinc-100"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1">Role</label>
              <select
                value={role} onChange={(e) => setRole(e.target.value as User["role"])}
                className="w-full rounded-xl border border-zinc-300 px-4 py-2.5 text-sm dark:border-zinc-700 dark:bg-zinc-800 dark:text-zinc-100"
              >
                <option value="operator">Operator</option>
                <option value="developer">Developer</option>
                <option value="admin">Admin</option>
                <option value="viewer">Viewer</option>
              </select>
            </div>
            <button
              onClick={handleRegister}
              disabled={loading || !email || !password}
              className="w-full rounded-xl bg-zinc-900 py-2.5 text-sm font-medium text-white disabled:opacity-50 dark:bg-zinc-100 dark:text-zinc-900"
            >
              {loading ? "Creating account…" : "Create Account"}
            </button>
          </div>
          <p className="mt-4 text-center text-sm text-zinc-500">
            Already have an account?{" "}
            <button onClick={() => { setView("login"); setError(""); }} className="text-zinc-900 underline dark:text-zinc-100">
              Sign In
            </button>
          </p>
        </div>
      )}
    </div>
  );
}

/**
 * File: settings/preferences/page.tsx
 * Full preferences UI — appearance, chat, workflow builder, observability, notifications.
 */
"use client";

import { useEffect, useState } from "react";

type Prefs = {
  theme: "light" | "dark" | "system";
  accentColor: string;
  fontSize: "sm" | "md" | "lg";
  defaultPriority: "low" | "normal" | "high";
  streamingEnabled: boolean;
  showAgentThinking: boolean;
  defaultSupervisorBehavior: "auto_route" | "confirm_routing" | "manual_select";
  emailOnFailure: boolean;
  emailDigestFrequency: "never" | "daily" | "weekly";
};

const DEFAULTS: Prefs = {
  theme: "system",
  accentColor: "#18181b",
  fontSize: "md",
  defaultPriority: "normal",
  streamingEnabled: true,
  showAgentThinking: true,
  defaultSupervisorBehavior: "auto_route",
  emailOnFailure: false,
  emailDigestFrequency: "never",
};

export default function PreferencesPage() {
  const [prefs, setPrefs] = useState<Prefs>(DEFAULTS);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const token = typeof window !== "undefined" ? localStorage.getItem("vishwakarma_token") : null;

  useEffect(() => {
    if (!token) return;
    fetch("/api/v1/preferences", { headers: { Authorization: `Bearer ${token}` } })
      .then((r) => r.json())
      .then((j) => { if (j.data && Object.keys(j.data).length > 0) setPrefs({ ...DEFAULTS, ...j.data }); })
      .catch(() => {});
  }, [token]);

  async function save() {
    if (!token) return;
    setSaving(true);
    try {
      await fetch("/api/v1/preferences", {
        method: "PUT",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify(prefs),
      });
      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
    } finally { setSaving(false); }
  }

  function set<K extends keyof Prefs>(key: K, value: Prefs[K]) {
    setPrefs((p) => ({ ...p, [key]: value }));
  }

  const section = (title: string, children: React.ReactNode) => (
    <div className="rounded-xl border border-zinc-200 bg-white p-6 dark:border-zinc-800 dark:bg-zinc-900">
      <h2 className="mb-4 text-sm font-semibold text-zinc-700 dark:text-zinc-300">{title}</h2>
      <div className="space-y-4">{children}</div>
    </div>
  );

  const row = (label: string, children: React.ReactNode) => (
    <div className="flex items-center justify-between">
      <span className="text-sm text-zinc-600 dark:text-zinc-400">{label}</span>
      {children}
    </div>
  );

  const toggle = (key: keyof Prefs) => (
    <button
      onClick={() => set(key, !prefs[key] as Prefs[typeof key])}
      className={`relative inline-flex h-6 w-11 items-center rounded-full transition ${
        prefs[key] ? "bg-zinc-900 dark:bg-zinc-100" : "bg-zinc-300 dark:bg-zinc-700"
      }`}
    >
      <span className={`inline-block h-4 w-4 rounded-full bg-white transition ${prefs[key] ? "translate-x-6" : "translate-x-1"}`} />
    </button>
  );

  if (!token) {
    return (
      <div className="mx-auto max-w-2xl px-6 py-16 text-center">
        <p className="text-zinc-600 dark:text-zinc-400">Please <a href="/profile" className="underline text-zinc-900 dark:text-zinc-100">sign in</a> to manage preferences.</p>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-2xl px-6 py-10">
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-bold text-zinc-900 dark:text-zinc-100">Preferences</h1>
        <button
          onClick={save}
          disabled={saving}
          className="rounded-xl bg-zinc-900 px-5 py-2 text-sm font-medium text-white disabled:opacity-50 dark:bg-zinc-100 dark:text-zinc-900"
        >
          {saved ? "✓ Saved" : saving ? "Saving…" : "Save"}
        </button>
      </div>

      <div className="space-y-4">
        {section("Appearance", <>
          {row("Theme", (
            <select value={prefs.theme} onChange={(e) => set("theme", e.target.value as Prefs["theme"])}
              className="rounded-lg border border-zinc-300 px-3 py-1.5 text-sm dark:border-zinc-700 dark:bg-zinc-800 dark:text-zinc-100">
              <option value="system">System</option>
              <option value="light">Light</option>
              <option value="dark">Dark</option>
            </select>
          ))}
          {row("Font Size", (
            <select value={prefs.fontSize} onChange={(e) => set("fontSize", e.target.value as Prefs["fontSize"])}
              className="rounded-lg border border-zinc-300 px-3 py-1.5 text-sm dark:border-zinc-700 dark:bg-zinc-800 dark:text-zinc-100">
              <option value="sm">Small</option>
              <option value="md">Medium</option>
              <option value="lg">Large</option>
            </select>
          ))}
        </>)}

        {section("Chat UI", <>
          {row("Streaming Enabled", toggle("streamingEnabled"))}
          {row("Show Agent Thinking", toggle("showAgentThinking"))}
          {row("Default Priority", (
            <select value={prefs.defaultPriority} onChange={(e) => set("defaultPriority", e.target.value as Prefs["defaultPriority"])}
              className="rounded-lg border border-zinc-300 px-3 py-1.5 text-sm dark:border-zinc-700 dark:bg-zinc-800 dark:text-zinc-100">
              <option value="low">Low</option>
              <option value="normal">Normal</option>
              <option value="high">High</option>
            </select>
          ))}
          {row("Supervisor Routing", (
            <select value={prefs.defaultSupervisorBehavior} onChange={(e) => set("defaultSupervisorBehavior", e.target.value as Prefs["defaultSupervisorBehavior"])}
              className="rounded-lg border border-zinc-300 px-3 py-1.5 text-sm dark:border-zinc-700 dark:bg-zinc-800 dark:text-zinc-100">
              <option value="auto_route">Auto Route</option>
              <option value="confirm_routing">Confirm Routing</option>
              <option value="manual_select">Manual Select</option>
            </select>
          ))}
        </>)}

        {section("Notifications", <>
          {row("Email on Failure", toggle("emailOnFailure"))}
          {row("Email Digest", (
            <select value={prefs.emailDigestFrequency} onChange={(e) => set("emailDigestFrequency", e.target.value as Prefs["emailDigestFrequency"])}
              className="rounded-lg border border-zinc-300 px-3 py-1.5 text-sm dark:border-zinc-700 dark:bg-zinc-800 dark:text-zinc-100">
              <option value="never">Never</option>
              <option value="daily">Daily</option>
              <option value="weekly">Weekly</option>
            </select>
          ))}
        </>)}
      </div>
    </div>
  );
}

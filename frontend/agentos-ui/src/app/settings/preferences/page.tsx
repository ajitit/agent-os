/**
 * File: page.tsx (Preferences)
 * 
 * Purpose:
 * Renders the user preferences page, allowing customization of UI themes, 
 * behavior, and notification settings with real-time optimistic updates.
 */
"use client";

import { useState, useEffect } from "react";
import { api, UserPreferences, APIResponse } from "@/lib/api";

export default function PreferencesPage() {
  const [prefs, setPrefs] = useState<UserPreferences | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    api.get<APIResponse<UserPreferences>>("/preferences")
      .then(res => setPrefs(res.data))
      .finally(() => setLoading(false));
  }, []);

  const updatePref = async (updates: Partial<UserPreferences>) => {
    if (!prefs) return;
    const previous = { ...prefs };
    setPrefs({ ...prefs, ...updates });
    setSaving(true);
    try {
      await api.put<APIResponse<UserPreferences>>("/preferences", updates);
    } catch {
      setPrefs(previous);
      alert("Failed to save preference");
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <div className="p-8 text-center">Loading preferences...</div>;
  if (!prefs) return <div className="p-8 text-center text-red-500">Failed to load preferences.</div>;

  const Section = ({ title, children }: { title: string; children: React.ReactNode }) => (
    <section className="mb-10">
      <h2 className="mb-4 text-xs font-semibold uppercase tracking-widest text-zinc-400 dark:text-zinc-500">{title}</h2>
      <div className="rounded-2xl border border-zinc-200 bg-white/30 p-6 shadow-sm backdrop-blur-md dark:border-zinc-800 dark:bg-zinc-900/30">
        {children}
      </div>
    </section>
  );

  const Toggle = ({ label, value, onChange }: { label: string; value: boolean; onChange: (v: boolean) => void }) => (
    <div className="flex items-center justify-between py-3">
      <span className="text-sm font-medium text-zinc-700 dark:text-zinc-300">{label}</span>
      <button
        onClick={() => onChange(!value)}
        className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
          value ? "bg-zinc-900 dark:bg-zinc-100" : "bg-zinc-200 dark:bg-zinc-800"
        }`}
      >
        <span
          className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform dark:bg-zinc-500 ${
            value ? "translate-x-6" : "translate-x-1"
          }`}
        />
      </button>
    </div>
  );

  const Select = ({ label, options, value, onChange }: { label: string; options: { id: string; name: string }[]; value: string; onChange: (v: string) => void }) => (
    <div className="flex items-center justify-between py-3">
      <span className="text-sm font-medium text-zinc-700 dark:text-zinc-300">{label}</span>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="rounded-md border border-zinc-200 bg-transparent px-2 py-1 text-sm dark:border-zinc-800"
      >
        {options.map(o => <option key={o.id} value={o.id}>{o.name}</option>)}
      </select>
    </div>
  );

  return (
    <main className="mx-auto max-w-3xl p-8 pb-20">
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-zinc-900 dark:text-zinc-100">Preferences</h1>
          <p className="mt-1 text-zinc-500">Personalize your AgentOS experience</p>
        </div>
        {saving && <span className="text-xs text-zinc-400 animate-pulse">Saving changes...</span>}
      </div>

      <Section title="Appearance">
        <Select
          label="Theme"
          value={prefs.theme}
          options={[{ id: "light", name: "Light" }, { id: "dark", name: "Dark" }, { id: "system", name: "System" }]}
          onChange={(v) => updatePref({ theme: v as UserPreferences["theme"] })}
        />
        <Select
          label="Font Size"
          value={prefs.fontSize}
          options={[{ id: "sm", name: "Small" }, { id: "md", name: "Medium" }, { id: "lg", name: "Large" }]}
          onChange={(v) => updatePref({ fontSize: v as UserPreferences["fontSize"] })}
        />
      </Section>

      <Section title="Chat Behavior">
        <Toggle
          label="Enable Streaming Output"
          value={prefs.streamingEnabled}
          onChange={(v) => updatePref({ streamingEnabled: v })}
        />
        <Toggle
          label="Show Agent Thinking Process"
          value={prefs.showAgentThinking}
          onChange={(v) => updatePref({ showAgentThinking: v })}
        />
        <Select
          label="Supervisor Strategy"
          value={prefs.defaultSupervisorBehavior}
          options={[
            { id: "auto_route", name: "Auto Route" },
            { id: "confirm_routing", name: "Confirm Routing" },
            { id: "manual_select", name: "Manual Select" }
          ]}
          onChange={(v) => updatePref({ defaultSupervisorBehavior: v as UserPreferences["defaultSupervisorBehavior"] })}
        />
      </Section>

      <Section title="Notifications">
        <Toggle
          label="Email on Run Failure"
          value={prefs.emailOnFailure}
          onChange={(v) => updatePref({ emailOnFailure: v })}
        />
        <Select
          label="Digest Frequency"
          value={prefs.emailDigestFrequency}
          options={[
            { id: "never", name: "Never" },
            { id: "daily", name: "Daily" },
            { id: "weekly", name: "Weekly" }
          ]}
          onChange={(v) => updatePref({ emailDigestFrequency: v as UserPreferences["emailDigestFrequency"] })}
        />
      </Section>
    </main>
  );
}

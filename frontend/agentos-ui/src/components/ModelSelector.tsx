"use client";

import { useEffect, useState } from "react";
import { api, type ModelSetting } from "@/lib/api";

export function ModelSelector() {
  const [settings, setSettings] = useState<ModelSetting | null>(null);
  const [open, setOpen] = useState(false);

  useEffect(() => {
    api.get<ModelSetting>("/settings/models").then(setSettings).catch(() => {});
  }, []);

  const handleChange = async (modelId: string) => {
    if (!settings) return;
    try {
      await api.put("/settings/models", { primary_model: modelId });
      setSettings({ ...settings, primary_model: modelId });
      setOpen(false);
    } catch {
      /* ignore */
    }
  };

  if (!settings) return null;

  const current = settings.available_models.find((m) => m.id === settings.primary_model);

  return (
    <div className="relative">
      <button
        type="button"
        onClick={() => setOpen(!open)}
        className="flex items-center gap-2 rounded-lg border border-zinc-200 bg-white px-3 py-1.5 text-sm dark:border-zinc-700 dark:bg-zinc-800"
      >
        <span className="text-zinc-500">Model:</span>
        <span>{current?.name ?? settings.primary_model}</span>
      </button>
      {open && (
        <>
          <div
            className="fixed inset-0 z-10"
            onClick={() => setOpen(false)}
            onKeyDown={() => {}}
            role="button"
            tabIndex={0}
            aria-label="Close"
          />
          <div className="absolute right-0 top-full z-20 mt-1 w-56 rounded-lg border border-zinc-200 bg-white py-1 shadow-lg dark:border-zinc-700 dark:bg-zinc-800">
            {settings.available_models.map((m) => (
              <button
                key={m.id}
                type="button"
                onClick={() => handleChange(m.id)}
                className={`block w-full px-4 py-2 text-left text-sm hover:bg-zinc-100 dark:hover:bg-zinc-700 ${
                  m.id === settings.primary_model ? "font-medium" : ""
                }`}
              >
                {m.name} ({m.provider})
              </button>
            ))}
          </div>
        </>
      )}
    </div>
  );
}

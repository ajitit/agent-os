"use client";

import React from "react";

import { FormEvent, useEffect, useState } from "react";
import { api, type Agent } from "@/lib/api";

type LikertValue = 1 | 2 | 3 | 4 | 5;

type EvaluationFormState = {
  agentId: string;
  version: string;
  modelProvider: string;
  taskCategory: string;
  taskSuccess: LikertValue;
  hallucinationRate: LikertValue;
  toolCallAccuracy: LikertValue;
  intentResolution: LikertValue;
  notes: string;
};

const MODEL_PROVIDERS = [
  "OpenAI - GPT-4o",
  "OpenAI - GPT-4 Turbo",
  "Anthropic - Claude 3.5 Sonnet",
  "Anthropic - Claude 3.5 Haiku",
  "Google - Gemini 1.5 Pro",
  "Local / Custom",
];

const TASK_CATEGORIES = [
  "Customer Support",
  "Code Generation",
  "Data Analysis",
  "Content Writing",
  "Agentic Workflow",
  "Tool Automation",
  "Other",
];

const DEFAULT_FORM: EvaluationFormState = {
  agentId: "",
  version: "v1",
  modelProvider: MODEL_PROVIDERS[0],
  taskCategory: TASK_CATEGORIES[0],
  taskSuccess: 3,
  hallucinationRate: 3,
  toolCallAccuracy: 3,
  intentResolution: 3,
  notes: "",
};

export default function EvaluationEntryPage() {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [form, setForm] = useState<EvaluationFormState>(DEFAULT_FORM);
  const [loadingAgents, setLoadingAgents] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [toast, setToast] = useState<string | null>(null);

  useEffect(() => {
    api
      .get<Agent[]>("/agents")
      .then((data) => setAgents(data))
      .catch(() => {
        setAgents([]);
      })
      .finally(() => setLoadingAgents(false));
  }, []);

  const updateForm = <K extends keyof EvaluationFormState>(key: K, value: EvaluationFormState[K]) => {
    setForm((prev) => ({ ...prev, [key]: value }));
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!form.agentId) {
      setError("Please select an Agent ID.");
      return;
    }
    setSubmitting(true);
    setError(null);

    try {
      await api.post("/evaluations", {
        agent_id: form.agentId,
        version: form.version,
        model_provider: form.modelProvider,
        task_category: form.taskCategory,
        metrics: {
          task_success_rate: form.taskSuccess,
          hallucination_rate: form.hallucinationRate,
          tool_call_accuracy: form.toolCallAccuracy,
          intent_resolution: form.intentResolution,
        },
        notes: form.notes || undefined,
      });

      setForm(DEFAULT_FORM);
      setToast("Evaluation submitted successfully.");
      setTimeout(() => setToast(null), 4000);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Failed to submit evaluation.";
      setError(message);
    } finally {
      setSubmitting(false);
    }
  };

  const likertControl = (label: string, value: LikertValue, onChange: (next: LikertValue) => void, helper?: string) => (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-zinc-900 dark:text-zinc-100">{label}</p>
          {helper ? (
            <p className="text-xs text-zinc-500 dark:text-zinc-400">{helper}</p>
          ) : null}
        </div>
        <span className="text-xs font-medium text-zinc-600 dark:text-zinc-300">{value} / 5</span>
      </div>
      <input
        type="range"
        min={1}
        max={5}
        step={1}
        value={value}
        onChange={(event) => onChange(Number(event.target.value) as LikertValue)}
        className="w-full accent-zinc-900 dark:accent-zinc-100"
      />
      <div className="flex justify-between text-[11px] text-zinc-500 dark:text-zinc-400">
        <span>1</span>
        <span>2</span>
        <span>3</span>
        <span>4</span>
        <span>5</span>
      </div>
    </div>
  );

  return (
    <div className="mx-auto max-w-4xl px-6 py-8">
      {toast ? (
        <div className="fixed right-4 top-20 z-50 rounded-lg bg-emerald-600 px-4 py-3 text-sm text-white shadow-lg">
          {toast}
        </div>
      ) : null}

      <div className="mb-6">
        <h1 className="text-2xl font-bold text-zinc-900 dark:text-zinc-100">Agent Evaluation Entry</h1>
        <p className="mt-1 text-sm text-zinc-600 dark:text-zinc-400">
          Capture structured evaluation data for a single agent run, including core quality metrics and qualitative notes.
        </p>
      </div>

      <form
        onSubmit={handleSubmit}
        className="space-y-8 rounded-xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900"
      >
        <section className="grid gap-4 md:grid-cols-2">
          <div className="space-y-1">
            <label className="text-sm font-medium text-zinc-900 dark:text-zinc-100">Agent ID</label>
            <select
              value={form.agentId}
              onChange={(event) => updateForm("agentId", event.target.value)}
              className="w-full rounded-lg border border-zinc-200 bg-white px-3 py-2 text-sm dark:border-zinc-700 dark:bg-zinc-800 dark:text-zinc-100"
            >
              <option value="">{loadingAgents ? "Loading agents..." : "Select an agent"}</option>
              {agents.map((agent) => (
                <option key={agent.id} value={agent.id}>
                  {agent.name} ({agent.id})
                </option>
              ))}
            </select>
          </div>

          <div className="space-y-1">
            <label className="text-sm font-medium text-zinc-900 dark:text-zinc-100">Version</label>
            <input
              type="text"
              value={form.version}
              onChange={(event) => updateForm("version", event.target.value)}
              placeholder="e.g. v1, v1.2.3"
              className="w-full rounded-lg border border-zinc-200 bg-white px-3 py-2 text-sm dark:border-zinc-700 dark:bg-zinc-800 dark:text-zinc-100"
            />
          </div>

          <div className="space-y-1">
            <label className="text-sm font-medium text-zinc-900 dark:text-zinc-100">Model Provider</label>
            <select
              value={form.modelProvider}
              onChange={(event) => updateForm("modelProvider", event.target.value)}
              className="w-full rounded-lg border border-zinc-200 bg-white px-3 py-2 text-sm dark:border-zinc-700 dark:bg-zinc-800 dark:text-zinc-100"
            >
              {MODEL_PROVIDERS.map((provider) => (
                <option key={provider} value={provider}>
                  {provider}
                </option>
              ))}
            </select>
          </div>

          <div className="space-y-1">
            <label className="text-sm font-medium text-zinc-900 dark:text-zinc-100">Task Category</label>
            <select
              value={form.taskCategory}
              onChange={(event) => updateForm("taskCategory", event.target.value)}
              className="w-full rounded-lg border border-zinc-200 bg-white px-3 py-2 text-sm dark:border-zinc-700 dark:bg-zinc-800 dark:text-zinc-100"
            >
              {TASK_CATEGORIES.map((category) => (
                <option key={category} value={category}>
                  {category}
                </option>
              ))}
            </select>
          </div>
        </section>

        <section className="grid gap-6 md:grid-cols-2">
          {likertControl(
            "Task Success Rate",
            form.taskSuccess,
            (next) => updateForm("taskSuccess", next),
            "Did the agent complete the objective?"
          )}
          {likertControl(
            "Hallucination Rate",
            form.hallucinationRate,
            (next) => updateForm("hallucinationRate", next),
            "Was the output factually grounded?"
          )}
          {likertControl(
            "Tool Call Accuracy",
            form.toolCallAccuracy,
            (next) => updateForm("toolCallAccuracy", next),
            "Did it use the correct tools with the right arguments?"
          )}
          {likertControl(
            "Intent Resolution",
            form.intentResolution,
            (next) => updateForm("intentResolution", next),
            "Did it correctly interpret the user's goal?"
          )}
        </section>

        <section className="space-y-2">
          <label className="text-sm font-medium text-zinc-900 dark:text-zinc-100">Reasoning / Notes</label>
          <textarea
            value={form.notes}
            onChange={(event) => updateForm("notes", event.target.value)}
            rows={4}
            placeholder="Explain why you chose these scores, reference any traces or edge cases observed..."
            className="w-full rounded-lg border border-zinc-200 bg-white px-3 py-2 text-sm dark:border-zinc-700 dark:bg-zinc-800 dark:text-zinc-100"
          />
        </section>

        {error ? (
          <div className="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700 dark:border-red-900/60 dark:bg-red-950/40 dark:text-red-300">
            {error}
          </div>
        ) : null}

        <div className="flex items-center justify-end gap-3">
          <button
            type="reset"
            onClick={() => {
              setForm(DEFAULT_FORM);
              setError(null);
            }}
            className="rounded-lg px-4 py-2 text-sm text-zinc-600 hover:bg-zinc-100 dark:text-zinc-300 dark:hover:bg-zinc-800"
          >
            Clear
          </button>
          <button
            type="submit"
            disabled={submitting}
            className="rounded-lg bg-zinc-900 px-4 py-2 text-sm font-medium text-white shadow-sm transition hover:bg-zinc-800 disabled:cursor-not-allowed disabled:opacity-60 dark:bg-zinc-100 dark:text-zinc-900 dark:hover:bg-zinc-200"
          >
            {submitting ? "Submitting..." : "Submit Evaluation"}
          </button>
        </div>
      </form>
    </div>
  );
}


/**
 * File: page.tsx
 * 
 * Purpose:
 * Displays a comprehensive analytics dashboard visualizing agent and model performance
 * metrics over time.
 * 
 * Key Functionalities:
 * - Render top-level summary statistics (Success rate, latency, token costs)
 * - Display comparative charts using Recharts (Radar traits, time-series trends)
 * - Render an Intent Confusion Matrix heat-map using HTML tables
 * - Provide an interactive evaluation log list showing individual runs
 * - Support toggling the primary provider and comparative overlay
 * 
 * Inputs:
 * - Currently uses mocked analytics/evaluation data for visualization
 * 
 * Outputs:
 * - React page component for `/analytics`
 * 
 * Interacting Files / Modules:
 * - None
 */
"use client";

import { useMemo, useState } from "react";
import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  PolarAngleAxis,
  PolarGrid,
  PolarRadiusAxis,
  Radar,
  RadarChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

type ProviderKey = "gpt4o" | "claude35";

type EvaluationRadarMetric = {
  metric: string;
  gpt4o: number;
  claude35: number;
};

type TrendPoint = {
  day: string;
  gpt4o: number;
  claude35: number;
};

type ConfusionCell = {
  actual: string;
  predicted: string;
  count: number;
};

type EvaluationRow = {
  id: string;
  timestamp: string;
  agentId: string;
  provider: string;
  taskCategory: string;
  success: number;
  latencyMs: number;
  totalTokens: number;
  traceUrl?: string;
};

const radarData: EvaluationRadarMetric[] = [
  { metric: "Accuracy", gpt4o: 4.4, claude35: 4.6 },
  { metric: "Speed", gpt4o: 4.1, claude35: 3.9 },
  { metric: "Tool Use", gpt4o: 4.3, claude35: 4.2 },
  { metric: "Safety", gpt4o: 4.7, claude35: 4.8 },
  { metric: "Coherence", gpt4o: 4.5, claude35: 4.6 },
];

const trendData: TrendPoint[] = Array.from({ length: 30 }).map((_, index) => {
  const day = `D${index + 1}`;
  return {
    day,
    gpt4o: 82 + Math.sin(index / 4) * 6 + (index % 5) * 0.5,
    claude35: 84 + Math.cos(index / 5) * 5 + ((index + 2) % 7) * 0.4,
  };
});

const confusionMatrixLabels = ["Q&A", "Code", "Analysis", "Routing"];

const confusionMatrix: ConfusionCell[] = [
  { actual: "Q&A", predicted: "Q&A", count: 128 },
  { actual: "Q&A", predicted: "Code", count: 6 },
  { actual: "Q&A", predicted: "Analysis", count: 9 },
  { actual: "Q&A", predicted: "Routing", count: 3 },
  { actual: "Code", predicted: "Q&A", count: 5 },
  { actual: "Code", predicted: "Code", count: 97 },
  { actual: "Code", predicted: "Analysis", count: 11 },
  { actual: "Code", predicted: "Routing", count: 2 },
  { actual: "Analysis", predicted: "Q&A", count: 7 },
  { actual: "Analysis", predicted: "Code", count: 8 },
  { actual: "Analysis", predicted: "Analysis", count: 112 },
  { actual: "Analysis", predicted: "Routing", count: 4 },
  { actual: "Routing", predicted: "Q&A", count: 3 },
  { actual: "Routing", predicted: "Code", count: 2 },
  { actual: "Routing", predicted: "Analysis", count: 5 },
  { actual: "Routing", predicted: "Routing", count: 76 },
];

const evaluationRows: EvaluationRow[] = [
  {
    id: "run_01",
    timestamp: "2026-03-10T08:31:00Z",
    agentId: "support-bot",
    provider: "GPT-4o",
    taskCategory: "Customer Support",
    success: 5,
    latencyMs: 2310,
    totalTokens: 1874,
  },
  {
    id: "run_02",
    timestamp: "2026-03-10T08:18:00Z",
    agentId: "code-reviewer",
    provider: "Claude 3.5 Sonnet",
    taskCategory: "Code Generation",
    success: 4,
    latencyMs: 2980,
    totalTokens: 2640,
  },
  {
    id: "run_03",
    timestamp: "2026-03-09T21:03:00Z",
    agentId: "analytics-agent",
    provider: "GPT-4o",
    taskCategory: "Data Analysis",
    success: 4,
    latencyMs: 1840,
    totalTokens: 1420,
  },
  {
    id: "run_04",
    timestamp: "2026-03-09T20:44:00Z",
    agentId: "routing-orchestrator",
    provider: "Claude 3.5 Sonnet",
    taskCategory: "Agentic Workflow",
    success: 5,
    latencyMs: 2560,
    totalTokens: 3210,
  },
];

const formatPercent = (value: number) => `${value.toFixed(1)}%`;

export default function PerformanceAnalyticsPage() {
  const [comparisonEnabled, setComparisonEnabled] = useState(true);
  const [primaryProvider, setPrimaryProvider] = useState<ProviderKey>("gpt4o");

  const successRate = useMemo(() => {
    const values = trendData.map((point) => point[primaryProvider]);
    const average = values.reduce((sum, value) => sum + value, 0) / values.length;
    return average;
  }, [primaryProvider]);

  const medianLatency = useMemo(() => {
    const values = evaluationRows.map((run) => run.latencyMs).sort((a, b) => a - b);
    const middle = Math.floor(values.length / 2);
    if (values.length % 2 === 0) {
      return (values[middle - 1] + values[middle]) / 2;
    }
    return values[middle];
  }, []);

  const totalTokenCost = useMemo(() => {
    return evaluationRows.reduce((sum, run) => sum + run.totalTokens, 0);
  }, []);

  const maxConfusion = Math.max(...confusionMatrix.map((cell) => cell.count));

  const colorForCell = (value: number) => {
    const ratio = value / maxConfusion;
    const intensity = Math.round(30 + ratio * 70);
    return `rgb(37 99 235 / ${intensity}%)`;
  };

  return (
    <div className="mx-auto max-w-6xl px-6 py-8">
      <div className="mb-6 flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-zinc-900 dark:text-zinc-100">Performance Analytics</h1>
          <p className="mt-1 text-sm text-zinc-600 dark:text-zinc-400">
            Visualize evaluation metrics over time to spot regressions, model drift, and provider-level ROI.
          </p>
        </div>
        <div className="flex items-center gap-3 rounded-full border border-zinc-200 bg-white px-3 py-2 text-xs shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
          <span className="mr-1 text-zinc-600 dark:text-zinc-300">Primary model</span>
          <button
            type="button"
            onClick={() => setPrimaryProvider("gpt4o")}
            className={
              primaryProvider === "gpt4o"
                ? "rounded-full bg-zinc-900 px-3 py-1 text-white dark:bg-zinc-100 dark:text-zinc-900"
                : "rounded-full px-3 py-1 text-zinc-600 hover:bg-zinc-100 dark:text-zinc-300 dark:hover:bg-zinc-800"
            }
          >
            GPT-4o
          </button>
          <button
            type="button"
            onClick={() => setPrimaryProvider("claude35")}
            className={
              primaryProvider === "claude35"
                ? "rounded-full bg-zinc-900 px-3 py-1 text-white dark:bg-zinc-100 dark:text-zinc-900"
                : "rounded-full px-3 py-1 text-zinc-600 hover:bg-zinc-100 dark:text-zinc-300 dark:hover:bg-zinc-800"
            }
          >
            Claude 3.5
          </button>
          <div className="ml-3 flex items-center gap-1">
            <label className="text-zinc-600 dark:text-zinc-300">Comparison</label>
            <button
              type="button"
              onClick={() => setComparisonEnabled((current) => !current)}
              className={`relative inline-flex h-5 w-9 items-center rounded-full transition ${
                comparisonEnabled ? "bg-emerald-500" : "bg-zinc-400 dark:bg-zinc-600"
              }`}
            >
              <span
                className={`inline-block h-4 w-4 transform rounded-full bg-white transition ${
                  comparisonEnabled ? "translate-x-4" : "translate-x-1"
                }`}
              />
            </button>
          </div>
        </div>
      </div>

      <section className="mb-8 grid gap-4 md:grid-cols-3">
        <div className="rounded-xl border border-zinc-200 bg-white p-4 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
          <p className="text-xs font-medium uppercase tracking-wide text-zinc-500 dark:text-zinc-400">
            Avg. Success Rate (30d)
          </p>
          <p className="mt-2 text-2xl font-semibold text-zinc-900 dark:text-zinc-100">
            {formatPercent(successRate)}
          </p>
          <p className="mt-1 text-xs text-zinc-500 dark:text-zinc-400">
            Across all {primaryProvider === "gpt4o" ? "GPT-4o" : "Claude 3.5"} evaluations
          </p>
        </div>

        <div className="rounded-xl border border-zinc-200 bg-white p-4 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
          <p className="text-xs font-medium uppercase tracking-wide text-zinc-500 dark:text-zinc-400">
            Median Latency
          </p>
          <p className="mt-2 text-2xl font-semibold text-zinc-900 dark:text-zinc-100">
            {(medianLatency / 1000).toFixed(2)}s
          </p>
          <p className="mt-1 text-xs text-zinc-500 dark:text-zinc-400">
            P50 latency across recent evaluation runs
          </p>
        </div>

        <div className="rounded-xl border border-zinc-200 bg-white p-4 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
          <p className="text-xs font-medium uppercase tracking-wide text-zinc-500 dark:text-zinc-400">
            Total Token Cost (sample)
          </p>
          <p className="mt-2 text-2xl font-semibold text-zinc-900 dark:text-zinc-100">
            {totalTokenCost.toLocaleString()}
          </p>
          <p className="mt-1 text-xs text-zinc-500 dark:text-zinc-400">Tokens across recent evaluation runs</p>
        </div>
      </section>

      <section className="grid gap-6 md:grid-cols-2">
        <div className="rounded-xl border border-zinc-200 bg-white p-4 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
          <div className="mb-3 flex items-center justify-between">
            <div>
              <h2 className="text-sm font-semibold text-zinc-900 dark:text-zinc-100">Evaluation Matrix</h2>
              <p className="text-xs text-zinc-500 dark:text-zinc-400">
                Accuracy, speed, tool use, safety, and coherence profile.
              </p>
            </div>
          </div>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart data={radarData}>
                <PolarGrid />
                <PolarAngleAxis dataKey="metric" />
                <PolarRadiusAxis angle={45} domain={[0, 5]} tick={{ fontSize: 10 }} />
                <Radar
                  name="GPT-4o"
                  dataKey="gpt4o"
                  stroke="#0f172a"
                  fill="#0f172a"
                  fillOpacity={0.3}
                />
                {comparisonEnabled ? (
                  <Radar
                    name="Claude 3.5"
                    dataKey="claude35"
                    stroke="#22c55e"
                    fill="#22c55e"
                    fillOpacity={0.3}
                  />
                ) : null}
                <Legend />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="rounded-xl border border-zinc-200 bg-white p-4 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
          <div className="mb-3 flex items-center justify-between">
            <div>
              <h2 className="text-sm font-semibold text-zinc-900 dark:text-zinc-100">Intent Confusion Matrix</h2>
              <p className="text-xs text-zinc-500 dark:text-zinc-400">
                Predicted vs. actual intent classes for routing and classification.
              </p>
            </div>
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full border-collapse text-xs">
              <thead>
                <tr>
                  <th className="px-2 py-1 text-left text-zinc-500 dark:text-zinc-400">Actual \\ Predicted</th>
                  {confusionMatrixLabels.map((label) => (
                    <th key={label} className="px-2 py-1 text-center text-zinc-500 dark:text-zinc-400">
                      {label}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {confusionMatrixLabels.map((actual) => (
                  <tr key={actual}>
                    <td className="px-2 py-1 text-left text-zinc-600 dark:text-zinc-300">{actual}</td>
                    {confusionMatrixLabels.map((predicted) => {
                      const cell = confusionMatrix.find(
                        (entry) => entry.actual === actual && entry.predicted === predicted
                      );
                      const value = cell?.count ?? 0;
                      const backgroundColor = value > 0 ? colorForCell(value) : "transparent";
                      return (
                        <td
                          key={`${actual}-${predicted}`}
                          className="px-2 py-1 text-center text-[11px] text-zinc-50"
                          style={{ backgroundColor }}
                        >
                          {value || ""}
                        </td>
                      );
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </section>

      <section className="mt-6 rounded-xl border border-zinc-200 bg-white p-4 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
        <div className="mb-3 flex items-center justify-between">
          <div>
            <h2 className="text-sm font-semibold text-zinc-900 dark:text-zinc-100">
              30-Day Performance Trend
            </h2>
            <p className="text-xs text-zinc-500 dark:text-zinc-400">
              Monitor success rate and detect performance drift over time.
            </p>
          </div>
        </div>
        <div className="h-72">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={trendData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis dataKey="day" tick={{ fontSize: 10 }} />
              <YAxis domain={[70, 100]} tickFormatter={(value) => `${value}%`} tick={{ fontSize: 10 }} />
              <Tooltip formatter={(value: number) => `${value.toFixed(1)}%`} />
              <Legend />
              <Line
                type="monotone"
                dataKey="gpt4o"
                name="GPT-4o"
                stroke="#0f172a"
                strokeWidth={2}
                dot={false}
              />
              {comparisonEnabled ? (
                <Line
                  type="monotone"
                  dataKey="claude35"
                  name="Claude 3.5"
                  stroke="#22c55e"
                  strokeWidth={2}
                  dot={false}
                />
              ) : null}
            </LineChart>
          </ResponsiveContainer>
        </div>
      </section>

      <section className="mt-6 rounded-xl border border-zinc-200 bg-white p-4 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
        <div className="mb-3 flex items-center justify-between">
          <div>
            <h2 className="text-sm font-semibold text-zinc-900 dark:text-zinc-100">Evaluation Log</h2>
            <p className="text-xs text-zinc-500 dark:text-zinc-400">
              Individual evaluation runs with quick access to traces for debugging.
            </p>
          </div>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full border-collapse text-xs">
            <thead>
              <tr className="border-b border-zinc-200 dark:border-zinc-800">
                <th className="px-3 py-2 text-left font-medium text-zinc-500 dark:text-zinc-400">
                  Timestamp
                </th>
                <th className="px-3 py-2 text-left font-medium text-zinc-500 dark:text-zinc-400">Agent</th>
                <th className="px-3 py-2 text-left font-medium text-zinc-500 dark:text-zinc-400">Provider</th>
                <th className="px-3 py-2 text-left font-medium text-zinc-500 dark:text-zinc-400">Category</th>
                <th className="px-3 py-2 text-right font-medium text-zinc-500 dark:text-zinc-400">Success</th>
                <th className="px-3 py-2 text-right font-medium text-zinc-500 dark:text-zinc-400">Latency</th>
                <th className="px-3 py-2 text-right font-medium text-zinc-500 dark:text-zinc-400">Tokens</th>
                <th className="px-3 py-2 text-right font-medium text-zinc-500 dark:text-zinc-400">Trace</th>
              </tr>
            </thead>
            <tbody>
              {evaluationRows.map((run) => (
                <tr key={run.id} className="border-b border-zinc-100 last:border-0 dark:border-zinc-800">
                  <td className="px-3 py-2 text-zinc-700 dark:text-zinc-200">
                    {new Date(run.timestamp).toLocaleString()}
                  </td>
                  <td className="px-3 py-2 text-zinc-700 dark:text-zinc-200">{run.agentId}</td>
                  <td className="px-3 py-2 text-zinc-700 dark:text-zinc-200">{run.provider}</td>
                  <td className="px-3 py-2 text-zinc-600 dark:text-zinc-300">{run.taskCategory}</td>
                  <td className="px-3 py-2 text-right text-zinc-700 dark:text-zinc-200">{run.success}/5</td>
                  <td className="px-3 py-2 text-right text-zinc-700 dark:text-zinc-200">
                    {(run.latencyMs / 1000).toFixed(2)}s
                  </td>
                  <td className="px-3 py-2 text-right text-zinc-700 dark:text-zinc-200">
                    {run.totalTokens.toLocaleString()}
                  </td>
                  <td className="px-3 py-2 text-right">
                    <button
                      type="button"
                      className="text-xs font-medium text-zinc-900 underline-offset-2 hover:underline dark:text-zinc-100"
                    >
                      View trace
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}


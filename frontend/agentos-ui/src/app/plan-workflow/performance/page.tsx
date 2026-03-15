/**
 * File: plan-workflow/performance/page.tsx
 *
 * Performance Review (Optional) — evaluate workflow success,
 * view agent performance metrics, and receive optimization suggestions.
 */
export default function PerformanceReviewPage() {
  return (
    <div className="mx-auto max-w-7xl px-6 py-12">
      <div className="mb-8">
        <div className="inline-flex items-center gap-2 bg-zinc-800/60 border border-zinc-700 rounded-full px-3 py-1 text-xs text-zinc-400 mb-4">
          Optional
        </div>
        <h1 className="text-3xl font-bold text-zinc-100 tracking-tight mb-2">
          Performance Review
        </h1>
        <p className="text-zinc-400">
          Evaluate workflow success, review agent performance metrics, and act on optimization suggestions.
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-3">
        {[
          {
            icon: "✅",
            title: "Workflow Success",
            description: "Evaluate whether workflows met their defined goals and completion criteria.",
          },
          {
            icon: "📈",
            title: "Agent Metrics",
            description: "Per-agent latency, accuracy, task completion rates, and error breakdowns.",
          },
          {
            icon: "💡",
            title: "Optimization Suggestions",
            description: "AI-generated recommendations to improve agent configuration and workflow design.",
          },
        ].map(({ icon, title, description }) => (
          <div
            key={title}
            className="rounded-2xl border border-zinc-800 bg-zinc-900/40 p-6"
          >
            <div className="mb-3 text-3xl">{icon}</div>
            <h2 className="text-base font-bold text-zinc-100 mb-2">{title}</h2>
            <p className="text-sm text-zinc-400 leading-relaxed">{description}</p>
          </div>
        ))}
      </div>

      <div className="mt-10 rounded-2xl border border-dashed border-zinc-700 bg-zinc-900/20 p-10 text-center">
        <p className="text-zinc-500 text-sm">No performance data available. Complete a workflow run to generate metrics.</p>
      </div>
    </div>
  );
}

/**
 * File: plan-workflow/output/page.tsx
 *
 * Output / Feedback — view workflow results, provide feedback,
 * and trigger iterative workflow improvement.
 */
export default function OutputFeedbackPage() {
  return (
    <div className="mx-auto max-w-7xl px-6 py-12">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-zinc-100 tracking-tight mb-2">
          Output / Feedback
        </h1>
        <p className="text-zinc-400">
          View workflow results, provide feedback, and trigger iterative improvements.
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-3">
        {[
          {
            icon: "📤",
            title: "Workflow Results",
            description: "Review the outputs produced by recent workflow executions.",
          },
          {
            icon: "💬",
            title: "Provide Feedback",
            description: "Rate results and add structured feedback to guide agent improvement.",
          },
          {
            icon: "🔁",
            title: "Iterative Improvement",
            description: "Trigger re-runs with updated context or revised agent instructions.",
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
        <p className="text-zinc-500 text-sm">No workflow output yet. Run a workflow to see results here.</p>
      </div>
    </div>
  );
}

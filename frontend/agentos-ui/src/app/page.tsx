import Link from "next/link";

export default function Home() {
  return (
    <div className="min-h-screen bg-zinc-50 dark:bg-zinc-950">
      <nav className="border-b border-zinc-200 bg-white px-6 py-4 dark:border-zinc-800 dark:bg-zinc-900">
        <div className="mx-auto flex max-w-6xl items-center justify-between">
          <Link href="/" className="text-xl font-semibold text-zinc-900 dark:text-zinc-100">
            AgentOS
          </Link>
          <div className="flex gap-6">
            <Link
              href="/admin/agents"
              className="text-zinc-600 hover:text-zinc-900 dark:text-zinc-400 dark:hover:text-zinc-100"
            >
              Agents
            </Link>
            <Link
              href="/admin/mcp"
              className="text-zinc-600 hover:text-zinc-900 dark:text-zinc-400 dark:hover:text-zinc-100"
            >
              MCP Services
            </Link>
            <Link
              href="/chat"
              className="rounded-lg bg-zinc-900 px-4 py-2 text-sm font-medium text-white dark:bg-zinc-100 dark:text-zinc-900"
            >
              Chat
            </Link>
          </div>
        </div>
      </nav>
      <main className="mx-auto max-w-6xl px-6 py-16">
        <h1 className="text-3xl font-bold text-zinc-900 dark:text-zinc-100">
          Enterprise Multi-Agent AI Platform
        </h1>
        <p className="mt-4 max-w-2xl text-lg text-zinc-600 dark:text-zinc-400">
          Orchestrate autonomous workflows with crews, agents, MCP tools, and human-in-the-loop.
        </p>
        <div className="mt-12 grid gap-6 sm:grid-cols-3">
          <Link
            href="/admin/agents"
            className="rounded-xl border border-zinc-200 bg-white p-6 shadow-sm transition hover:border-zinc-300 dark:border-zinc-800 dark:bg-zinc-900 dark:hover:border-zinc-700"
          >
            <h2 className="text-lg font-semibold">Agent Management</h2>
            <p className="mt-2 text-sm text-zinc-600 dark:text-zinc-400">
              Create, edit, and configure AI agents with system prompts and tools.
            </p>
          </Link>
          <Link
            href="/admin/mcp"
            className="rounded-xl border border-zinc-200 bg-white p-6 shadow-sm transition hover:border-zinc-300 dark:border-zinc-800 dark:bg-zinc-900 dark:hover:border-zinc-700"
          >
            <h2 className="text-lg font-semibold">MCP Service Marketplace</h2>
            <p className="mt-2 text-sm text-zinc-600 dark:text-zinc-400">
              Manage MCP servers, tools, and resources.
            </p>
          </Link>
          <Link
            href="/chat"
            className="rounded-xl border border-zinc-200 bg-white p-6 shadow-sm transition hover:border-zinc-300 dark:border-zinc-800 dark:bg-zinc-900 dark:hover:border-zinc-700"
          >
            <h2 className="text-lg font-semibold">Chat Interface</h2>
            <p className="mt-2 text-sm text-zinc-600 dark:text-zinc-400">
              Interact with agents and see tool executions in real time.
            </p>
          </Link>
        </div>
      </main>
    </div>
  );
}

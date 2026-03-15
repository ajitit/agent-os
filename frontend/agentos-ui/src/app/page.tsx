/**
 * File: page.tsx — Vishwakarma Dashboard
 *
 * Landing page reflecting the Agentic AI Platform navigation structure:
 *   Chat · Plan & Workflow · Agent Management · Agent Capabilities ·
 *   Tools & Integrations · Insights & Governance · Settings
 */
import Link from "next/link";

interface DashCard {
  href: string;
  icon: string;
  title: string;
  description: string;
  badge?: string;
  color: string;
}

const PRIMARY_CARDS: DashCard[] = [
  {
    href: "/chat",
    icon: "💬",
    title: "Chat",
    description:
      "Conversational interface to interact with agents and agent groups. View responses, context, and execution logs in real time.",
    badge: "Live",
    color: "from-violet-800/40 to-indigo-900/40",
  },
  {
    href: "/plans",
    icon: "📋",
    title: "Plan & Workflow",
    description:
      "Define execution strategies, break tasks into steps, build orchestration pipelines, and review output with iterative feedback.",
    badge: "New",
    color: "from-purple-800/40 to-violet-900/40",
  },
  {
    href: "/admin/agents",
    icon: "🤖",
    title: "Agent Management",
    description:
      "Full lifecycle management for agents. Add, view, update, and delete agents. Assign multi-select capabilities per agent.",
    color: "from-slate-700/40 to-zinc-800/40",
  },
  {
    href: "/registry/skills",
    icon: "⚡",
    title: "Agent Capabilities",
    description:
      "Reusable capability library: Skills (task abilities), Models (LLM & multimodal), and Knowledge Graphs for agent reasoning context.",
    badge: "New",
    color: "from-blue-800/40 to-cyan-900/40",
  },
];

const SECONDARY_CARDS: DashCard[] = [
  {
    href: "/registry/mcp-servers",
    icon: "🔧",
    title: "Tools & Integrations",
    description:
      "MCP Server tool-hosting layer with Data Sources (databases, data lakes, storage) and Remote APIs (SaaS, enterprise systems).",
    color: "from-teal-800/40 to-emerald-900/40",
  },
  {
    href: "/analytics",
    icon: "📊",
    title: "Insights & Governance",
    description:
      "Analytics on usage and performance, full observability traces and logs, and an immutable audit record for compliance tracking.",
    color: "from-sky-800/40 to-blue-900/40",
  },
  {
    href: "/settings/preferences",
    icon: "⚙️",
    title: "Settings",
    description:
      "Configure your profile, access roles, UI preferences, notification settings, API keys, and developer integrations.",
    color: "from-zinc-700/40 to-zinc-800/40",
  },
  {
    href: "/marketplace",
    icon: "🛒",
    title: "Marketplace",
    description:
      "Browse and install Skills, Models, and Tools. Pre-seeded with LLMs, built-in tools, and a publishable skill registry.",
    badge: "New",
    color: "from-amber-800/40 to-orange-900/40",
  },
];

function Card({ card }: { card: DashCard }) {
  return (
    <Link
      href={card.href}
      className={`group relative rounded-2xl border border-zinc-800 bg-gradient-to-br ${card.color} p-6 transition-all hover:border-zinc-600 hover:shadow-lg hover:shadow-zinc-900/50 hover:-translate-y-0.5`}
    >
      {card.badge && (
        <span className="absolute right-4 top-4 rounded-full bg-violet-700 px-2 py-0.5 text-xs font-semibold text-white">
          {card.badge}
        </span>
      )}
      <div className="mb-3 text-3xl">{card.icon}</div>
      <h2 className="text-base font-bold text-zinc-100 mb-2">{card.title}</h2>
      <p className="text-sm text-zinc-400 leading-relaxed">{card.description}</p>
      <div className="mt-4 text-xs text-zinc-600 group-hover:text-violet-400 transition-colors">
        Open →
      </div>
    </Link>
  );
}

export default function Home() {
  return (
    <div className="mx-auto max-w-7xl px-6 py-12">
      {/* Hero */}
      <div className="mb-12">
        <div className="inline-flex items-center gap-2 bg-violet-950/50 border border-violet-800/50 rounded-full px-4 py-1.5 text-xs text-violet-300 mb-6">
          <span className="w-1.5 h-1.5 bg-violet-400 rounded-full animate-pulse" />
          Enterprise Multi-Agent AI Platform · v1.0
        </div>
        <h1 className="text-4xl font-bold text-zinc-100 tracking-tight mb-4">
          Agentic AI Platform
        </h1>
        <p className="max-w-2xl text-lg text-zinc-400 leading-relaxed">
          Orchestrate autonomous agents with supervisor planning, multi-agent workflows,
          a reusable capability library, and full observability and governance.
        </p>
        <div className="mt-6 flex flex-wrap gap-3">
          <Link
            href="/chat"
            className="rounded-xl bg-violet-700 hover:bg-violet-600 px-6 py-3 text-sm font-semibold text-white transition-colors"
          >
            Start Chatting →
          </Link>
          <Link
            href="/plans"
            className="rounded-xl border border-zinc-700 hover:border-zinc-500 px-6 py-3 text-sm font-medium text-zinc-300 hover:text-white transition-colors"
          >
            View Plans
          </Link>
          <Link
            href="/workflows"
            className="rounded-xl border border-zinc-700 hover:border-zinc-500 px-6 py-3 text-sm font-medium text-zinc-300 hover:text-white transition-colors"
          >
            Build Workflows
          </Link>
        </div>
      </div>

      {/* Stats strip */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-10">
        {[
          { label: "Pre-seeded Models", value: "7" },
          { label: "Built-in Tools", value: "8" },
          { label: "Pipeline Stages", value: "9" },
          { label: "API Endpoints", value: "80+" },
        ].map(({ label, value }) => (
          <div key={label} className="rounded-xl border border-zinc-800 bg-zinc-900/40 p-4 text-center">
            <div className="text-2xl font-bold text-white">{value}</div>
            <div className="text-xs text-zinc-500 mt-0.5">{label}</div>
          </div>
        ))}
      </div>

      {/* Primary features */}
      <div className="mb-6">
        <h2 className="text-xs font-semibold text-zinc-500 uppercase tracking-widest mb-4">Core</h2>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {PRIMARY_CARDS.map((card) => (
            <Card key={card.href} card={card} />
          ))}
        </div>
      </div>

      {/* Secondary features */}
      <div>
        <h2 className="text-xs font-semibold text-zinc-500 uppercase tracking-widest mb-4">Platform</h2>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {SECONDARY_CARDS.map((card) => (
            <Card key={card.href} card={card} />
          ))}
        </div>
      </div>
    </div>
  );
}

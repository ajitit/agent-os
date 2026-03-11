/**
 * File: page.tsx — AgentOS Dashboard / Landing Page
 *
 * Shows all platform capabilities as a navigable card grid.
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
    title: "Chat Interface",
    description: "Talk to the Supervisor Agent. It decomposes your goal into a plan, routes tasks to specialised sub-agents, and streams results in real time.",
    badge: "Live",
    color: "from-violet-800/40 to-indigo-900/40",
  },
  {
    href: "/plans",
    icon: "🗺️",
    title: "Supervisor Plans",
    description: "View every auto-generated execution plan. Inspect goal decomposition, approve or reject plans, and track task-level progress live.",
    badge: "New",
    color: "from-purple-800/40 to-violet-900/40",
  },
  {
    href: "/workflows",
    icon: "🎨",
    title: "Workflow Builder",
    description: "Drag-and-drop graph editor for designing, deploying, and testing multi-agent pipelines with visual node connections.",
    badge: "New",
    color: "from-blue-800/40 to-cyan-900/40",
  },
  {
    href: "/pipeline",
    icon: "⚗️",
    title: "Input Pipeline",
    description: "9-stage input processing: filter → extract → map → mask → route → classify → aggregate → result → review.",
    color: "from-teal-800/40 to-emerald-900/40",
  },
];

const SECONDARY_CARDS: DashCard[] = [
  {
    href: "/marketplace",
    icon: "🛒",
    title: "Marketplace",
    description: "Browse and install Skills, Models, and Tools. Pre-seeded with 7 LLMs, 8 tools, and publishable skill registry.",
    badge: "New",
    color: "from-amber-800/40 to-orange-900/40",
  },
  {
    href: "/observability",
    icon: "📊",
    title: "Observability",
    description: "Full trace explorer, KPI dashboard, structured logs, and real-time run monitoring with span-level detail.",
    color: "from-sky-800/40 to-blue-900/40",
  },
  {
    href: "/audit",
    icon: "📋",
    title: "Audit Log",
    description: "Immutable, append-only record of every human, agent, crew, and system action. Filter, export CSV, view stats.",
    badge: "New",
    color: "from-orange-800/40 to-red-900/40",
  },
  {
    href: "/admin/agents",
    icon: "🤖",
    title: "Agent Management",
    description: "Create, configure, and manage AI agents with system prompts, models, tools, and RBAC access control.",
    color: "from-slate-700/40 to-zinc-800/40",
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
          AgentOS: Enterprise Multi-Agent AI Platform
        </h1>
        <p className="max-w-2xl text-lg text-zinc-400 leading-relaxed">
          Orchestrate autonomous workflows with supervisor planning, multi-agent crews,
          a 9-stage input pipeline, a full marketplace, and complete audit trails.
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
            href="/marketplace"
            className="rounded-xl border border-zinc-700 hover:border-zinc-500 px-6 py-3 text-sm font-medium text-zinc-300 hover:text-white transition-colors"
          >
            Browse Marketplace
          </Link>
        </div>
      </div>

      {/* Stats strip */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-10">
        {[
          { label: "Pipeline Stages", value: "9" },
          { label: "Pre-seeded Models", value: "7" },
          { label: "Built-in Tools", value: "8" },
          { label: "API Endpoints", value: "80+" },
        ].map(({ label, value }) => (
          <div key={label} className="rounded-xl border border-zinc-800 bg-zinc-900/40 p-4 text-center">
            <div className="text-2xl font-bold text-white">{value}</div>
            <div className="text-xs text-zinc-500 mt-0.5">{label}</div>
          </div>
        ))}
      </div>

      {/* Primary features */}
      <div className="mb-4">
        <h2 className="text-xs font-semibold text-zinc-500 uppercase tracking-widest mb-4">Core</h2>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {PRIMARY_CARDS.map((card) => (
            <Card key={card.href} card={card} />
          ))}
        </div>
      </div>

      {/* Secondary features */}
      <div className="mt-6">
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

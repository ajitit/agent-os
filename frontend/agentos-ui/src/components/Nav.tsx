/**
 * File: Nav.tsx
 *
 * Top navigation bar for AgentOS UI.
 * Includes all primary routes: Chat, Pipeline, Workflows, Plans, Marketplace,
 * Audit, Observability, Agents, and Settings dropdown.
 */
"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { ModelSelector } from "./ModelSelector";

interface NavLinkGroup {
  label: string;
  items: { href: string; label: string }[];
}

const GROUPS: NavLinkGroup[] = [
  {
    label: "Operate",
    items: [
      { href: "/chat", label: "Chat" },
      { href: "/pipeline", label: "Pipeline" },
      { href: "/plans", label: "Plans" },
      { href: "/workflows", label: "Workflows" },
    ],
  },
  {
    label: "Manage",
    items: [
      { href: "/marketplace", label: "Marketplace" },
      { href: "/admin/agents", label: "Agents" },
    ],
  },
  {
    label: "Registry",
    items: [
      { href: "/registry/skills", label: "Skills" },
      { href: "/registry/models", label: "Models" },
      { href: "/registry/knowledge-graphs", label: "Knowledge Graphs" },
      { href: "/registry/tools", label: "Tools" },
      { href: "/registry/mcp-servers", label: "MCP Servers" },
      { href: "/registry/remote-apis", label: "Remote APIs" },
      { href: "/registry/data-sources", label: "Data Sources" },
    ],
  },
  {
    label: "Observe",
    items: [
      { href: "/observability", label: "Observability" },
      { href: "/audit", label: "Audit" },
    ],
  },
];

const FLAT_LINKS = GROUPS.flatMap((g) => g.items);

export function Nav() {
  const pathname = usePathname();

  const isActive = (href: string) => pathname?.startsWith(href) ?? false;

  const linkClass = (href: string) =>
    isActive(href)
      ? "font-semibold text-white"
      : "text-zinc-500 hover:text-zinc-200 dark:text-zinc-400 dark:hover:text-zinc-100";

  return (
    <nav className="border-b border-zinc-800 bg-zinc-950 sticky top-0 z-40">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-3 gap-4">
        {/* Logo */}
        <Link
          href="/"
          className="flex items-center gap-2 text-white font-bold text-lg tracking-tight shrink-0"
        >
          <span className="w-7 h-7 rounded-lg bg-gradient-to-br from-violet-600 to-indigo-700 flex items-center justify-center text-sm">⚡</span>
          AgentOS
        </Link>

        {/* Primary links */}
        <div className="hidden md:flex items-center gap-5 text-sm">
          {FLAT_LINKS.map(({ href, label }) => (
            <Link key={href} href={href} className={`transition-colors ${linkClass(href)}`}>
              {label}
            </Link>
          ))}
        </div>

        {/* Right side */}
        <div className="flex items-center gap-3 text-sm shrink-0">
          <ModelSelector />
          <div className="h-4 w-px bg-zinc-800" />

          {/* Settings dropdown */}
          <div className="group relative">
            <button
              className="text-zinc-400 hover:text-zinc-100 transition-colors flex items-center gap-1 text-sm"
              aria-label="Settings menu"
            >
              <span className="hidden sm:inline">Settings</span>
              <span className="text-xs">▾</span>
            </button>
            <div className="invisible group-hover:visible absolute right-0 top-full z-50 mt-2 w-52 origin-top-right rounded-xl border border-zinc-800 bg-zinc-950 p-1.5 shadow-xl">
              <div className="px-2 py-1 text-xs text-zinc-600 uppercase tracking-wider mb-1">Account</div>
              <Link href="/profile" className="flex items-center gap-2 rounded-lg px-3 py-2 text-sm text-zinc-400 hover:bg-zinc-900 hover:text-zinc-100 transition-colors">
                <span>👤</span> Profile
              </Link>
              <Link href="/settings/preferences" className="flex items-center gap-2 rounded-lg px-3 py-2 text-sm text-zinc-400 hover:bg-zinc-900 hover:text-zinc-100 transition-colors">
                <span>⚙️</span> Preferences
              </Link>
              <Link href="/settings/keys" className="flex items-center gap-2 rounded-lg px-3 py-2 text-sm text-zinc-400 hover:bg-zinc-900 hover:text-zinc-100 transition-colors">
                <span>🔑</span> API Keys
              </Link>
              <div className="border-t border-zinc-800 my-1" />
              <div className="px-2 py-1 text-xs text-zinc-600 uppercase tracking-wider mb-1">Platform</div>
              <Link href="/admin/agents" className="flex items-center gap-2 rounded-lg px-3 py-2 text-sm text-zinc-400 hover:bg-zinc-900 hover:text-zinc-100 transition-colors">
                <span>🤖</span> Agents
              </Link>
              <Link href="/admin/mcp" className="flex items-center gap-2 rounded-lg px-3 py-2 text-sm text-zinc-400 hover:bg-zinc-900 hover:text-zinc-100 transition-colors">
                <span>🔌</span> MCP Services
              </Link>
              <Link href="/analytics" className="flex items-center gap-2 rounded-lg px-3 py-2 text-sm text-zinc-400 hover:bg-zinc-900 hover:text-zinc-100 transition-colors">
                <span>📈</span> Analytics
              </Link>
            </div>
          </div>
        </div>
      </div>

      {/* Mobile overflow */}
      <div className="md:hidden overflow-x-auto border-t border-zinc-800">
        <div className="flex gap-4 px-6 py-2 text-sm w-max">
          {FLAT_LINKS.map(({ href, label }) => (
            <Link key={href} href={href} className={`transition-colors whitespace-nowrap ${linkClass(href)}`}>
              {label}
            </Link>
          ))}
        </div>
      </div>
    </nav>
  );
}

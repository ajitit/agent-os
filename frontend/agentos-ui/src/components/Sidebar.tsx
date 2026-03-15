/**
 * File: Sidebar.tsx
 *
 * Left sidebar navigation for AgentOS UI.
 * Implements the Agentic AI Platform navigation structure:
 *   Chat
 *   Plan & Workflow → Plan, Workflow, Output/Feedback, Performance Review
 *   Agent Management
 *   Agent Capabilities → Skills, Model, Knowledge Graph
 *   Tools & Integrations → MCP Server → Data Source, Remote API
 *   Insights & Governance → Analytics, Observability, Audit
 *   Settings → Profile, Preferences, API
 */
"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState, useEffect } from "react";
import { ModelSelector } from "./ModelSelector";

// ── Nav tree types ──────────────────────────────────────────────────────────

type LeafNode = {
  type: "leaf";
  label: string;
  href: string;
  icon: string;
};

type GroupNode = {
  type: "group";
  label: string;
  icon: string;
  /** Optional direct link on the group header */
  href?: string;
  children: NavNode[];
};

type NavNode = LeafNode | GroupNode;

// ── Navigation tree ─────────────────────────────────────────────────────────

const NAV_TREE: NavNode[] = [
  {
    type: "leaf",
    label: "Chat",
    href: "/chat",
    icon: "💬",
  },
  {
    type: "group",
    label: "Plan & Workflow",
    icon: "📋",
    children: [
      { type: "leaf", label: "Plan", href: "/plans", icon: "🗺️" },
      { type: "leaf", label: "Workflow", href: "/workflows", icon: "🎨" },
      { type: "leaf", label: "Output / Feedback", href: "/plan-workflow/output", icon: "📤" },
      { type: "leaf", label: "Performance Review", href: "/plan-workflow/performance", icon: "📈" },
    ],
  },
  {
    type: "leaf",
    label: "Agent Management",
    href: "/admin/agents",
    icon: "🤖",
  },
  {
    type: "group",
    label: "Agent Capabilities",
    icon: "⚡",
    children: [
      { type: "leaf", label: "Skills", href: "/registry/skills", icon: "🎯" },
      { type: "leaf", label: "Model", href: "/registry/models", icon: "🧠" },
      { type: "leaf", label: "Knowledge Graph", href: "/registry/knowledge-graphs", icon: "🕸️" },
    ],
  },
  {
    type: "group",
    label: "Tools & Integrations",
    icon: "🔧",
    children: [
      {
        type: "group",
        label: "MCP Server",
        icon: "🔌",
        href: "/registry/mcp-servers",
        children: [
          { type: "leaf", label: "Data Source", href: "/registry/data-sources", icon: "🗄️" },
          { type: "leaf", label: "Remote API", href: "/registry/remote-apis", icon: "🌐" },
        ],
      },
    ],
  },
  {
    type: "group",
    label: "Insights & Governance",
    icon: "📊",
    children: [
      { type: "leaf", label: "Analytics", href: "/analytics", icon: "📉" },
      { type: "leaf", label: "Observability", href: "/observability", icon: "🔍" },
      { type: "leaf", label: "Audit", href: "/audit", icon: "🗂️" },
    ],
  },
  {
    type: "group",
    label: "Settings",
    icon: "⚙️",
    children: [
      { type: "leaf", label: "Profile", href: "/profile", icon: "👤" },
      { type: "leaf", label: "Preferences", href: "/settings/preferences", icon: "🎛️" },
      { type: "leaf", label: "API", href: "/settings/keys", icon: "🔑" },
    ],
  },
];

// ── Helpers ──────────────────────────────────────────────────────────────────

function getAllHrefs(node: NavNode): string[] {
  if (node.type === "leaf") return [node.href];
  const childHrefs = node.children.flatMap(getAllHrefs);
  return node.href ? [node.href, ...childHrefs] : childHrefs;
}

function getAutoExpanded(pathname: string | null): Set<string> {
  const result = new Set<string>();

  function walk(nodes: NavNode[]) {
    for (const node of nodes) {
      if (node.type === "group") {
        const hrefs = getAllHrefs(node);
        if (hrefs.some((h) => pathname?.startsWith(h))) {
          result.add(node.label);
        }
        walk(node.children);
      }
    }
  }

  walk(NAV_TREE);
  return result;
}

// ── Component ────────────────────────────────────────────────────────────────

export function Sidebar() {
  const pathname = usePathname();
  const [expanded, setExpanded] = useState<Set<string>>(() => getAutoExpanded(pathname));

  // Auto-expand groups when navigating to a child route
  useEffect(() => {
    const auto = getAutoExpanded(pathname);
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setExpanded((prev) => new Set([...prev, ...auto]));
  }, [pathname]);

  const toggleGroup = (label: string) => {
    setExpanded((prev) => {
      const next = new Set(prev);
      if (next.has(label)) { next.delete(label); } else { next.add(label); }
      return next;
    });
  };

  const isActive = (href: string) => pathname === href || (pathname?.startsWith(href + "/") ?? false);

  // ── Renderers ──────────────────────────────────────────────────────────────

  function renderLeaf(node: LeafNode, depth: number) {
    const active = isActive(node.href);
    return (
      <Link
        key={node.href}
        href={node.href}
        style={{ paddingLeft: `${0.625 + depth * 0.875}rem` }}
        className={`group flex items-center gap-2.5 rounded-lg pr-3 py-2 text-sm transition-colors ${
          active
            ? "bg-violet-700/20 text-violet-300 font-medium"
            : "text-zinc-400 hover:bg-zinc-800/60 hover:text-zinc-100"
        }`}
      >
        <span className="text-sm leading-none shrink-0">{node.icon}</span>
        <span className="flex-1 leading-tight">{node.label}</span>
        {active && <span className="w-1.5 h-1.5 rounded-full bg-violet-400 shrink-0" />}
      </Link>
    );
  }

  function renderGroup(node: GroupNode, depth: number) {
    const isOpen = expanded.has(node.label);
    const childHrefs = getAllHrefs(node);
    const anyChildActive = childHrefs.some((h) => isActive(h));

    return (
      <div key={node.label}>
        {/* Group header */}
        <div
          role="button"
          tabIndex={0}
          aria-expanded={isOpen}
          style={{ paddingLeft: `${0.625 + depth * 0.875}rem` }}
          className={`flex items-center gap-2.5 rounded-lg pr-3 py-2 text-sm cursor-pointer select-none transition-colors ${
            anyChildActive
              ? "text-zinc-100"
              : "text-zinc-400 hover:bg-zinc-800/60 hover:text-zinc-100"
          }`}
          onClick={() => toggleGroup(node.label)}
          onKeyDown={(e) => e.key === "Enter" && toggleGroup(node.label)}
        >
          <span className="text-sm leading-none shrink-0">{node.icon}</span>

          {/* If the group has its own href, make label a link */}
          {node.href ? (
            <Link
              href={node.href}
              className="flex-1 leading-tight hover:text-violet-300 transition-colors"
              onClick={(e) => e.stopPropagation()}
            >
              {node.label}
            </Link>
          ) : (
            <span className="flex-1 leading-tight">{node.label}</span>
          )}

          <span
            className={`text-zinc-600 text-xs transition-transform duration-200 shrink-0 ${
              isOpen ? "rotate-90" : ""
            }`}
          >
            ›
          </span>
        </div>

        {/* Children */}
        {isOpen && (
          <div className="mt-0.5">
            {node.children.map((child) =>
              child.type === "leaf"
                ? renderLeaf(child, depth + 1)
                : renderGroup(child as GroupNode, depth + 1)
            )}
          </div>
        )}
      </div>
    );
  }

  // ── Render ─────────────────────────────────────────────────────────────────

  return (
    <aside className="flex flex-col w-60 shrink-0 border-r border-zinc-800 bg-zinc-950 h-screen sticky top-0 overflow-y-auto">
      {/* Logo */}
      <div className="px-4 py-4 border-b border-zinc-800 shrink-0">
        <Link
          href="/"
          className="flex items-center gap-2.5 text-white tracking-tight"
        >
          <span className="w-8 h-8 rounded-lg bg-gradient-to-br from-violet-600 to-indigo-700 flex items-center justify-center text-sm shrink-0">
            ⚡
          </span>
          <span>
            <span className="block text-sm font-bold leading-tight">AgentOS</span>
            <span className="block text-xs text-zinc-500 font-normal leading-tight">
              Agentic AI Platform
            </span>
          </span>
        </Link>
      </div>

      {/* Model selector */}
      <div className="px-3 py-3 border-b border-zinc-800 shrink-0">
        <ModelSelector />
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-2 py-3 space-y-0.5 overflow-y-auto">
        {NAV_TREE.map((node) =>
          node.type === "leaf" ? renderLeaf(node, 0) : renderGroup(node, 0)
        )}
      </nav>

      {/* Footer */}
      <div className="px-4 py-3 border-t border-zinc-800 shrink-0">
        <p className="text-xs text-zinc-600">AgentOS v1.0</p>
      </div>
    </aside>
  );
}

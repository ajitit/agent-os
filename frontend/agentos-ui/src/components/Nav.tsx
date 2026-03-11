/**
 * File: Nav.tsx
 * 
 * Purpose:
 * Renders the primary top navigation bar for the AgentOS frontend application.
 * 
 * Key Functionalities:
 * - Provide client-side routing links (Next.js) to major sections: Agents, MCP Services, Evaluations, Analytics, Chat
 * - Highlight the active route
 * - Embed the `ModelSelector` component for global model switching
 * 
 * Inputs:
 * - Current URL pathname via `usePathname`
 * 
 * Outputs:
 * - React navigation component
 * 
 * Interacting Files / Modules:
 * - src.components.ModelSelector
 */
"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { ModelSelector } from "./ModelSelector";

export function Nav() {
  const pathname = usePathname();

  const link = (href: string, label: string) => (
    <Link
      href={href}
      className={
        pathname?.startsWith(href)
          ? "font-medium text-zinc-900 dark:text-zinc-100"
          : "text-zinc-600 hover:text-zinc-900 dark:text-zinc-400 dark:hover:text-zinc-100"
      }
    >
      {label}
    </Link>
  );

  return (
    <nav className="border-b border-zinc-200 bg-white dark:border-zinc-800 dark:bg-zinc-900">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
        <Link href="/" className="text-xl font-semibold text-zinc-900 dark:text-zinc-100">
          AgentOS
        </Link>
        <div className="flex items-center gap-6">
          {link("/admin/agents", "Agents")}
          {link("/admin/mcp", "MCP Services")}
          {link("/chat", "Chat")}
          <div className="h-4 w-px bg-zinc-200 dark:bg-zinc-800" />
          {link("/profile", "Profile")}
          <div className="group relative">
            <button className="text-zinc-600 hover:text-zinc-900 dark:text-zinc-400 dark:hover:text-zinc-100">
              Settings
            </button>
            <div className="invisible absolute right-0 top-full z-50 mt-2 w-48 origin-top-right rounded-xl border border-zinc-200 bg-white p-2 shadow-lg group-hover:visible dark:border-zinc-800 dark:bg-zinc-900">
              <Link href="/settings/preferences" className="block rounded-lg px-3 py-2 text-sm text-zinc-600 hover:bg-zinc-50 hover:text-zinc-900 dark:text-zinc-400 dark:hover:bg-zinc-800 dark:hover:text-zinc-100">
                Preferences
              </Link>
              <Link href="/settings/keys" className="block rounded-lg px-3 py-2 text-sm text-zinc-600 hover:bg-zinc-50 hover:text-zinc-900 dark:text-zinc-400 dark:hover:bg-zinc-800 dark:hover:text-zinc-100">
                API Keys
              </Link>
            </div>
          </div>
          <ModelSelector />
        </div>
      </div>
    </nav>
  );
}

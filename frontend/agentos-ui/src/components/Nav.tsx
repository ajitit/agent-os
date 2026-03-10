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
          {link("/evaluations", "Evaluations")}
          {link("/analytics", "Analytics")}
          {link("/chat", "Chat")}
          <ModelSelector />
        </div>
      </div>
    </nav>
  );
}

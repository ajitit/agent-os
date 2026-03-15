/**
 * File: chat/page.tsx
 *
 * ChatWorkspace — split-pane chat UI for the Supervisor Agent.
 * Left: conversation list + active tasks sidebar.
 * Right: message thread with streaming SSE + live agent activity feed.
 */
"use client";

import { useEffect, useRef, useState } from "react";

// ── Types ────────────────────────────────────────────────────────────────────

type Message = {
  id: string;
  role: "user" | "assistant" | "supervisor" | "error";
  content: string;
  nodeName?: string;
  timestamp: string;
};

type Conversation = { id: string; title: string; userId?: string };

type ActiveTask = {
  runId: string;
  status: "routing" | "in_progress" | "complete" | "failed";
  preview: string;
};

const STATUS_COLOR: Record<string, string> = {
  routing: "text-yellow-500",
  in_progress: "text-blue-500",
  complete: "text-green-500",
  failed: "text-red-500",
};

// ── Component ────────────────────────────────────────────────────────────────

export default function ChatPage() {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [activeConvId, setActiveConvId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [tasks, setTasks] = useState<ActiveTask[]>([]);
  const [input, setInput] = useState("");
  const [priority, setPriority] = useState<"low" | "normal" | "high" | "urgent">("normal");
  const [sending, setSending] = useState(false);
  const [token, setToken] = useState<string | null>(null);
  const bottomRef = useRef<HTMLDivElement>(null);
  const esRef = useRef<EventSource | null>(null);

  // ── Auth token (localStorage) ─────────────────────────────────────────────
  async function loadConversations(t: string) {
    try {
      const res = await fetch("/api/v1/chat/conversations", {
        headers: { Authorization: `Bearer ${t}` },
      });
      if (res.ok) {
        const json = await res.json();
        setConversations(json.data || []);
      }
    } catch {}
  }

  useEffect(() => {
    const t = typeof window !== "undefined" ? localStorage.getItem("vishwakarma_token") : null;
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setToken(t);
    if (t) loadConversations(t);
  }, []);

  async function createConversation() {
    if (!token) return null;
    const res = await fetch("/api/v1/chat/conversations", {
      method: "POST",
      headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
      body: JSON.stringify({ title: "New Chat" }),
    });
    if (res.ok) {
      const json = await res.json();
      const conv: Conversation = json.data;
      setConversations((prev) => [conv, ...prev]);
      return conv.id;
    }
    return null;
  }

  async function selectConversation(convId: string) {
    setActiveConvId(convId);
    if (!token) return;
    const res = await fetch(`/api/v1/chat/conversations/${convId}/messages`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (res.ok) {
      const json = await res.json();
      setMessages(
        (json.data || []).map((m: Record<string, unknown>, i: number) => ({
          id: String(i),
          role: m.role === "assistant" ? "assistant" : "user",
          content: m.content as string,
          timestamp: new Date().toISOString(),
        }))
      );
    }
  }

  async function sendMessage() {
    if (!input.trim() || sending) return;
    setSending(true);

    let convId = activeConvId;
    if (!convId) {
      convId = await createConversation();
      if (convId) setActiveConvId(convId);
    }

    const userMsg: Message = {
      id: Date.now().toString(),
      role: "user",
      content: input.trim(),
      timestamp: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");

    try {
      const res = await fetch("/api/v1/chat/send", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({
          message: userMsg.content,
          conversation_id: convId,
          priority,
        }),
      });
      const json = await res.json();
      const runId: string = json?.data?.runId;
      if (!runId) { setSending(false); return; }

      // Track task
      setTasks((prev) => [
        { runId, status: "routing", preview: userMsg.content.slice(0, 50) },
        ...prev,
      ]);

      // Connect SSE
      const es = new EventSource(`/api/v1/chat/stream/${runId}`);
      esRef.current = es;

      es.onmessage = (e) => {
        try {
          const event = JSON.parse(e.data);
          if (event.type === "message" && event.nodeName === "agent") {
            const assistantMsg: Message = {
              id: event.timestamp,
              role: "assistant",
              content: event.message,
              nodeName: event.nodeName,
              timestamp: event.timestamp,
            };
            setMessages((prev) => [...prev, assistantMsg]);
            setTasks((prev) =>
              prev.map((t) => (t.runId === runId ? { ...t, status: "in_progress" } : t))
            );
          } else if (event.type === "message" && event.nodeName === "supervisor") {
            const supMsg: Message = {
              id: event.timestamp,
              role: "supervisor",
              content: event.message,
              nodeName: "supervisor",
              timestamp: event.timestamp,
            };
            setMessages((prev) => [...prev, supMsg]);
          } else if (event.type === "complete") {
            setTasks((prev) =>
              prev.map((t) => (t.runId === runId ? { ...t, status: "complete" } : t))
            );
            es.close();
            setSending(false);
          } else if (event.type === "error") {
            const errMsg: Message = {
              id: Date.now().toString(),
              role: "error",
              content: event.message || "Execution error",
              timestamp: event.timestamp,
            };
            setMessages((prev) => [...prev, errMsg]);
            setTasks((prev) =>
              prev.map((t) => (t.runId === runId ? { ...t, status: "failed" } : t))
            );
            es.close();
            setSending(false);
          }
        } catch {}
      };

      es.addEventListener("done", () => { es.close(); setSending(false); });
      es.onerror = () => { es.close(); setSending(false); };
    } catch {
      setSending(false);
    }
  }

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // ── Render ────────────────────────────────────────────────────────────────

  return (
    <div className="flex h-[calc(100vh-57px)] overflow-hidden">
      {/* LEFT SIDEBAR */}
      <aside className="flex w-64 flex-col border-r border-zinc-200 bg-white dark:border-zinc-800 dark:bg-zinc-900">
        <div className="flex items-center justify-between px-4 py-3 border-b border-zinc-200 dark:border-zinc-800">
          <span className="text-sm font-semibold text-zinc-700 dark:text-zinc-300">Conversations</span>
          <button
            onClick={async () => { const id = await createConversation(); if (id) setActiveConvId(id); setMessages([]); }}
            className="rounded-lg bg-zinc-900 px-2 py-1 text-xs text-white dark:bg-zinc-100 dark:text-zinc-900"
          >
            + New
          </button>
        </div>
        <div className="flex-1 overflow-y-auto p-2 space-y-1">
          {conversations.length === 0 && (
            <p className="px-2 py-4 text-xs text-zinc-400 text-center">No conversations yet</p>
          )}
          {conversations.map((c) => (
            <button
              key={c.id}
              onClick={() => selectConversation(c.id)}
              className={`w-full rounded-lg px-3 py-2 text-left text-sm truncate transition ${
                activeConvId === c.id
                  ? "bg-zinc-100 font-medium dark:bg-zinc-800"
                  : "text-zinc-600 hover:bg-zinc-50 dark:text-zinc-400 dark:hover:bg-zinc-800"
              }`}
            >
              {c.title}
            </button>
          ))}
        </div>

        {/* Active Tasks Panel */}
        <div className="border-t border-zinc-200 dark:border-zinc-800 p-3">
          <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-zinc-400">Active Tasks</p>
          <div className="space-y-1">
            {tasks.slice(0, 5).map((t) => (
              <div key={t.runId} className="flex items-center gap-2 rounded-lg px-2 py-1.5 bg-zinc-50 dark:bg-zinc-800/50">
                <span className={`text-xs ${STATUS_COLOR[t.status]}`}>●</span>
                <span className="text-xs text-zinc-600 dark:text-zinc-400 truncate">{t.preview}</span>
              </div>
            ))}
            {tasks.length === 0 && <p className="text-xs text-zinc-400">No active tasks</p>}
          </div>
        </div>
      </aside>

      {/* MAIN CHAT AREA */}
      <div className="flex flex-1 flex-col bg-zinc-50 dark:bg-zinc-950">
        {/* Messages */}
        <div className="flex-1 overflow-y-auto px-6 py-6 space-y-4">
          {messages.length === 0 && (
            <div className="flex h-full items-center justify-center">
              <div className="text-center">
                <p className="text-2xl font-semibold text-zinc-700 dark:text-zinc-300">AgentOS Chat</p>
                <p className="mt-2 text-sm text-zinc-500">Send a message to start a new task</p>
              </div>
            </div>
          )}
          {messages.map((msg) => (
            <div
              key={msg.id}
              className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
            >
              <div
                className={`max-w-[75%] rounded-2xl px-4 py-3 text-sm leading-relaxed ${
                  msg.role === "user"
                    ? "bg-zinc-900 text-white dark:bg-zinc-100 dark:text-zinc-900"
                    : msg.role === "supervisor"
                    ? "bg-yellow-50 border border-yellow-200 text-yellow-800 dark:bg-yellow-900/20 dark:border-yellow-700 dark:text-yellow-200"
                    : msg.role === "error"
                    ? "bg-red-50 border border-red-200 text-red-700 dark:bg-red-900/20 dark:border-red-700 dark:text-red-300"
                    : "bg-white border border-zinc-200 text-zinc-800 dark:bg-zinc-800 dark:border-zinc-700 dark:text-zinc-200"
                }`}
              >
                {msg.role === "supervisor" && (
                  <p className="mb-1 text-xs font-semibold text-yellow-600 dark:text-yellow-400">
                    🔀 Supervisor
                  </p>
                )}
                {msg.role === "assistant" && msg.nodeName && (
                  <p className="mb-1 text-xs font-semibold text-zinc-400">
                    🤖 {msg.nodeName}
                  </p>
                )}
                {msg.content}
              </div>
            </div>
          ))}
          {sending && (
            <div className="flex justify-start">
              <div className="rounded-2xl border border-zinc-200 bg-white px-4 py-3 text-sm text-zinc-500 dark:bg-zinc-800 dark:border-zinc-700 dark:text-zinc-400">
                <span className="animate-pulse">Agent thinking…</span>
              </div>
            </div>
          )}
          <div ref={bottomRef} />
        </div>

        {/* Input Bar */}
        <div className="border-t border-zinc-200 bg-white px-6 py-4 dark:border-zinc-800 dark:bg-zinc-900">
          <div className="flex items-center gap-3">
            <select
              value={priority}
              onChange={(e) => setPriority(e.target.value as typeof priority)}
              className="rounded-lg border border-zinc-300 bg-zinc-50 px-2 py-2 text-xs text-zinc-600 dark:border-zinc-700 dark:bg-zinc-800 dark:text-zinc-300"
            >
              <option value="low">Low</option>
              <option value="normal">Normal</option>
              <option value="high">High</option>
              <option value="urgent">Urgent</option>
            </select>
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && sendMessage()}
              placeholder="Assign a task to the Supervisor Agent…"
              className="flex-1 rounded-xl border border-zinc-300 bg-zinc-50 px-4 py-2.5 text-sm outline-none focus:border-zinc-500 dark:border-zinc-700 dark:bg-zinc-800 dark:text-zinc-100 dark:placeholder-zinc-500"
            />
            <button
              onClick={sendMessage}
              disabled={sending || !input.trim()}
              className="rounded-xl bg-zinc-900 px-5 py-2.5 text-sm font-medium text-white disabled:opacity-50 dark:bg-zinc-100 dark:text-zinc-900"
            >
              Send
            </button>
          </div>
          {!token && (
            <p className="mt-2 text-xs text-amber-600">
              ⚠ Not logged in — messages sent anonymously. <a href="/profile" className="underline">Log in</a> to save history.
            </p>
          )}
        </div>
      </div>
    </div>
  );
}

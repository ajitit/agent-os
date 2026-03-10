/**
 * File: api.ts
 * 
 * Purpose:
 * Provides a highly-typed HTTP API client for interacting with the AgentOS backend,
 * centralizing fetch logic, error handling, and type definitions.
 * 
 * Key Functionalities:
 * - Implement API wrapper methods (get, post, put, delete) with standardized JSON handling
 * - Custom `APIError` class for consistent error mapping and request tracing
 * - Export TypeScript types corresponding to backend models (Agent, MCPServer, Task, etc.)
 * 
 * Inputs:
 * - HTTP request paths, payloads, and options
 * 
 * Outputs:
 * - Parsed JSON object responses typed as Generics
 * - Standardized APIError exceptions
 * 
 * Interacting Files / Modules:
 * - src.lib.env
 */

import { env } from "./env";

const API_PREFIX = "/api/v1";

export class APIError extends Error {
  constructor(
    message: string,
    public status: number,
    public code?: string,
    public requestId?: string
  ) {
    super(message);
    this.name = "APIError";
  }
}

async function handleResponse<T>(res: Response): Promise<T> {
  const requestId = res.headers.get("X-Request-ID") ?? undefined;

  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = body.detail ?? body.error ?? detail;
    } catch {
      // ignore
    }
    throw new APIError(
      typeof detail === "string" ? detail : "Request failed",
      res.status,
      undefined,
      requestId
    );
  }

  const contentType = res.headers.get("content-type");
  if (contentType?.includes("application/json")) {
    return res.json() as Promise<T>;
  }
  return res.text() as Promise<T>;
}

export const api = {
  baseUrl: env.apiUrl,

  async get<T>(path: string, options?: RequestInit): Promise<T> {
    const res = await fetch(`${env.apiUrl}${API_PREFIX}${path}`, {
      ...options,
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        ...options?.headers,
      },
    });
    return handleResponse<T>(res);
  },

  async post<T>(path: string, body?: unknown, options?: RequestInit): Promise<T> {
    const res = await fetch(`${env.apiUrl}${API_PREFIX}${path}`, {
      ...options,
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...options?.headers,
      },
      body: body ? JSON.stringify(body) : undefined,
    });
    return handleResponse<T>(res);
  },

  async put<T>(path: string, body?: unknown, options?: RequestInit): Promise<T> {
    const res = await fetch(`${env.apiUrl}${API_PREFIX}${path}`, {
      ...options,
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        ...options?.headers,
      },
      body: body ? JSON.stringify(body) : undefined,
    });
    return handleResponse<T>(res);
  },

  async delete(path: string, options?: RequestInit): Promise<void> {
    const res = await fetch(`${env.apiUrl}${API_PREFIX}${path}`, {
      ...options,
      method: "DELETE",
    });
    if (!res.ok) {
      let detail = res.statusText;
      try {
        const body = await res.json();
        detail = body.detail ?? body.error ?? detail;
      } catch {
        /* empty */
      }
      throw new APIError(detail, res.status);
    }
  },
};

export type Agent = {
  id: string;
  name: string;
  role?: string;
  model?: string;
  status?: string;
  system_prompt?: string;
  temperature?: number;
  tool_ids?: string[];
};

export type MCPServer = {
  id: string;
  name: string;
  url?: string;
  command?: string;
};

export type MCPTool = {
  id: string;
  name: string;
  description?: string;
  enabled?: boolean;
};

export type ModelSetting = {
  primary_model: string;
  available_models: { id: string; name: string; provider: string }[];
};

export type Task = { goal: string; status: string };
export type HealthStatus = { status: string; version: string; environment: string };

export type AgentEvaluation = {
  id: string;
  agent_id: string;
  agent_version: string;
  model_provider: string;
  task_category: string;
  task_success_rate: number;
  hallucination_rate: number;
  tool_call_accuracy: number;
  intent_resolution: number;
  latency_ms?: number;
  total_tokens?: number;
  created_at: string;
};

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
export type User = {
  id: string;
  email: string;
  full_name?: string;
  role: "admin" | "developer" | "operator" | "viewer";
};

export type UserPreferences = {
  theme: "light" | "dark" | "system";
  accentColor: string;
  fontSize: "sm" | "md" | "lg";
  defaultPriority: "low" | "normal" | "high" | "urgent";
  streamingEnabled: boolean;
  showAgentThinking: boolean;
  defaultSupervisorBehavior: "auto_route" | "confirm_routing" | "manual_select";
  emailOnFailure: boolean;
  emailDigestFrequency: "never" | "daily" | "weekly";
};

export type APIKey = {
  id: string;
  name: string;
  key: string;
  createdAt: string;
};

export type APIResponse<T> = {
  data: T;
  meta?: {
    version: string;
    timestamp: string;
  };
};

// ── Registry Types ────────────────────────────────────────────────────────────

export type RegistrySkill = {
  id: string;
  name: string;
  description: string;
  category: string;
  author?: string;
  version: string;
  status: "active" | "deprecated" | "draft";
  tags: string[];
  installs?: number;
  createdAt?: string;
  updatedAt?: string;
};

export type RegistryModel = {
  id: string;
  name: string;
  provider: string;
  type: "chat" | "embedding" | "image" | "audio" | "vision";
  contextWindow?: number;
  description?: string;
  status: "active" | "deprecated" | "draft";
  tags: string[];
  installs?: number;
  createdAt?: string;
  updatedAt?: string;
};

export type KnowledgeGraph = {
  id: string;
  name: string;
  description?: string;
  category?: string;
  endpointUrl: string;
  authType: "none" | "api_key" | "oauth2" | "basic";
  status: "active" | "inactive" | "draft";
  tags: string[];
  createdAt?: string;
  updatedAt?: string;
};

export type RegistryTool = {
  id: string;
  name: string;
  category: string;
  description: string;
  author?: string;
  version: string;
  status: "active" | "deprecated" | "draft";
  tags: string[];
  installs?: number;
  createdAt?: string;
  updatedAt?: string;
};

export type RemoteAPI = {
  id: string;
  name: string;
  description?: string;
  category?: string;
  baseUrl: string;
  apiType: "rest" | "graphql" | "grpc" | "soap";
  authType: "none" | "api_key" | "oauth2" | "basic" | "bearer";
  status: "active" | "inactive" | "deprecated";
  tags: string[];
  createdAt?: string;
  updatedAt?: string;
};

export type DataSource = {
  id: string;
  name: string;
  description?: string;
  type: "postgresql" | "mysql" | "sqlite" | "mongodb" | "redis" | "s3" | "gcs" | "azure_blob" | "sftp" | "nfs" | "sharepoint" | "local";
  host?: string;
  port?: number;
  database?: string;
  status: "active" | "inactive" | "maintenance";
  tags: string[];
  createdAt?: string;
  updatedAt?: string;
};

export type RegistryGroup = {
  id: string;
  name: string;
  description?: string;
  members: string[];
  createdAt?: string;
};

// ── Registry API Methods ──────────────────────────────────────────────────────

export const registryApi = {
  // Skills
  skills: {
    list: (category?: string) =>
      api.get<APIResponse<RegistrySkill[]>>(`/registry/skills${category ? `?category=${category}` : ""}`),
    get: (id: string) => api.get<APIResponse<RegistrySkill>>(`/registry/skills/${id}`),
    create: (data: Partial<RegistrySkill>) => api.post<APIResponse<RegistrySkill>>("/registry/skills", data),
    update: (id: string, data: Partial<RegistrySkill>) => api.put<APIResponse<RegistrySkill>>(`/registry/skills/${id}`, data),
    delete: (id: string) => api.delete(`/registry/skills/${id}`),
    groups: {
      list: () => api.get<APIResponse<RegistryGroup[]>>("/registry/skills/groups"),
      create: (data: { name: string; description?: string }) => api.post<APIResponse<RegistryGroup>>("/registry/skills/groups", data),
      update: (gid: string, data: { name: string; description?: string }) => api.put<APIResponse<RegistryGroup>>(`/registry/skills/groups/${gid}`, data),
      delete: (gid: string) => api.delete(`/registry/skills/groups/${gid}`),
      addMember: (gid: string, skillId: string) => api.post(`/registry/skills/groups/${gid}/members`, { skill_id: skillId }),
      removeMember: (gid: string, skillId: string) => api.delete(`/registry/skills/groups/${gid}/members/${skillId}`),
    },
    agents: {
      list: (agentId: string) => api.get<APIResponse<string[]>>(`/registry/skills/agents/${agentId}`),
      assign: (agentId: string, skillId: string) => api.post(`/registry/skills/agents/${agentId}`, { skill_id: skillId }),
      remove: (agentId: string, skillId: string) => api.delete(`/registry/skills/agents/${agentId}/${skillId}`),
    },
  },

  // Models
  models: {
    list: (provider?: string, type?: string) => {
      const params = new URLSearchParams();
      if (provider) params.set("provider", provider);
      if (type) params.set("type", type);
      return api.get<APIResponse<RegistryModel[]>>(`/registry/models${params.toString() ? `?${params}` : ""}`);
    },
    get: (id: string) => api.get<APIResponse<RegistryModel>>(`/registry/models/${id}`),
    create: (data: Partial<RegistryModel> & { id: string }) => api.post<APIResponse<RegistryModel>>("/registry/models", data),
    update: (id: string, data: Partial<RegistryModel>) => api.put<APIResponse<RegistryModel>>(`/registry/models/${id}`, data),
    delete: (id: string) => api.delete(`/registry/models/${id}`),
    groups: {
      list: () => api.get<APIResponse<RegistryGroup[]>>("/registry/models/groups"),
      create: (data: { name: string; description?: string }) => api.post<APIResponse<RegistryGroup>>("/registry/models/groups", data),
      update: (gid: string, data: { name: string; description?: string }) => api.put<APIResponse<RegistryGroup>>(`/registry/models/groups/${gid}`, data),
      delete: (gid: string) => api.delete(`/registry/models/groups/${gid}`),
      addMember: (gid: string, modelId: string) => api.post(`/registry/models/groups/${gid}/members`, { model_id: modelId }),
      removeMember: (gid: string, modelId: string) => api.delete(`/registry/models/groups/${gid}/members/${modelId}`),
    },
    agents: {
      list: (agentId: string) => api.get<APIResponse<string[]>>(`/registry/models/agents/${agentId}`),
      assign: (agentId: string, modelId: string) => api.post(`/registry/models/agents/${agentId}`, { model_id: modelId }),
      remove: (agentId: string, modelId: string) => api.delete(`/registry/models/agents/${agentId}/${modelId}`),
    },
  },

  // Knowledge Graphs
  knowledgeGraphs: {
    list: (category?: string) =>
      api.get<APIResponse<KnowledgeGraph[]>>(`/registry/knowledge-graphs${category ? `?category=${category}` : ""}`),
    get: (id: string) => api.get<APIResponse<KnowledgeGraph>>(`/registry/knowledge-graphs/${id}`),
    create: (data: Partial<KnowledgeGraph>) => api.post<APIResponse<KnowledgeGraph>>("/registry/knowledge-graphs", data),
    update: (id: string, data: Partial<KnowledgeGraph>) => api.put<APIResponse<KnowledgeGraph>>(`/registry/knowledge-graphs/${id}`, data),
    delete: (id: string) => api.delete(`/registry/knowledge-graphs/${id}`),
    groups: {
      list: () => api.get<APIResponse<RegistryGroup[]>>("/registry/knowledge-graphs/groups"),
      create: (data: { name: string; description?: string }) => api.post<APIResponse<RegistryGroup>>("/registry/knowledge-graphs/groups", data),
      update: (gid: string, data: { name: string; description?: string }) => api.put<APIResponse<RegistryGroup>>(`/registry/knowledge-graphs/groups/${gid}`, data),
      delete: (gid: string) => api.delete(`/registry/knowledge-graphs/groups/${gid}`),
      addMember: (gid: string, kgId: string) => api.post(`/registry/knowledge-graphs/groups/${gid}/members`, { kg_id: kgId }),
      removeMember: (gid: string, kgId: string) => api.delete(`/registry/knowledge-graphs/groups/${gid}/members/${kgId}`),
    },
    agents: {
      list: (agentId: string) => api.get<APIResponse<string[]>>(`/registry/knowledge-graphs/agents/${agentId}`),
      assign: (agentId: string, kgId: string) => api.post(`/registry/knowledge-graphs/agents/${agentId}`, { kg_id: kgId }),
      remove: (agentId: string, kgId: string) => api.delete(`/registry/knowledge-graphs/agents/${agentId}/${kgId}`),
    },
  },

  // Tools
  tools: {
    list: (category?: string) =>
      api.get<APIResponse<RegistryTool[]>>(`/registry/tools${category ? `?category=${category}` : ""}`),
    get: (id: string) => api.get<APIResponse<RegistryTool>>(`/registry/tools/${id}`),
    create: (data: Partial<RegistryTool>) => api.post<APIResponse<RegistryTool>>("/registry/tools", data),
    update: (id: string, data: Partial<RegistryTool>) => api.put<APIResponse<RegistryTool>>(`/registry/tools/${id}`, data),
    delete: (id: string) => api.delete(`/registry/tools/${id}`),
    groups: {
      list: () => api.get<APIResponse<RegistryGroup[]>>("/registry/tools/groups"),
      create: (data: { name: string; description?: string }) => api.post<APIResponse<RegistryGroup>>("/registry/tools/groups", data),
      update: (gid: string, data: { name: string; description?: string }) => api.put<APIResponse<RegistryGroup>>(`/registry/tools/groups/${gid}`, data),
      delete: (gid: string) => api.delete(`/registry/tools/groups/${gid}`),
      addMember: (gid: string, toolId: string) => api.post(`/registry/tools/groups/${gid}/members`, { tool_id: toolId }),
      removeMember: (gid: string, toolId: string) => api.delete(`/registry/tools/groups/${gid}/members/${toolId}`),
    },
    agents: {
      list: (agentId: string) => api.get<APIResponse<string[]>>(`/registry/tools/agents/${agentId}`),
      assign: (agentId: string, toolId: string) => api.post(`/registry/tools/agents/${agentId}`, { tool_id: toolId }),
      remove: (agentId: string, toolId: string) => api.delete(`/registry/tools/agents/${agentId}/${toolId}`),
    },
    mcpServers: {
      list: (toolId: string) => api.get<APIResponse<string[]>>(`/registry/tools/${toolId}/mcp-servers`),
      assign: (toolId: string, serverId: string) => api.post(`/registry/tools/${toolId}/mcp-servers`, { server_id: serverId }),
      remove: (toolId: string, serverId: string) => api.delete(`/registry/tools/${toolId}/mcp-servers/${serverId}`),
    },
    remoteApis: {
      list: (toolId: string) => api.get<APIResponse<string[]>>(`/registry/tools/${toolId}/remote-apis`),
      assign: (toolId: string, apiId: string) => api.post(`/registry/tools/${toolId}/remote-apis`, { api_id: apiId }),
      remove: (toolId: string, apiId: string) => api.delete(`/registry/tools/${toolId}/remote-apis/${apiId}`),
    },
    dataSources: {
      list: (toolId: string) => api.get<APIResponse<string[]>>(`/registry/tools/${toolId}/data-sources`),
      assign: (toolId: string, dsId: string) => api.post(`/registry/tools/${toolId}/data-sources`, { ds_id: dsId }),
      remove: (toolId: string, dsId: string) => api.delete(`/registry/tools/${toolId}/data-sources/${dsId}`),
    },
  },

  // Remote APIs
  remoteApis: {
    list: (category?: string) =>
      api.get<APIResponse<RemoteAPI[]>>(`/registry/remote-apis${category ? `?category=${category}` : ""}`),
    get: (id: string) => api.get<APIResponse<RemoteAPI>>(`/registry/remote-apis/${id}`),
    create: (data: Partial<RemoteAPI>) => api.post<APIResponse<RemoteAPI>>("/registry/remote-apis", data),
    update: (id: string, data: Partial<RemoteAPI>) => api.put<APIResponse<RemoteAPI>>(`/registry/remote-apis/${id}`, data),
    delete: (id: string) => api.delete(`/registry/remote-apis/${id}`),
    groups: {
      list: () => api.get<APIResponse<RegistryGroup[]>>("/registry/remote-apis/groups"),
      create: (data: { name: string; description?: string }) => api.post<APIResponse<RegistryGroup>>("/registry/remote-apis/groups", data),
      delete: (gid: string) => api.delete(`/registry/remote-apis/groups/${gid}`),
      addMember: (gid: string, apiId: string) => api.post(`/registry/remote-apis/groups/${gid}/members`, { api_id: apiId }),
      removeMember: (gid: string, apiId: string) => api.delete(`/registry/remote-apis/groups/${gid}/members/${apiId}`),
    },
    tools: {
      list: (toolId: string) => api.get<APIResponse<string[]>>(`/registry/remote-apis/tools/${toolId}`),
      assign: (toolId: string, apiId: string) => api.post(`/registry/remote-apis/tools/${toolId}`, { api_id: apiId }),
      remove: (toolId: string, apiId: string) => api.delete(`/registry/remote-apis/tools/${toolId}/${apiId}`),
    },
  },

  // Data Sources
  dataSources: {
    list: (type?: string) =>
      api.get<APIResponse<DataSource[]>>(`/registry/data-sources${type ? `?type=${type}` : ""}`),
    get: (id: string) => api.get<APIResponse<DataSource>>(`/registry/data-sources/${id}`),
    create: (data: Partial<DataSource>) => api.post<APIResponse<DataSource>>("/registry/data-sources", data),
    update: (id: string, data: Partial<DataSource>) => api.put<APIResponse<DataSource>>(`/registry/data-sources/${id}`, data),
    delete: (id: string) => api.delete(`/registry/data-sources/${id}`),
    groups: {
      list: () => api.get<APIResponse<RegistryGroup[]>>("/registry/data-sources/groups"),
      create: (data: { name: string; description?: string }) => api.post<APIResponse<RegistryGroup>>("/registry/data-sources/groups", data),
      delete: (gid: string) => api.delete(`/registry/data-sources/groups/${gid}`),
      addMember: (gid: string, dsId: string) => api.post(`/registry/data-sources/groups/${gid}/members`, { ds_id: dsId }),
      removeMember: (gid: string, dsId: string) => api.delete(`/registry/data-sources/groups/${gid}/members/${dsId}`),
    },
    tools: {
      list: (toolId: string) => api.get<APIResponse<string[]>>(`/registry/data-sources/tools/${toolId}`),
      assign: (toolId: string, dsId: string) => api.post(`/registry/data-sources/tools/${toolId}`, { ds_id: dsId }),
      remove: (toolId: string, dsId: string) => api.delete(`/registry/data-sources/tools/${toolId}/${dsId}`),
    },
  },
};

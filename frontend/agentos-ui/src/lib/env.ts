/**
 * Validated environment configuration.
 * NEXT_PUBLIC_* vars are exposed to the browser.
 */

const REQUIRED_KEYS = ["NEXT_PUBLIC_API_URL"] as const;

function getEnv(key: (typeof REQUIRED_KEYS)[number]): string {
  const value = process.env[key];
  if (!value && process.env.NODE_ENV === "production") {
    throw new Error(`Missing required env: ${key}`);
  }
  return value || "http://localhost:8000";
}

export const env = {
  apiUrl: getEnv("NEXT_PUBLIC_API_URL").replace(/\/$/, ""),
} as const;

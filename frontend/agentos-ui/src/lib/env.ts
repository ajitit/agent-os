/**
 * File: env.ts
 * 
 * Purpose:
 * Validates and exposes environment variables to the frontend application,
 * ensuring required values are present before the app runs.
 * 
 * Key Functionalities:
 * - Check for required environment variables (NEXT_PUBLIC_API_URL)
 * - Throw errors in production if keys are missing
 * - Export a strongly-typed `env` object with validated endpoints
 * 
 * Inputs:
 * - process.env (specifically NEXT_PUBLIC_* variables)
 * 
 * Outputs:
 * - Validated `env` configuration object
 * 
 * Interacting Files / Modules:
 * - src.lib.api
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

/**
 * File: vitest.config.ts
 * 
 * Purpose:
 * Configures the Vitest testing framework for the React application.
 * 
 * Key Functionalities:
 * - Load Vite React plugin
 * - Configure testing environment (jsdom) and global variables
 * - Define setup files and path aliases for testing
 * 
 * Inputs:
 * - None
 * 
 * Outputs:
 * - Vitest configuration object
 * 
 * Interacting Files / Modules:
 * - vitest.setup.ts
 */
import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";
import path from "path";

export default defineConfig({
  plugins: [react()],
  test: {
    environment: "jsdom",
    globals: true,
    include: ["src/**/*.test.{ts,tsx}"],
    setupFiles: ["./vitest.setup.ts"],
  },
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
});

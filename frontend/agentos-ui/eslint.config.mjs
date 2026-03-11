/**
 * File: eslint.config.mjs
 * 
 * Purpose:
 * Configures ESLint rules and ignores for the Next.js frontend application.
 * 
 * Key Functionalities:
 * - Import and apply `eslint-config-next` base configurations for TypeScript and Web Vitals
 * - Define global ignore patterns for build outputs and auto-generated files
 * 
 * Inputs:
 * - None
 * 
 * Outputs:
 * - Flat ESLint configuration array
 * 
 * Interacting Files / Modules:
 * - None
 */
import { defineConfig, globalIgnores } from "eslint/config";
import nextVitals from "eslint-config-next/core-web-vitals";
import nextTs from "eslint-config-next/typescript";

const eslintConfig = defineConfig([
  ...nextVitals,
  ...nextTs,
  // Override default ignores of eslint-config-next.
  globalIgnores([
    // Default ignores of eslint-config-next:
    ".next/**",
    "out/**",
    "build/**",
    "next-env.d.ts",
  ]),
]);

export default eslintConfig;

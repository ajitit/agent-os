/**
 * File: next.config.ts
 * 
 * Purpose:
 * Configures the Next.js application, including compiler settings and security headers.
 * 
 * Key Functionalities:
 * - Enable React Compiler
 * - Configure strict HTTP security headers (X-Frame-Options, X-Content-Type-Options, Referrer-Policy)
 * 
 * Inputs:
 * - Next.js build and runtime environments
 * 
 * Outputs:
 * - NextConfig object
 * 
 * Interacting Files / Modules:
 * - None
 */
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "standalone",
  reactCompiler: true,
  poweredByHeader: false,
  async headers() {
    return [
      {
        source: "/:path*",
        headers: [
          { key: "X-DNS-Prefetch-Control", value: "on" },
          { key: "X-Frame-Options", value: "SAMEORIGIN" },
          { key: "X-Content-Type-Options", value: "nosniff" },
          { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
        ],
      },
    ];
  },
};

export default nextConfig;

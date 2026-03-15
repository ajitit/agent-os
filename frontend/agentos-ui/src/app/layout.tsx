/**
 * File: layout.tsx
 * 
 * Purpose:
 * Defines the root HTML and body structure for the entire Next.js application,
 * integrating global fonts, styles, and persistent UI components like the Navbar.
 * 
 * Key Functionalities:
 * - Configure global fonts (Geist Sans, Geist Mono)
 * - Define default application metadata (title, description) for SEO/sharing
 * - Wrap all child pages with the root `html`, `body`, and `<Nav />` component
 * 
 * Inputs:
 * - Child page components rendered by Next.js router
 * 
 * Outputs:
 * - Persistent root React layout
 * 
 * Interacting Files / Modules:
 * - src.components.Nav
 * - globals.css
 */
import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import { Sidebar } from "@/components/Sidebar";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Vishwakarma | Enterprise Multi-Agent AI Platform",
  description: "Orchestrate autonomous multi-agent workflows with modern AI infrastructure",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} flex min-h-screen bg-zinc-50 antialiased dark:bg-zinc-950`}
      >
        <Sidebar />
        <div className="flex-1 min-w-0 overflow-y-auto">
          {children}
        </div>
      </body>
    </html>
  );
}

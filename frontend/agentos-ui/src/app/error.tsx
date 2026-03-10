/**
 * File: error.tsx
 * 
 * Purpose:
 * Defines a global error boundary for the Next.js application, catching unhandled
 * runtime exceptions to prevent full app crashes.
 * 
 * Key Functionalities:
 * - Render a user-friendly error fallback screen
 * - Log errors to the browser console for debugging
 * - Provide a "Try again" button to attempt a route reset
 * 
 * Inputs:
 * - `error`: The caught JavaScript Error object
 * - `reset`: Function to clear the error boundary and re-render the segment
 * 
 * Outputs:
 * - React error boundary component
 * 
 * Interacting Files / Modules:
 * - None
 */
"use client";

import { useEffect } from "react";

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    // Log to monitoring service in production
    console.error("Application error:", error);
  }, [error]);

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-zinc-50 px-4 dark:bg-zinc-950">
      <div className="max-w-md text-center">
        <h1 className="text-2xl font-semibold text-zinc-900 dark:text-zinc-100">
          Something went wrong
        </h1>
        <p className="mt-2 text-zinc-600 dark:text-zinc-400">
          An unexpected error occurred. Please try again.
        </p>
        <button
          onClick={reset}
          className="mt-6 rounded-full bg-zinc-900 px-6 py-2.5 text-sm font-medium text-white transition hover:bg-zinc-800 dark:bg-zinc-100 dark:text-zinc-900 dark:hover:bg-zinc-200"
        >
          Try again
        </button>
      </div>
    </div>
  );
}

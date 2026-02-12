"use client";

import React from "react";
import { Button } from "@/components/ui/button";

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  React.useEffect(() => {
    // Log error to error reporting service
    console.error("Application error:", error);
  }, [error]);

  return (
    <main className="flex min-h-screen flex-col items-center justify-center bg-gradient-to-b from-zinc-950 via-neutral-900 to-zinc-950 px-4">
      <div className="space-y-6 text-center">
        <div className="space-y-2">
          <h1 className="text-4xl font-bold text-white sm:text-5xl md:text-6xl">
            Something went wrong
          </h1>
          <p className="mx-auto max-w-md text-lg text-zinc-400">
            We encountered an unexpected error. Please try again.
          </p>
        </div>

        <div className="flex flex-col gap-3 sm:flex-row sm:justify-center">
          <Button
            onClick={reset}
            size="lg"
            className="bg-blue-500 text-white hover:bg-blue-600"
          >
            Try Again
          </Button>
          <Button
            asChild
            size="lg"
            variant="outline"
            className="border-zinc-700 text-zinc-300 hover:bg-zinc-800"
          >
            <a href="/">Go Home</a>
          </Button>
        </div>

        {process.env.NODE_ENV === "development" && error.message && (
          <div className="mx-auto mt-8 max-w-2xl rounded-lg border border-red-900/50 bg-red-950/20 p-4 text-left">
            <p className="font-mono text-sm text-red-400">{error.message}</p>
          </div>
        )}
      </div>

      {/* Decorative gradient orb */}
      <div className="pointer-events-none absolute left-1/2 top-1/2 h-96 w-96 -translate-x-1/2 -translate-y-1/2 rounded-full bg-red-500/10 blur-3xl"></div>
    </main>
  );
}

import React from "react";
import Link from "next/link";
import { Button } from "@/components/ui/button";

export default function NotFound() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center bg-gradient-to-b from-zinc-950 via-neutral-900 to-zinc-950 px-4">
      <div className="space-y-6 text-center">
        <div className="space-y-2">
          <h1 className="text-6xl font-bold text-white sm:text-7xl md:text-8xl">404</h1>
          <h2 className="text-2xl font-semibold text-zinc-300 sm:text-3xl">Page not found</h2>
          <p className="mx-auto max-w-md text-zinc-400">
            The page you're looking for doesn't exist or has been moved.
          </p>
        </div>

        <div className="flex flex-col gap-3 sm:flex-row sm:justify-center">
          <Button asChild size="lg" className="bg-blue-500 text-white hover:bg-blue-600">
            <Link href="/">Go Home</Link>
          </Button>
          <Button asChild size="lg" variant="outline" className="border-zinc-700 text-zinc-300 hover:bg-zinc-800">
            <Link href="/login">Sign In</Link>
          </Button>
        </div>
      </div>

      {/* Decorative gradient orb */}
      <div className="pointer-events-none absolute left-1/2 top-1/2 h-96 w-96 -translate-x-1/2 -translate-y-1/2 rounded-full bg-blue-500/10 blur-3xl"></div>
    </main>
  );
}

import React from "react";

export default function Loading() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-b from-zinc-950 via-neutral-900 to-zinc-950">
      <div className="flex flex-col items-center space-y-4">
        <div className="h-12 w-12 animate-spin rounded-full border-4 border-zinc-800 border-t-blue-500"></div>
        <p className="text-sm text-zinc-400">Loading...</p>
      </div>
    </div>
  );
}

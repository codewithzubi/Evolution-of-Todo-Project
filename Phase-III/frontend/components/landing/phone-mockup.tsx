import React from "react";
import { CheckCircle, Circle } from "lucide-react";

export function PhoneMockup() {
  return (
    <div className="relative mx-auto w-full max-w-[700px]">
      {/* Soft gradient background */}
      <div className="absolute inset-0 -z-10 rounded-3xl bg-gradient-to-br from-blue-500/20 via-purple-500/10 to-transparent blur-3xl"></div>

      {/* Dashboard screenshot - Minimal style */}
      <div className="relative overflow-hidden rounded-2xl border border-zinc-800/50 bg-zinc-950 shadow-[0_20px_70px_-15px_rgba(0,0,0,0.8)]">
        {/* Dashboard preview */}
        <div className="flex h-[500px]">
          {/* Sidebar */}
          <div className="w-48 border-r border-zinc-800 bg-zinc-900/30 p-4">
            <div className="mb-6">
              <div className="text-sm font-semibold text-white">My Tasks</div>
            </div>
            <div className="space-y-2">
              <div className="rounded-lg bg-blue-500/20 px-3 py-2">
                <div className="text-sm font-medium text-blue-400">All Tasks</div>
              </div>
              <div className="rounded-lg px-3 py-2 transition-colors hover:bg-zinc-800/50">
                <div className="text-sm text-zinc-400">Pending</div>
              </div>
              <div className="rounded-lg px-3 py-2 transition-colors hover:bg-zinc-800/50">
                <div className="text-sm text-zinc-400">Completed</div>
              </div>
            </div>
          </div>

          {/* Task cards */}
          <div className="flex-1 space-y-4 overflow-y-auto p-6">
            {/* Task 1 - Pending */}
            <div className="rounded-xl border border-zinc-800 bg-zinc-900/50 p-4 transition-all hover:border-zinc-700 hover:bg-zinc-900/80">
              <div className="flex items-start gap-3">
                <Circle className="mt-0.5 h-5 w-5 flex-shrink-0 text-zinc-500" />
                <div className="flex-1 space-y-2">
                  <div className="text-base font-medium text-white">Buy groceries</div>
                  <div className="text-sm text-zinc-400">Milk, eggs, bread, and vegetables</div>
                  <div className="flex items-center gap-2">
                    <span className="inline-flex items-center rounded-full bg-orange-500/20 px-2.5 py-1 text-xs font-medium text-orange-400">
                      Pending
                    </span>
                    <span className="text-xs text-zinc-500">Due today</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Task 2 - Completed */}
            <div className="rounded-xl border border-zinc-800 bg-zinc-900/50 p-4 transition-all hover:border-zinc-700 hover:bg-zinc-900/80">
              <div className="flex items-start gap-3">
                <CheckCircle className="mt-0.5 h-5 w-5 flex-shrink-0 text-green-500" />
                <div className="flex-1 space-y-2">
                  <div className="text-base font-medium text-white line-through opacity-60">
                    Finish quarterly report
                  </div>
                  <div className="text-sm text-zinc-400 line-through opacity-60">
                    Q4 summary and analysis
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="inline-flex items-center rounded-full bg-green-500/20 px-2.5 py-1 text-xs font-medium text-green-400">
                      Completed
                    </span>
                    <span className="text-xs text-zinc-500">2 hours ago</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Task 3 - Pending */}
            <div className="rounded-xl border border-zinc-800 bg-zinc-900/50 p-4 transition-all hover:border-zinc-700 hover:bg-zinc-900/80">
              <div className="flex items-start gap-3">
                <Circle className="mt-0.5 h-5 w-5 flex-shrink-0 text-zinc-500" />
                <div className="flex-1 space-y-2">
                  <div className="text-base font-medium text-white">Call dentist for appointment</div>
                  <div className="flex items-center gap-2">
                    <span className="inline-flex items-center rounded-full bg-orange-500/20 px-2.5 py-1 text-xs font-medium text-orange-400">
                      Pending
                    </span>
                    <span className="text-xs text-zinc-500">Tomorrow</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Task 4 - Pending */}
            <div className="rounded-xl border border-zinc-800 bg-zinc-900/50 p-4 transition-all hover:border-zinc-700 hover:bg-zinc-900/80">
              <div className="flex items-start gap-3">
                <Circle className="mt-0.5 h-5 w-5 flex-shrink-0 text-zinc-500" />
                <div className="flex-1 space-y-2">
                  <div className="text-base font-medium text-white">Review project proposal</div>
                  <div className="text-sm text-zinc-400">Check budget and timeline</div>
                  <div className="flex items-center gap-2">
                    <span className="inline-flex items-center rounded-full bg-orange-500/20 px-2.5 py-1 text-xs font-medium text-orange-400">
                      Pending
                    </span>
                    <span className="text-xs text-zinc-500">Next week</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

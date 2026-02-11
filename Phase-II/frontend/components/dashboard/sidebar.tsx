"use client"

import { Button } from "@/components/ui/button"
import { ListTodo, Clock, CheckCircle2 } from "lucide-react"

type FilterStatus = "all" | "pending" | "completed"

interface SidebarProps {
  activeFilter: FilterStatus
  onFilterChange: (status: FilterStatus) => void
}

export function Sidebar({ activeFilter, onFilterChange }: SidebarProps) {
  const filters: { label: string; value: FilterStatus; icon: React.ReactNode }[] = [
    { label: "All Tasks", value: "all", icon: <ListTodo className="w-4 h-4" /> },
    { label: "Pending", value: "pending", icon: <Clock className="w-4 h-4" /> },
    { label: "Completed", value: "completed", icon: <CheckCircle2 className="w-4 h-4" /> },
  ]

  return (
    <aside className="w-64 bg-gray-800/50 backdrop-blur-sm border-r border-gray-700/50 p-4 hidden md:block">
      <h2 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-4 px-3">
        Filters
      </h2>
      <div className="space-y-1">
        {filters.map((filter) => {
          const isActive = activeFilter === filter.value
          return (
            <Button
              key={filter.value}
              onClick={() => onFilterChange(filter.value)}
              variant="ghost"
              className={`w-full justify-start text-left gap-3 transition-all duration-200 ${
                isActive
                  ? "bg-gradient-to-r from-blue-600 to-blue-700 text-white shadow-lg shadow-blue-500/20 hover:from-blue-700 hover:to-blue-800"
                  : "text-gray-400 hover:text-white hover:bg-gray-700/50"
              }`}
            >
              {filter.icon}
              <span className="font-medium">{filter.label}</span>
            </Button>
          )
        })}
      </div>
    </aside>
  )
}

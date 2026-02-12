"use client"

import React from "react"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { ThemeToggle } from "@/components/theme-toggle"
import { Circle } from "lucide-react"

export function Navbar() {
  return (
    <nav className="fixed top-0 z-50 w-full border-b border-white/10 bg-gradient-to-r from-purple-900/90 via-blue-900/90 to-purple-900/90 backdrop-blur-md dark:from-purple-900/90 dark:via-blue-900/90 dark:to-purple-900/90">
      <div className="container mx-auto flex h-16 items-center justify-between px-4">
        {/* Left - Logo */}
        <Link href="/" className="flex items-center gap-2 transition-opacity hover:opacity-80">
          <div className="flex h-8 w-8 items-center justify-center rounded-full bg-purple-500">
            <Circle className="h-4 w-4 text-white" fill="currentColor" />
          </div>
          <span className="text-xl font-bold text-white">Taskly</span>
        </Link>

        {/* Center - Navigation Links */}
        <div className="hidden items-center gap-8 md:flex">
          <Link
            href="#home"
            className="text-sm font-medium text-white transition-colors hover:text-purple-300"
          >
            Home
          </Link>
          <Link
            href="#features"
            className="text-sm font-medium text-white/80 transition-colors hover:text-white"
          >
            Features
          </Link>
          <Link
            href="#pricing"
            className="text-sm font-medium text-white/80 transition-colors hover:text-white"
          >
            Pricing
          </Link>
          <Link
            href="#docs"
            className="text-sm font-medium text-white/80 transition-colors hover:text-white"
          >
            Docs
          </Link>
        </div>

        {/* Right - Theme Toggle + Buttons */}
        <div className="flex items-center gap-3">
          {/* Theme Toggle */}
          <ThemeToggle />

          {/* Sign In Button */}
          <Button
            asChild
            variant="outline"
            className="hidden border-white/30 text-white hover:bg-white/10 hover:text-white sm:inline-flex"
          >
            <Link href="/login">Sign in</Link>
          </Button>

          {/* Get Started Button */}
          <Button
            asChild
            className="bg-purple-600 text-white hover:bg-purple-700"
          >
            <Link href="/login">Get Started</Link>
          </Button>
        </div>
      </div>
    </nav>
  )
}

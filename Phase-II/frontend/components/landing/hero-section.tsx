import React from "react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { PhoneMockup } from "./phone-mockup";
import { SocialIcons } from "./social-icons";
import { Users, CheckCircle2, Globe } from "lucide-react";

export function HeroSection() {
  return (
    <section
      className="relative min-h-screen overflow-hidden bg-gradient-to-b from-zinc-950 via-neutral-900 to-zinc-950"
      aria-labelledby="hero-heading"
    >
      <div className="container mx-auto px-4 py-20 md:py-32">
        <div className="grid items-center gap-12 lg:grid-cols-2 lg:gap-16">
          {/* Left side - Headline, CTA, and Stats */}
          <div className="space-y-8 text-center lg:text-left">
            <div className="space-y-4 animate-fade-in">
              <h1
                id="hero-heading"
                className="text-4xl font-bold tracking-tight text-white sm:text-5xl md:text-6xl lg:text-7xl"
              >
                Never forget a task again.
              </h1>
              <p className="text-xl text-zinc-400 sm:text-2xl md:text-3xl animate-fade-in animate-delay-100">
                Simple. Powerful. Yours.
              </p>
            </div>

            {/* Two buttons side by side */}
            <div className="flex flex-col gap-4 sm:flex-row sm:justify-center lg:justify-start animate-fade-in animate-delay-200">
              <Button
                asChild
                size="lg"
                className="min-h-[44px] min-w-[44px] bg-blue-500 text-base font-semibold text-white hover:bg-blue-600 sm:text-lg"
              >
                <Link href="/login" aria-label="Get started free with Phase II Todo">
                  Get Started Free
                </Link>
              </Button>
              <Button
                asChild
                size="lg"
                variant="outline"
                className="min-h-[44px] min-w-[44px] border-zinc-700 text-base font-semibold text-zinc-300 hover:bg-zinc-800 hover:text-white sm:text-lg"
              >
                <Link href="#demo" aria-label="Watch 45 second demo video">
                  Watch 45s Demo
                </Link>
              </Button>
            </div>

            {/* Stats row */}
            <div className="flex flex-col gap-6 sm:flex-row sm:gap-8 sm:justify-center lg:justify-start animate-fade-in animate-delay-300">
              <div className="flex items-center gap-2 text-zinc-400">
                <Users className="h-5 w-5 text-blue-400" />
                <span className="text-sm font-medium">50K+ active users</span>
              </div>
              <div className="flex items-center gap-2 text-zinc-400">
                <CheckCircle2 className="h-5 w-5 text-green-400" />
                <span className="text-sm font-medium">2.3M tasks completed</span>
              </div>
              <div className="flex items-center gap-2 text-zinc-400">
                <Globe className="h-5 w-5 text-purple-400" />
                <span className="text-sm font-medium">Always available</span>
              </div>
            </div>
          </div>

          {/* Right side - Phone Mockup + Social Icons */}
          <div className="flex flex-col items-center gap-8 animate-slide-up animate-delay-300">
            <div
              role="img"
              aria-label="Phone mockup showing the task management dashboard interface"
            >
              <PhoneMockup />
            </div>
            <SocialIcons />
          </div>
        </div>
      </div>

      {/* Decorative gradient orbs */}
      <div className="pointer-events-none absolute left-1/4 top-1/4 h-96 w-96 rounded-full bg-blue-500/10 blur-3xl" aria-hidden="true"></div>
      <div className="pointer-events-none absolute bottom-1/4 right-1/4 h-96 w-96 rounded-full bg-purple-500/10 blur-3xl" aria-hidden="true"></div>
    </section>
  );
}

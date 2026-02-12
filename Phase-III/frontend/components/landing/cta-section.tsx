import React from "react";
import Link from "next/link";
import { Button } from "@/components/ui/button";

export function CTASection() {
  return (
    <section
      className="relative bg-gradient-to-b from-zinc-950 via-zinc-900 to-zinc-950 py-20 md:py-32"
      aria-labelledby="cta-heading"
    >
      <div className="container mx-auto px-4">
        <div className="flex flex-col items-center space-y-8 text-center">
          <div className="space-y-4">
            <h2
              id="cta-heading"
              className="text-3xl font-bold tracking-tight text-white sm:text-4xl md:text-5xl"
            >
              Ready to get organized?
            </h2>
            <p className="mx-auto max-w-2xl text-lg text-zinc-400 sm:text-xl">
              Join thousands of users who have transformed their productivity.
            </p>
          </div>

          <Button
            asChild
            size="lg"
            className="min-h-[44px] min-w-[44px] bg-blue-500 text-base font-semibold text-white hover:bg-blue-600 sm:text-lg"
          >
            <Link href="/login" aria-label="Get started free with Phase II Todo">
              Get Started Free
            </Link>
          </Button>
        </div>
      </div>

      {/* Decorative gradient orb */}
      <div className="pointer-events-none absolute left-1/2 top-1/2 h-96 w-96 -translate-x-1/2 -translate-y-1/2 rounded-full bg-blue-500/10 blur-3xl" aria-hidden="true"></div>
    </section>
  );
}

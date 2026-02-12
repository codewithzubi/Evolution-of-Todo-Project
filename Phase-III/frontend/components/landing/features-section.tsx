import React from "react";
import { CheckCircle, Filter, Lock, Globe } from "lucide-react";
import { FeatureCard } from "./feature-card";

export function FeaturesSection() {
  const features = [
    {
      icon: CheckCircle,
      title: "Simple Task Management",
      description: "Add, edit, complete tasks effortlessly. Stay organized without the complexity.",
    },
    {
      icon: Filter,
      title: "Smart Filtering",
      description: "View all, pending, or completed tasks. Find what you need instantly.",
    },
    {
      icon: Lock,
      title: "Secure & Private",
      description: "Your tasks, your data, fully isolated. Privacy-first architecture.",
    },
    {
      icon: Globe,
      title: "Always Accessible",
      description: "Works on any device, anywhere. Your tasks sync seamlessly.",
    },
  ];

  return (
    <section
      className="relative bg-zinc-950 py-20 md:py-32"
      aria-labelledby="features-heading"
    >
      <div className="container mx-auto px-4">
        <div className="mb-12 space-y-4 text-center">
          <h2
            id="features-heading"
            className="text-3xl font-bold tracking-tight text-white sm:text-4xl md:text-5xl"
          >
            Everything you need to stay organized
          </h2>
          <p className="mx-auto max-w-2xl text-lg text-zinc-400 sm:text-xl">
            Powerful features designed to help you focus on what matters most.
          </p>
        </div>

        <div
          className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4"
          role="list"
          aria-label="Product features"
        >
          {features.map((feature, index) => (
            <div
              key={feature.title}
              className="animate-fade-in"
              style={{ animationDelay: `${index * 100}ms` }}
              role="listitem"
            >
              <FeatureCard
                icon={feature.icon}
                title={feature.title}
                description={feature.description}
              />
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

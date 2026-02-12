import React from "react";
import { LucideIcon } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";

interface FeatureCardProps {
  icon: LucideIcon;
  title: string;
  description: string;
}

export function FeatureCard({ icon: Icon, title, description }: FeatureCardProps) {
  return (
    <Card className="group border-zinc-800 bg-zinc-900/50 transition-all duration-300 hover:border-zinc-700 hover:bg-zinc-900/80 hover:shadow-lg hover:shadow-blue-500/10">
      <CardContent className="flex flex-col items-center space-y-4 p-6 text-center">
        <div className="rounded-full bg-blue-500/10 p-3 transition-colors duration-300 group-hover:bg-blue-500/20">
          <Icon className="h-6 w-6 text-blue-400" />
        </div>
        <h3 className="text-lg font-semibold text-white">{title}</h3>
        <p className="text-sm text-zinc-400">{description}</p>
      </CardContent>
    </Card>
  );
}

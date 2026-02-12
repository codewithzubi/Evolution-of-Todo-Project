import React from "react";
import { Github, Linkedin, Twitter } from "lucide-react";

export function SocialIcons() {
  const socials = [
    {
      icon: Github,
      href: "https://github.com",
      label: "GitHub",
      hoverColor: "hover:text-purple-400 hover:shadow-[0_0_20px_rgba(168,85,247,0.6)]",
    },
    {
      icon: Linkedin,
      href: "https://linkedin.com",
      label: "LinkedIn",
      hoverColor: "hover:text-blue-400 hover:shadow-[0_0_20px_rgba(59,130,246,0.6)]",
    },
    {
      icon: Twitter,
      href: "https://twitter.com",
      label: "Twitter",
      hoverColor: "hover:text-cyan-400 hover:shadow-[0_0_20px_rgba(34,211,238,0.6)]",
    },
  ];

  return (
    <div className="fixed right-4 top-1/2 z-40 flex -translate-y-1/2 flex-col items-center gap-6 md:relative md:right-auto md:top-auto md:translate-y-0">
      {socials.map((social) => {
        const Icon = social.icon;
        return (
          <a
            key={social.label}
            href={social.href}
            target="_blank"
            rel="noopener noreferrer"
            aria-label={social.label}
            className={`group flex h-12 w-12 items-center justify-center rounded-full border border-zinc-700/50 bg-zinc-900/50 text-zinc-400 backdrop-blur-sm transition-all duration-300 hover:scale-110 hover:border-transparent ${social.hoverColor}`}
          >
            <Icon className="h-5 w-5 transition-transform duration-300 group-hover:scale-110" />
          </a>
        );
      })}
    </div>
  );
}

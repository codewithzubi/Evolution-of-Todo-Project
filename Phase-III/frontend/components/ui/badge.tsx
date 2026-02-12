import * as React from "react"
import { cva, type VariantProps } from "class-variance-authority"

import { cn } from "@/lib/utils"

const badgeVariants = cva(
  "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2",
  {
    variants: {
      variant: {
        default:
          "border-transparent bg-primary text-primary-foreground hover:bg-primary/80",
        secondary:
          "border-transparent bg-secondary text-secondary-foreground hover:bg-secondary/80",
        destructive:
          "border-transparent bg-destructive text-destructive-foreground hover:bg-destructive/80",
        outline: "text-foreground",
        success:
          "border-transparent bg-green-900 text-green-100 hover:bg-green-900/80",
        warning:
          "border-transparent bg-orange-900 text-orange-100 hover:bg-orange-900/80",
        info:
          "border-transparent bg-blue-900 text-blue-100 hover:bg-blue-900/80",
        purple:
          "border-transparent bg-purple-900 text-purple-100 hover:bg-purple-900/80",
        pink:
          "border-transparent bg-pink-900 text-pink-100 hover:bg-pink-900/80",
        gray:
          "border-transparent bg-gray-700 text-gray-200 hover:bg-gray-700/80",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  }
)

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, ...props }: BadgeProps) {
  return (
    <div className={cn(badgeVariants({ variant }), className)} {...props} />
  )
}

export { Badge, badgeVariants }

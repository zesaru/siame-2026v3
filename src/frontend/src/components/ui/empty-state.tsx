/**
 * SIAME 2026v3 - Empty State
 * Componente para mostrar estados vacios con ilustracion y acciones
 */

import * as React from "react"
import { LucideIcon } from "lucide-react"
import { cn } from "@/lib/utils"
import { Button } from "./button"

interface EmptyStateProps {
  icon?: LucideIcon
  title: string
  description?: string
  action?: {
    label: string
    onClick: () => void
  }
  className?: string
}

const EmptyState = React.forwardRef<HTMLDivElement, EmptyStateProps>(
  ({ icon: Icon, title, description, action, className }, ref) => {
    return (
      <div
        ref={ref}
        className={cn(
          "flex min-h-[400px] flex-col items-center justify-center space-y-4 text-center",
          className
        )}
      >
        {Icon && (
          <div className="rounded-full bg-muted p-6">
            <Icon className="h-10 w-10 text-muted-foreground" />
          </div>
        )}
        <div className="space-y-2">
          <h3 className="text-lg font-semibold text-foreground">{title}</h3>
          {description && (
            <p className="text-sm text-muted-foreground max-w-md">
              {description}
            </p>
          )}
        </div>
        {action && (
          <Button onClick={action.onClick} className="mt-4">
            {action.label}
          </Button>
        )}
      </div>
    )
  }
)
EmptyState.displayName = "EmptyState"

export { EmptyState, type EmptyStateProps }

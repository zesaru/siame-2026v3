/**
 * SIAME 2026v3 - Label Component
 * Componente de label mejorado con indicador de requerido y help text
 */

import * as React from "react"
import { cn } from "@/lib/utils"

export interface LabelProps
  extends React.LabelHTMLAttributes<HTMLLabelElement> {
  required?: boolean
  helpText?: string
}

const Label = React.forwardRef<HTMLLabelElement, LabelProps>(
  ({ className, children, required, helpText, ...props }, ref) => {
    return (
      <div className="space-y-1">
        <label
          ref={ref}
          className={cn(
            "text-sm font-medium leading-none",
            "text-foreground",
            "peer-disabled:cursor-not-allowed peer-disabled:opacity-70",
            className
          )}
          {...props}
        >
          {children}
          {required && (
            <span className="ml-1 text-destructive" aria-label="required">
              *
            </span>
          )}
        </label>
        {helpText && (
          <p className="text-xs text-muted-foreground">{helpText}</p>
        )}
      </div>
    )
  }
)
Label.displayName = "Label"

export { Label }

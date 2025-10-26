/**
 * SIAME 2026v3 - Spinner
 * Componente de spinner para indicar carga
 */

import * as React from "react"
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "@/lib/utils"
import { Loader2 } from "lucide-react"

const spinnerVariants = cva("animate-spin", {
  variants: {
    size: {
      sm: "h-4 w-4",
      default: "h-6 w-6",
      lg: "h-8 w-8",
      xl: "h-12 w-12",
    },
    variant: {
      default: "text-primary",
      muted: "text-muted-foreground",
      white: "text-white",
    },
  },
  defaultVariants: {
    size: "default",
    variant: "default",
  },
})

export interface SpinnerProps
  extends React.HTMLAttributes<SVGElement>,
    VariantProps<typeof spinnerVariants> {}

const Spinner = React.forwardRef<SVGSVGElement, SpinnerProps>(
  ({ className, size, variant, ...props }, ref) => {
    return (
      <Loader2
        ref={ref}
        className={cn(spinnerVariants({ size, variant, className }))}
        {...props}
      />
    )
  }
)
Spinner.displayName = "Spinner"

// Componente de loading page completo
const LoadingPage = ({ message = "Cargando..." }: { message?: string }) => {
  return (
    <div className="flex min-h-[400px] flex-col items-center justify-center space-y-4">
      <Spinner size="xl" />
      <p className="text-sm text-muted-foreground">{message}</p>
    </div>
  )
}

// Componente de loading inline
const LoadingInline = ({ message }: { message?: string }) => {
  return (
    <div className="flex items-center space-x-2">
      <Spinner size="sm" />
      {message && <span className="text-sm text-muted-foreground">{message}</span>}
    </div>
  )
}

export { Spinner, spinnerVariants, LoadingPage, LoadingInline }

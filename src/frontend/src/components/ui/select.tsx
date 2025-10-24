import * as React from "react"
import { cn } from "@/lib/utils"

export interface SelectProps
  extends React.SelectHTMLAttributes<HTMLSelectElement> {}

const Select = React.forwardRef<HTMLSelectElement, SelectProps>(
  ({ className, children, ...props }, ref) => {
    return (
      <select
        className={cn(
          "flex h-10 w-full rounded-md border border-gray-300 dark:border-gray-700",
          "bg-white dark:bg-gray-800 px-3 py-2 text-sm",
          "ring-offset-white dark:ring-offset-gray-950",
          "focus-visible:outline-none focus-visible:ring-2",
          "focus-visible:ring-blue-500 dark:focus-visible:ring-blue-400",
          "focus-visible:ring-offset-2",
          "disabled:cursor-not-allowed disabled:opacity-50",
          "[&>option]:bg-white [&>option]:dark:bg-gray-800",
          className
        )}
        ref={ref}
        {...props}
      >
        {children}
      </select>
    )
  }
)
Select.displayName = "Select"

export { Select }

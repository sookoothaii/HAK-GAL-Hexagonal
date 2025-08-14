import * as React from "react"
import { CheckCircle2 } from "lucide-react"
import { cn } from "@/lib/utils"

const RadioGroup = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement> & { value?: string; onValueChange?: (value: string) => void }
>(({ className, value, onValueChange, ...props }, ref) => {
  return (
    <div 
      ref={ref} 
      className={cn("grid gap-2", className)} 
      {...props}
    />
  )
})
RadioGroup.displayName = "RadioGroup"

const RadioGroupItem = React.forwardRef<
  HTMLInputElement,
  React.InputHTMLAttributes<HTMLInputElement>
>(({ className, ...props }, ref) => {
  const groupValue = React.useContext(RadioGroupContext)
  
  return (
    <input
      type="radio"
      ref={ref}
      className={cn(
        "h-4 w-4 rounded-full border border-primary text-primary focus:ring-2 focus:ring-primary focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50",
        className
      )}
      checked={groupValue === props.value}
      onChange={(e) => {
        if (e.target.checked && props.onChange) {
          props.onChange(e)
        }
      }}
      {...props}
    />
  )
})
RadioGroupItem.displayName = "RadioGroupItem"

// Simple context for radio group
const RadioGroupContext = React.createContext<string | undefined>(undefined)

// Simple implementation for now
export { RadioGroup, RadioGroupItem }

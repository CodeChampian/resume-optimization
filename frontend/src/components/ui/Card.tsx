import { cn } from '@/lib/utils'

interface CardProps {
  children: React.ReactNode
  className?: string
}

function Card({ children, className }: CardProps) {
  return (
    <div className={cn('rounded-lg border bg-white', className)}>
      {children}
    </div>
  )
}

Card.Header = function CardHeader({ children, className }: { children: React.ReactNode; className?: string }) {
  return <div className={cn('border-b px-6 py-4', className)}>{children}</div>
}

Card.Body = function CardBody({ children, className }: { children: React.ReactNode; className?: string }) {
  return <div className={cn('px-6 py-4', className)}>{children}</div>
}

Card.Footer = function CardFooter({ children, className }: { children: React.ReactNode; className?: string }) {
  return <div className={cn('border-t px-6 py-4', className)}>{children}</div>
}

export { Card }

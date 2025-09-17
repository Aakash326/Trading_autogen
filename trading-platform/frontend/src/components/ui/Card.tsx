import React from 'react'
import { motion } from 'framer-motion'
import { clsx } from 'clsx'

interface CardProps {
  children: React.ReactNode
  className?: string
  hover?: boolean
  onClick?: () => void
}

export const Card: React.FC<CardProps> = ({
  children,
  className,
  hover = false,
  onClick
}) => {
  const MotionDiv = onClick ? motion.button : motion.div

  return (
    <MotionDiv
      whileHover={hover ? { scale: 1.02, y: -2 } : undefined}
      whileTap={onClick ? { scale: 0.98 } : undefined}
      className={clsx(
        'bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-sm',
        hover && 'hover:shadow-md transition-shadow cursor-pointer',
        onClick && 'focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2',
        className
      )}
      onClick={onClick}
      type={onClick ? 'button' : undefined}
    >
      {children}
    </MotionDiv>
  )
}

export const CardHeader: React.FC<{ children: React.ReactNode; className?: string }> = ({
  children,
  className
}) => (
  <div className={clsx('px-6 py-4 border-b border-gray-200 dark:border-gray-700', className)}>
    {children}
  </div>
)

export const CardContent: React.FC<{ children: React.ReactNode; className?: string }> = ({
  children,
  className
}) => (
  <div className={clsx('px-6 py-4', className)}>
    {children}
  </div>
)

export const CardFooter: React.FC<{ children: React.ReactNode; className?: string }> = ({
  children,
  className
}) => (
  <div className={clsx('px-6 py-4 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900 rounded-b-lg', className)}>
    {children}
  </div>
)
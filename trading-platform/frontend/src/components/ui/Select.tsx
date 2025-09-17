import React, { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { ChevronDownIcon } from '@heroicons/react/24/outline'
import { clsx } from 'clsx'

interface SelectOption {
  value: string
  label: string
  description?: string
}

interface SelectProps {
  options: SelectOption[]
  value?: string
  placeholder?: string
  onChange: (value: string) => void
  className?: string
  disabled?: boolean
}

export const Select: React.FC<SelectProps> = ({
  options,
  value,
  placeholder = 'Select an option...',
  onChange,
  className,
  disabled = false
}) => {
  const [isOpen, setIsOpen] = useState(false)
  const [selectedOption, setSelectedOption] = useState<SelectOption | null>(
    options.find(option => option.value === value) || null
  )
  const selectRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (selectRef.current && !selectRef.current.contains(event.target as Node)) {
        setIsOpen(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  useEffect(() => {
    setSelectedOption(options.find(option => option.value === value) || null)
  }, [value, options])

  const handleSelect = (option: SelectOption) => {
    setSelectedOption(option)
    onChange(option.value)
    setIsOpen(false)
  }

  return (
    <div ref={selectRef} className={clsx('relative', className)}>
      <motion.button
        whileTap={{ scale: 0.99 }}
        type="button"
        className={clsx(
          'relative w-full bg-white border border-gray-300 rounded-md shadow-sm py-2 px-3 text-left cursor-default focus:outline-none focus:ring-1 focus:ring-primary-500 focus:border-primary-500',
          disabled && 'bg-gray-100 cursor-not-allowed',
          className
        )}
        onClick={() => !disabled && setIsOpen(!isOpen)}
        disabled={disabled}
      >
        <span className="block truncate">
          {selectedOption ? selectedOption.label : placeholder}
        </span>
        <span className="absolute inset-y-0 right-0 flex items-center pr-2 pointer-events-none">
          <ChevronDownIcon
            className={clsx(
              'h-5 w-5 text-gray-400 transition-transform',
              isOpen && 'transform rotate-180'
            )}
          />
        </span>
      </motion.button>

      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.2 }}
            className="absolute z-10 mt-1 w-full bg-white shadow-lg max-h-60 rounded-md py-1 text-base ring-1 ring-black ring-opacity-5 overflow-auto focus:outline-none"
          >
            {options.map((option) => (
              <motion.button
                key={option.value}
                whileHover={{ backgroundColor: '#f3f4f6' }}
                type="button"
                className={clsx(
                  'w-full text-left cursor-default select-none relative py-2 px-3',
                  selectedOption?.value === option.value
                    ? 'text-primary-600 bg-primary-50'
                    : 'text-gray-900'
                )}
                onClick={() => handleSelect(option)}
              >
                <span className="block font-medium">{option.label}</span>
                {option.description && (
                  <span className="block text-sm text-gray-500 mt-1">
                    {option.description}
                  </span>
                )}
              </motion.button>
            ))}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
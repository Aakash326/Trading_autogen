import React from 'react'
import { motion } from 'framer-motion'
import { 
  ChartBarIcon, 
  BellIcon, 
  Cog6ToothIcon,
  WifiIcon
} from '@heroicons/react/24/outline'
import { useStore } from '../../store/useStore'

export const Header: React.FC = () => {
  const { websocketConnected, isAnalysisRunning, currentAnalysis } = useStore()

  return (
    <header className="bg-white border-b border-gray-200 px-6 py-4">
      <div className="flex justify-between items-center max-w-7xl mx-auto">
        {/* Logo and Title */}
        <div className="flex items-center space-x-3">
          <motion.div
            whileHover={{ rotate: 360 }}
            transition={{ duration: 0.5 }}
            className="h-8 w-8 bg-primary-600 rounded-lg flex items-center justify-center"
          >
            <ChartBarIcon className="h-5 w-5 text-white" />
          </motion.div>
          <div>
            <h1 className="text-xl font-bold text-gray-900">
              Trading Analysis Platform
            </h1>
            <p className="text-sm text-gray-500">
              AI-Powered Investment Intelligence
            </p>
          </div>
        </div>

        {/* Status and Actions */}
        <div className="flex items-center space-x-4">
          {/* Analysis Status */}
          {isAnalysisRunning && currentAnalysis && (
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              className="flex items-center space-x-2 px-3 py-1.5 bg-blue-50 border border-blue-200 rounded-lg"
            >
              <div className="h-2 w-2 bg-blue-500 rounded-full animate-pulse" />
              <span className="text-sm text-blue-700 font-medium">
                Analyzing {currentAnalysis.stock_symbol}
              </span>
            </motion.div>
          )}

          {/* WebSocket Status */}
          <div className="flex items-center space-x-2">
            <WifiIcon 
              className={`h-5 w-5 ${
                websocketConnected ? 'text-green-500' : 'text-red-500'
              }`} 
            />
            <span className={`text-sm ${
              websocketConnected ? 'text-green-600' : 'text-red-600'
            }`}>
              {websocketConnected ? 'Connected' : 'Disconnected'}
            </span>
          </div>

          {/* Notifications */}
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="p-2 text-gray-400 hover:text-gray-600 relative"
          >
            <BellIcon className="h-6 w-6" />
            {/* Notification badge */}
            <span className="absolute -top-1 -right-1 h-3 w-3 bg-red-500 rounded-full"></span>
          </motion.button>

          {/* Settings */}
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="p-2 text-gray-400 hover:text-gray-600"
          >
            <Cog6ToothIcon className="h-6 w-6" />
          </motion.button>
        </div>
      </div>
    </header>
  )
}
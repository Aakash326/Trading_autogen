import React from 'react'
import { motion } from 'framer-motion'
import {
  HomeIcon,
  ChartBarIcon,
  DocumentTextIcon,
  Cog6ToothIcon,
  QuestionMarkCircleIcon,
  ClockIcon
} from '@heroicons/react/24/outline'
import { useStore } from '../../store/useStore'

interface SidebarProps {
  currentView: string
  onViewChange: (view: string) => void
}

const NAVIGATION_ITEMS = [
  { id: 'home', name: 'Dashboard', icon: HomeIcon },
  { id: 'analysis', name: 'New Analysis', icon: ChartBarIcon },
  { id: 'history', name: 'History', icon: ClockIcon },
  { id: 'reports', name: 'Reports', icon: DocumentTextIcon },
  { id: 'settings', name: 'Settings', icon: Cog6ToothIcon },
  { id: 'help', name: 'Help', icon: QuestionMarkCircleIcon }
]

export const Sidebar: React.FC<SidebarProps> = ({ currentView, onViewChange }) => {
  const { analysisHistory, isAnalysisRunning } = useStore()

  return (
    <div className="bg-gray-900 text-white w-64 min-h-screen flex flex-col">
      {/* Navigation */}
      <nav className="flex-1 px-4 py-6 space-y-2">
        {NAVIGATION_ITEMS.map((item) => {
          const Icon = item.icon
          const isActive = currentView === item.id
          const isDisabled = isAnalysisRunning && item.id === 'analysis'
          
          return (
            <motion.button
              key={item.id}
              whileHover={!isDisabled ? { x: 4 } : {}}
              whileTap={!isDisabled ? { scale: 0.95 } : {}}
              onClick={() => !isDisabled && onViewChange(item.id)}
              disabled={isDisabled}
              className={`w-full flex items-center space-x-3 px-3 py-2 rounded-lg text-left transition-colors ${
                isActive
                  ? 'bg-primary-600 text-white'
                  : isDisabled
                  ? 'text-gray-500 cursor-not-allowed'
                  : 'text-gray-300 hover:bg-gray-800 hover:text-white'
              }`}
            >
              <Icon className="h-5 w-5" />
              <span className="font-medium">{item.name}</span>
              {item.id === 'history' && analysisHistory.length > 0 && (
                <span className="ml-auto bg-gray-700 text-gray-300 text-xs px-2 py-1 rounded-full">
                  {analysisHistory.length}
                </span>
              )}
              {item.id === 'analysis' && isAnalysisRunning && (
                <div className="ml-auto h-2 w-2 bg-blue-400 rounded-full animate-pulse" />
              )}
            </motion.button>
          )
        })}
      </nav>

      {/* Recent Activity */}
      <div className="px-4 py-4 border-t border-gray-800">
        <h3 className="text-sm font-medium text-gray-400 mb-3">Recent Analysis</h3>
        <div className="space-y-2">
          {analysisHistory.slice(0, 3).map((analysis) => (
            <motion.div
              key={analysis.id}
              whileHover={{ x: 4 }}
              className="flex items-center space-x-2 p-2 rounded text-sm text-gray-300 hover:bg-gray-800 cursor-pointer"
            >
              <div className={`h-2 w-2 rounded-full ${
                analysis.status === 'completed' ? 'bg-green-400' :
                analysis.status === 'running' ? 'bg-blue-400' :
                analysis.status === 'error' ? 'bg-red-400' : 'bg-gray-400'
              }`} />
              <div className="flex-1 min-w-0">
                <div className="font-medium truncate">{analysis.stock_symbol}</div>
                <div className="text-xs text-gray-500 truncate">
                  {analysis.analysis_type}
                </div>
              </div>
            </motion.div>
          ))}
          
          {analysisHistory.length === 0 && (
            <div className="text-sm text-gray-500 italic">
              No recent analysis
            </div>
          )}
        </div>
      </div>

      {/* Footer */}
      <div className="px-4 py-4 border-t border-gray-800">
        <div className="text-xs text-gray-500">
          <div>Trading Analysis Platform</div>
          <div>Powered by AI Agents</div>
        </div>
      </div>
    </div>
  )
}
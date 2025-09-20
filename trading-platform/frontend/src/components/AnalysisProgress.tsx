import React, { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { CheckIcon, ExclamationTriangleIcon, StopIcon, ChevronDownIcon, ChevronUpIcon } from '@heroicons/react/24/outline'
import { Card, CardContent, CardHeader } from './ui/Card'
import { Button } from './ui/Button'
import { AnalysisPhase } from '../types'
import { useStore } from '../store/useStore'
import { api } from '../utils/api'

const AGENT_ICONS: Record<string, string> = {
  'ComplianceOfficer': '⚖️',
  'MarketDataAnalyst': '📊',
  'QuantitativeAnalyst': '🔢',
  'RiskManager': '⚠️',
  'StrategyDeveloper': '💡',
  'ResearchAgent': '🔬',
  'ReportGenerator': '📄',
  'default': '🤖'
}

const getAgentIcon = (agentName: string): string => {
  const cleanName = agentName.replace(/\s+/g, '')
  return AGENT_ICONS[cleanName] || AGENT_ICONS.default
}

interface AnalysisProgressProps {
  phases: AnalysisPhase[]
  isRunning: boolean
}

export const AnalysisProgress: React.FC<AnalysisProgressProps> = ({
  phases,
  isRunning
}) => {
  const [expandedPhases, setExpandedPhases] = useState<Set<string>>(new Set())
  const { 
    selectedStock, 
    selectedAnalysisType, 
    selectedWorkflow,
    currentAnalysis,
    isCancelling,
    setCancelling,
    setAnalysisRunning,
    setCurrentAnalysis
  } = useStore()

  const togglePhaseExpansion = (phaseId: string) => {
    const newExpanded = new Set(expandedPhases)
    if (newExpanded.has(phaseId)) {
      newExpanded.delete(phaseId)
    } else {
      newExpanded.add(phaseId)
    }
    setExpandedPhases(newExpanded)
  }

  const handleStopAnalysis = async () => {
    if (!currentAnalysis?.id || isCancelling) return

    try {
      setCancelling(true)
      await api.cancelAnalysis(currentAnalysis.id)
      
      // Update the analysis status to cancelled
      setCurrentAnalysis({
        ...currentAnalysis,
        status: 'cancelled'
      })
      setAnalysisRunning(false)
    } catch (error) {
      console.error('Failed to cancel analysis:', error)
    } finally {
      setCancelling(false)
    }
  }

  const getStatusColor = (status: AnalysisPhase['status']) => {
    switch (status) {
      case 'completed':
        return 'text-green-600 bg-green-100'
      case 'running':
        return 'text-blue-600 bg-blue-100'
      case 'error':
        return 'text-red-600 bg-red-100'
      default:
        return 'text-gray-600 bg-gray-100'
    }
  }

  const getStatusIcon = (status: AnalysisPhase['status']) => {
    switch (status) {
      case 'completed':
        return <CheckIcon className="h-4 w-4" />
      case 'error':
        return <ExclamationTriangleIcon className="h-4 w-4" />
      case 'running':
        return (
          <div className="h-4 w-4 animate-spin">
            <div className="h-full w-full border-2 border-current border-t-transparent rounded-full" />
          </div>
        )
      default:
        return <div className="h-2 w-2 bg-current rounded-full" />
    }
  }

  const completedPhases = phases.filter(p => p.status === 'completed').length
  
  // Use expected total phases based on workflow type, not actual phases.length
  const expectedTotalPhases = selectedWorkflow === '13-agent' ? 16 : 
                              selectedWorkflow === '6-agent' ? 9 : 10
  
  // For progress calculation, use the expected total or actual phases if more than expected
  const totalPhases = Math.max(expectedTotalPhases, phases.length)
  const progressPercentage = totalPhases > 0 ? (completedPhases / totalPhases) * 100 : 0

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-bold text-gray-900">
                Analysis Progress
              </h2>
              {selectedStock && selectedAnalysisType && (
                <div className="text-gray-600 mt-1">
                  Analyzing <strong>{selectedStock.symbol}</strong> for{' '}
                  <strong>{selectedAnalysisType.name}</strong>
                </div>
              )}
            </div>
            <div className="flex items-center space-x-3">
              <span className="text-sm text-gray-500">
                {selectedWorkflow} workflow
              </span>
              {isRunning && currentAnalysis && (
                <Button
                  variant="destructive"
                  size="sm"
                  onClick={handleStopAnalysis}
                  loading={isCancelling}
                  className="flex items-center space-x-2"
                >
                  <StopIcon className="h-4 w-4" />
                  <span>{isCancelling ? 'Stopping...' : 'Stop Analysis'}</span>
                </Button>
              )}
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {/* Progress Bar */}
          <div className="mb-6">
            <div className="flex justify-between text-sm text-gray-600 mb-2">
              <span>Progress</span>
              <span>{completedPhases}/{totalPhases} phases completed</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <motion.div
                className="bg-primary-600 h-2 rounded-full"
                initial={{ width: 0 }}
                animate={{ width: `${progressPercentage}%` }}
                transition={{ duration: 0.5 }}
              />
            </div>
            <div className="text-right text-sm text-gray-500 mt-1">
              {progressPercentage.toFixed(0)}% complete
            </div>
          </div>

          {/* Phase List */}
          <div className="space-y-3">
            <AnimatePresence>
              {phases.map((phase, index) => (
                <motion.div
                  key={`${phase.phase}-${index}`}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: 20 }}
                  transition={{ delay: index * 0.1 }}
                  className="flex items-start space-x-3 p-3 rounded-lg border border-gray-200 bg-gray-50"
                >
                  <div className="text-2xl">
                    {getAgentIcon(phase.agent)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between">
                      <h4 className="font-medium text-gray-900 truncate">
                        {phase.agent}
                      </h4>
                      <div className={`flex items-center space-x-1 px-2 py-1 rounded-full text-xs ${getStatusColor(phase.status)}`}>
                        {getStatusIcon(phase.status)}
                        <span className="capitalize ml-1">{phase.status}</span>
                      </div>
                    </div>
                    <p className="text-sm text-gray-600 mt-1">
                      {phase.phase}
                    </p>
                    {phase.content && (
                      <div className="mt-2">
                        <div className="p-2 bg-white rounded border text-sm text-gray-700">
                          {phase.content.length > 200 ? (
                            <div>
                              <div>
                                {expandedPhases.has(`${phase.phase}-${index}`) 
                                  ? phase.content 
                                  : `${phase.content.substring(0, 200)}...`
                                }
                              </div>
                              <button
                                onClick={() => togglePhaseExpansion(`${phase.phase}-${index}`)}
                                className="mt-2 flex items-center text-blue-600 hover:text-blue-800 text-xs font-medium"
                              >
                                {expandedPhases.has(`${phase.phase}-${index}`) ? (
                                  <>
                                    <ChevronUpIcon className="h-3 w-3 mr-1" />
                                    Show less
                                  </>
                                ) : (
                                  <>
                                    <ChevronDownIcon className="h-3 w-3 mr-1" />
                                    Show more
                                  </>
                                )}
                              </button>
                            </div>
                          ) : (
                            phase.content
                          )}
                        </div>
                      </div>
                    )}
                    {phase.timestamp && (
                      <div className="text-xs text-gray-400 mt-1">
                        {new Date(phase.timestamp).toLocaleTimeString()}
                      </div>
                    )}
                  </div>
                </motion.div>
              ))}
            </AnimatePresence>
          </div>

          {/* Loading State */}
          {isRunning && phases.length === 0 && (
            <div className="text-center py-8">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500 mb-4"></div>
              <p className="text-gray-600">Initializing analysis...</p>
              <p className="text-sm text-gray-500 mt-1">
                Setting up {selectedWorkflow} workflow
              </p>
            </div>
          )}

          {/* Completion State */}
          {!isRunning && phases.length > 0 && completedPhases === phases.length && currentAnalysis?.status !== 'cancelled' && (
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              className="text-center py-6 bg-green-50 rounded-lg border border-green-200"
            >
              <CheckIcon className="h-12 w-12 text-green-600 mx-auto mb-2" />
              <h3 className="text-lg font-semibold text-green-800">
                Analysis Complete!
              </h3>
              <p className="text-green-600 text-sm">
                All agents have finished their analysis
              </p>
            </motion.div>
          )}

          {/* Cancelled State */}
          {currentAnalysis?.status === 'cancelled' && (
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              className="text-center py-6 bg-red-50 rounded-lg border border-red-200"
            >
              <StopIcon className="h-12 w-12 text-red-600 mx-auto mb-2" />
              <h3 className="text-lg font-semibold text-red-800">
                Analysis Cancelled
              </h3>
              <p className="text-red-600 text-sm">
                The analysis was stopped by user request
              </p>
            </motion.div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { 
  DocumentTextIcon, 
  ChartBarIcon, 
  ExclamationTriangleIcon,
  CheckCircleIcon,
  ClipboardDocumentIcon
} from '@heroicons/react/24/outline'
import { Card, CardContent, CardHeader } from './ui/Card'
import { Button } from './ui/Button'
import { AnalysisResult } from '../types'

interface AnalysisResultsProps {
  result: AnalysisResult
}

export const AnalysisResults: React.FC<AnalysisResultsProps> = ({ result }) => {
  const [activeTab, setActiveTab] = useState<'summary' | 'details' | 'phases'>('summary')
  const [copiedSection, setCopiedSection] = useState<string | null>(null)

  const copyToClipboard = async (text: string, section: string) => {
    try {
      await navigator.clipboard.writeText(text)
      setCopiedSection(section)
      setTimeout(() => setCopiedSection(null), 2000)
    } catch (err) {
      console.error('Failed to copy text: ', err)
    }
  }

  const getRecommendationColor = (recommendation?: string) => {
    if (!recommendation) return 'text-gray-600'
    
    const lower = recommendation.toLowerCase()
    if (lower.includes('buy') || lower.includes('strong buy')) return 'text-green-600'
    if (lower.includes('sell') || lower.includes('strong sell')) return 'text-red-600'
    if (lower.includes('hold')) return 'text-yellow-600'
    return 'text-gray-600'
  }

  const getConfidenceColor = (score?: number) => {
    if (!score) return 'text-gray-600'
    if (score >= 80) return 'text-green-600'
    if (score >= 60) return 'text-yellow-600'
    return 'text-red-600'
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString()
  }

  const tabs = [
    { id: 'summary', name: 'Summary', icon: DocumentTextIcon },
    { id: 'details', name: 'Detailed Analysis', icon: ChartBarIcon },
    { id: 'phases', name: 'Agent Phases', icon: ExclamationTriangleIcon }
  ]

  return (
    <div className="space-y-6">
      {/* Header */}
      <Card>
        <CardHeader>
          <div className="flex justify-between items-start">
            <div>
              <h2 className="text-2xl font-bold text-gray-900">
                Analysis Results
              </h2>
              <div className="flex items-center space-x-4 mt-2 text-sm text-gray-600">
                <span>Symbol: <strong>{result.stock_symbol}</strong></span>
                <span>Type: <strong>{result.analysis_type}</strong></span>
                <span>Workflow: <strong>{result.workflow_type}</strong></span>
              </div>
            </div>
            <div className="text-right">
              <div className={`text-lg font-semibold ${getRecommendationColor(result.recommendation)}`}>
                {result.recommendation || 'Analysis Complete'}
              </div>
              {result.confidence_score && (
                <div className={`text-sm ${getConfidenceColor(result.confidence_score)}`}>
                  Confidence: {result.confidence_score}%
                </div>
              )}
            </div>
          </div>
        </CardHeader>
      </Card>

      {/* Key Metrics */}
      {(result.recommendation || result.confidence_score) && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {result.recommendation && (
            <Card>
              <CardContent className="p-6 text-center">
                <CheckCircleIcon className={`h-8 w-8 mx-auto mb-2 ${getRecommendationColor(result.recommendation)}`} />
                <h3 className="font-semibold text-gray-900">Recommendation</h3>
                <p className={`text-lg font-medium ${getRecommendationColor(result.recommendation)}`}>
                  {result.recommendation}
                </p>
              </CardContent>
            </Card>
          )}
          
          {result.confidence_score && (
            <Card>
              <CardContent className="p-6 text-center">
                <ChartBarIcon className={`h-8 w-8 mx-auto mb-2 ${getConfidenceColor(result.confidence_score)}`} />
                <h3 className="font-semibold text-gray-900">Confidence Score</h3>
                <p className={`text-lg font-medium ${getConfidenceColor(result.confidence_score)}`}>
                  {result.confidence_score}%
                </p>
              </CardContent>
            </Card>
          )}
          
          <Card>
            <CardContent className="p-6 text-center">
              <DocumentTextIcon className="h-8 w-8 mx-auto mb-2 text-blue-600" />
              <h3 className="font-semibold text-gray-900">Analysis Time</h3>
              <p className="text-lg font-medium text-blue-600">
                {result.completed_at ? (
                  `${Math.round((new Date(result.completed_at).getTime() - new Date(result.created_at).getTime()) / 1000)}s`
                ) : (
                  'In Progress'
                )}
              </p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Tab Navigation */}
      <div className="border-b border-gray-200">
        <nav className="flex space-x-8">
          {tabs.map((tab) => {
            const Icon = tab.icon
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`py-2 px-1 border-b-2 font-medium text-sm flex items-center space-x-2 ${
                  activeTab === tab.id
                    ? 'border-primary-500 text-primary-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <Icon className="h-4 w-4" />
                <span>{tab.name}</span>
              </button>
            )
          })}
        </nav>
      </div>

      {/* Tab Content */}
      <Card>
        <CardContent className="p-6">
          {activeTab === 'summary' && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="space-y-4"
            >
              <div className="flex justify-between items-start">
                <h3 className="text-lg font-semibold text-gray-900">Executive Summary</h3>
                {result.summary && (
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => copyToClipboard(result.summary!, 'summary')}
                  >
                    <ClipboardDocumentIcon className="h-4 w-4 mr-1" />
                    {copiedSection === 'summary' ? 'Copied!' : 'Copy'}
                  </Button>
                )}
              </div>
              <div className="prose max-w-none">
                {result.summary ? (
                  <div className="bg-gray-50 p-4 rounded-lg whitespace-pre-wrap">
                    {result.summary}
                  </div>
                ) : (
                  <p className="text-gray-500 italic">
                    Summary will be available once the analysis is complete.
                  </p>
                )}
              </div>
            </motion.div>
          )}

          {activeTab === 'details' && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="space-y-4"
            >
              <h3 className="text-lg font-semibold text-gray-900">Detailed Analysis</h3>
              <div className="space-y-4">
                {result.phases.filter(phase => phase.content).map((phase, index) => (
                  <div key={index} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex justify-between items-start mb-2">
                      <h4 className="font-medium text-gray-900">{phase.agent}</h4>
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => copyToClipboard(phase.content!, `phase-${index}`)}
                      >
                        <ClipboardDocumentIcon className="h-4 w-4" />
                        {copiedSection === `phase-${index}` ? 'Copied!' : ''}
                      </Button>
                    </div>
                    <p className="text-sm text-gray-600 mb-2">{phase.phase}</p>
                    <div className="bg-gray-50 p-3 rounded text-sm whitespace-pre-wrap">
                      {phase.content}
                    </div>
                  </div>
                ))}
                {result.phases.filter(phase => phase.content).length === 0 && (
                  <p className="text-gray-500 italic">
                    Detailed analysis will be available as agents complete their work.
                  </p>
                )}
              </div>
            </motion.div>
          )}

          {activeTab === 'phases' && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="space-y-4"
            >
              <h3 className="text-lg font-semibold text-gray-900">Agent Phase Timeline</h3>
              <div className="space-y-3">
                {result.phases.map((phase, index) => (
                  <div key={index} className="flex items-start space-x-3 p-3 border border-gray-200 rounded-lg">
                    <div className={`mt-1 h-3 w-3 rounded-full ${
                      phase.status === 'completed' ? 'bg-green-500' :
                      phase.status === 'running' ? 'bg-blue-500' :
                      phase.status === 'error' ? 'bg-red-500' : 'bg-gray-300'
                    }`} />
                    <div className="flex-1">
                      <div className="flex justify-between items-start">
                        <h4 className="font-medium text-gray-900">{phase.agent}</h4>
                        <span className={`text-xs px-2 py-1 rounded capitalize ${
                          phase.status === 'completed' ? 'bg-green-100 text-green-800' :
                          phase.status === 'running' ? 'bg-blue-100 text-blue-800' :
                          phase.status === 'error' ? 'bg-red-100 text-red-800' : 'bg-gray-100 text-gray-800'
                        }`}>
                          {phase.status}
                        </span>
                      </div>
                      <p className="text-sm text-gray-600 mt-1">{phase.phase}</p>
                      {phase.timestamp && (
                        <p className="text-xs text-gray-400 mt-1">
                          {formatDate(phase.timestamp)}
                        </p>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </motion.div>
          )}
        </CardContent>
      </Card>

      {/* Metadata */}
      <Card>
        <CardContent className="p-4">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            <div>
              <span className="text-gray-500">Created:</span>
              <div className="font-medium">{formatDate(result.created_at)}</div>
            </div>
            {result.completed_at && (
              <div>
                <span className="text-gray-500">Completed:</span>
                <div className="font-medium">{formatDate(result.completed_at)}</div>
              </div>
            )}
            <div>
              <span className="text-gray-500">Status:</span>
              <div className={`font-medium capitalize ${
                result.status === 'completed' ? 'text-green-600' :
                result.status === 'running' ? 'text-blue-600' :
                result.status === 'error' ? 'text-red-600' : 'text-gray-600'
              }`}>
                {result.status}
              </div>
            </div>
            <div>
              <span className="text-gray-500">Analysis ID:</span>
              <div className="font-mono text-xs">{result.id}</div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
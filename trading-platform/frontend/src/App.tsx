import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Header } from './components/layout/Header'
import { Sidebar } from './components/layout/Sidebar'
import { StockSelector } from './components/StockSelector'
import { AnalysisTypeSelector } from './components/AnalysisTypeSelector'
import { AnalysisProgress } from './components/AnalysisProgress'
import { AnalysisResults } from './components/AnalysisResults'
import { Button } from './components/ui/Button'
import { Select } from './components/ui/Select'
import { Card, CardContent, CardHeader } from './components/ui/Card'
import { useStore } from './store/useStore'
import { useWebSocket } from './hooks/useWebSocket'
import { api } from './utils/api'

const App: React.FC = () => {
  const [currentView, setCurrentView] = useState('analysis')
  const [step, setStep] = useState(1)
  
  const {
    selectedStock,
    selectedAnalysisType,
    selectedWorkflow,
    setSelectedWorkflow,
    currentAnalysis,
    setCurrentAnalysis,
    isAnalysisRunning,
    setAnalysisRunning,
    analysisHistory,
    addToHistory,
    resetSelection
  } = useStore()

  const { isConnected } = useWebSocket()

  const workflowOptions = [
    { value: '6-agent', label: '6-Agent Workflow (Best) - Recommended', description: 'Optimized performance with essential agents' },
    { value: '7-agent', label: '7-Agent Workflow', description: 'Faster analysis with core agents' },
    { value: '13-agent', label: '13-Agent Workflow', description: 'Comprehensive analysis with all agents' }
  ]

  const canProceedToStep2 = selectedStock !== null
  const canProceedToStep3 = canProceedToStep2 && selectedAnalysisType !== null
  const canStartAnalysis = canProceedToStep3 && !isAnalysisRunning

  const handleStartAnalysis = async () => {
    if (!selectedStock || !selectedAnalysisType) return

    try {
      setAnalysisRunning(true)
      
      const response = await api.startAnalysis({
        stock_symbol: selectedStock.symbol,
        analysis_type: selectedAnalysisType.id,
        workflow_type: selectedWorkflow
      })

      // Create initial analysis result
      const newAnalysis = {
        id: response.analysis_id,
        stock_symbol: selectedStock.symbol,
        analysis_type: selectedAnalysisType.id,
        workflow_type: selectedWorkflow,
        status: 'running' as const,
        phases: [],
        created_at: new Date().toISOString()
      }

      setCurrentAnalysis(newAnalysis)
      setStep(4) // Move to progress view

      // Start polling for updates as backup to WebSocket
      const pollForUpdates = async () => {
        try {
          const analysisStatus = await api.getAnalysis(response.analysis_id)
          setCurrentAnalysis(analysisStatus)
          
          if (analysisStatus.status === 'completed' || analysisStatus.status === 'cancelled' || analysisStatus.status === 'error') {
            setAnalysisRunning(false)
            if (analysisStatus.status === 'completed') {
              addToHistory(analysisStatus)
            }
          } else {
            // Continue polling every 2 seconds
            setTimeout(pollForUpdates, 2000)
          }
        } catch (error) {
          console.error('Failed to poll analysis status:', error)
          setAnalysisRunning(false)
        }
      }

      // Start polling immediately
      setTimeout(pollForUpdates, 1000)
      
    } catch (error) {
      console.error('Failed to start analysis:', error)
      setAnalysisRunning(false)
    }
  }

  const handleNewAnalysis = () => {
    resetSelection()
    setStep(1)
    setCurrentView('analysis')
  }

  const renderAnalysisFlow = () => {
    return (
      <div className="max-w-6xl mx-auto space-y-8">
        {/* Progress Steps */}
        <div className="flex items-center justify-center space-x-4 mb-8">
          {[1, 2, 3, 4].map((stepNumber) => (
            <div key={stepNumber} className="flex items-center">
              <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                step >= stepNumber 
                  ? 'bg-primary-600 text-white' 
                  : 'bg-gray-200 text-gray-600'
              }`}>
                {stepNumber}
              </div>
              {stepNumber < 4 && (
                <div className={`w-16 h-0.5 ${
                  step > stepNumber ? 'bg-primary-600' : 'bg-gray-200'
                }`} />
              )}
            </div>
          ))}
        </div>

        <AnimatePresence mode="wait">
          {step === 1 && (
            <motion.div
              key="step1"
              initial={{ opacity: 0, x: 50 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -50 }}
              transition={{ duration: 0.3 }}
            >
              <StockSelector />
              <div className="flex justify-end mt-6">
                <Button
                  onClick={() => setStep(2)}
                  disabled={!canProceedToStep2}
                  size="lg"
                >
                  Next: Choose Analysis Type
                </Button>
              </div>
            </motion.div>
          )}

          {step === 2 && (
            <motion.div
              key="step2"
              initial={{ opacity: 0, x: 50 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -50 }}
              transition={{ duration: 0.3 }}
            >
              <AnalysisTypeSelector />
              <div className="flex justify-between mt-6">
                <Button
                  variant="outline"
                  onClick={() => setStep(1)}
                  size="lg"
                >
                  Back
                </Button>
                <Button
                  onClick={() => setStep(3)}
                  disabled={!canProceedToStep3}
                  size="lg"
                >
                  Next: Configure Analysis
                </Button>
              </div>
            </motion.div>
          )}

          {step === 3 && (
            <motion.div
              key="step3"
              initial={{ opacity: 0, x: 50 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -50 }}
              transition={{ duration: 0.3 }}
            >
              <Card>
                <CardHeader>
                  <h2 className="text-2xl font-bold text-gray-900">
                    Configure Analysis
                  </h2>
                  <p className="text-gray-600">
                    Review your selections and choose the analysis workflow
                  </p>
                </CardHeader>
                <CardContent className="space-y-6">
                  {/* Selection Summary */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Selected Stock
                      </label>
                      <div className="p-3 bg-gray-50 rounded-lg">
                        <div className="font-semibold">{selectedStock?.symbol}</div>
                        <div className="text-sm text-gray-600">{selectedStock?.name}</div>
                      </div>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Analysis Type
                      </label>
                      <div className="p-3 bg-gray-50 rounded-lg">
                        <div className="font-semibold">{selectedAnalysisType?.name}</div>
                        <div className="text-sm text-gray-600">{selectedAnalysisType?.description}</div>
                      </div>
                    </div>
                  </div>

                  {/* Workflow Selection */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Analysis Workflow
                    </label>
                    <Select
                      options={workflowOptions}
                      value={selectedWorkflow}
                      onChange={(value) => setSelectedWorkflow(value as '6-agent' | '7-agent' | '13-agent')}
                      className="max-w-md"
                    />
                  </div>

                  {/* Connection Status */}
                  <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
                    <div className="flex items-center space-x-2">
                      <div className={`h-3 w-3 rounded-full ${isConnected ? 'bg-green-400' : 'bg-red-400'}`} />
                      <span className="text-sm font-medium text-blue-800">
                        {isConnected ? 'Connected to analysis server' : 'Disconnected from server'}
                      </span>
                    </div>
                    {!isConnected && (
                      <p className="text-sm text-blue-600 mt-1">
                        Real-time updates may not be available
                      </p>
                    )}
                  </div>
                </CardContent>
              </Card>

              <div className="flex justify-between mt-6">
                <Button
                  variant="outline"
                  onClick={() => setStep(2)}
                  size="lg"
                >
                  Back
                </Button>
                <Button
                  onClick={handleStartAnalysis}
                  disabled={!canStartAnalysis}
                  loading={isAnalysisRunning}
                  size="lg"
                >
                  Start Analysis
                </Button>
              </div>
            </motion.div>
          )}

          {step === 4 && currentAnalysis && (
            <motion.div
              key="step4"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3 }}
              className="space-y-6"
            >
              <AnalysisProgress 
                phases={currentAnalysis.phases}
                isRunning={isAnalysisRunning}
              />
              
              {currentAnalysis.status === 'completed' && 
               (() => {
                 // Check if we have completed phases from actual agents (not just system phases)
                 const agentPhases = currentAnalysis.phases.filter(p => 
                   p.status === 'completed' && 
                   p.agent !== 'System' && 
                   p.agent !== '7-Agent Team' && 
                   p.agent !== '13-Agent Team'
                 );
                 const expectedAgents = selectedWorkflow === '6-agent' ? 3 : selectedWorkflow === '7-agent' ? 3 : 5; // Minimum expected agent contributions
                 return agentPhases.length >= expectedAgents;
               })() && (
                <AnalysisResults result={currentAnalysis} />
              )}
              
              <div className="flex justify-center">
                <Button
                  onClick={handleNewAnalysis}
                  variant="outline"
                  size="lg"
                >
                  Start New Analysis
                </Button>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    )
  }

  const renderDashboard = () => {
    return (
      <div className="max-w-6xl mx-auto space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600 mt-2">Overview of your trading analysis activity</p>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card>
            <CardContent className="p-6 text-center">
              <div className="text-3xl font-bold text-primary-600">{analysisHistory.length}</div>
              <div className="text-gray-600">Total Analyses</div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-6 text-center">
              <div className="text-3xl font-bold text-green-600">
                {analysisHistory.filter(a => a.status === 'completed').length}
              </div>
              <div className="text-gray-600">Completed</div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-6 text-center">
              <div className="text-3xl font-bold text-blue-600">
                {isAnalysisRunning ? 1 : 0}
              </div>
              <div className="text-gray-600">Running</div>
            </CardContent>
          </Card>
        </div>

        {/* Recent Analysis */}
        <Card>
          <CardHeader>
            <h2 className="text-xl font-semibold">Recent Analysis</h2>
          </CardHeader>
          <CardContent>
            {analysisHistory.length > 0 ? (
              <div className="space-y-4">
                {analysisHistory.slice(0, 5).map((analysis) => (
                  <div key={analysis.id} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                    <div className="flex items-center space-x-4">
                      <div className={`h-3 w-3 rounded-full ${
                        analysis.status === 'completed' ? 'bg-green-400' :
                        analysis.status === 'running' ? 'bg-blue-400' :
                        analysis.status === 'error' ? 'bg-red-400' : 'bg-gray-400'
                      }`} />
                      <div>
                        <div className="font-medium">{analysis.stock_symbol}</div>
                        <div className="text-sm text-gray-600">{analysis.analysis_type}</div>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-sm text-gray-500">
                        {new Date(analysis.created_at).toLocaleDateString()}
                      </div>
                      <div className="text-sm font-medium capitalize text-gray-700">
                        {analysis.status}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8 text-gray-500">
                No analysis history yet. Start your first analysis!
              </div>
            )}
          </CardContent>
        </Card>

        {/* Quick Actions */}
        <div className="flex justify-center">
          <Button
            onClick={() => setCurrentView('analysis')}
            size="lg"
          >
            Start New Analysis
          </Button>
        </div>
      </div>
    )
  }

  const renderContent = () => {
    switch (currentView) {
      case 'home':
        return renderDashboard()
      case 'analysis':
        return renderAnalysisFlow()
      case 'history':
        return (
          <div className="max-w-6xl mx-auto">
            <h1 className="text-3xl font-bold text-gray-900 mb-6">Analysis History</h1>
            {/* History implementation */}
            <Card>
              <CardContent className="p-6">
                <p className="text-gray-500">Analysis history will be implemented here.</p>
              </CardContent>
            </Card>
          </div>
        )
      default:
        return renderDashboard()
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 flex">
      <Sidebar currentView={currentView} onViewChange={setCurrentView} />
      <div className="flex-1 flex flex-col">
        <Header />
        <main className="flex-1 p-6">
          {renderContent()}
        </main>
      </div>
    </div>
  )
}

export default App
import { create } from 'zustand'
import { devtools } from 'zustand/middleware'
import { Stock, AnalysisType, AnalysisResult } from '../types'

interface AppState {
  selectedStock: Stock | null
  selectedAnalysisType: AnalysisType | null
  selectedWorkflow: '7-agent' | '13-agent'
  currentAnalysis: AnalysisResult | null
  analysisHistory: AnalysisResult[]
  isAnalysisRunning: boolean
  websocketConnected: boolean
  isCancelling: boolean
  
  setSelectedStock: (stock: Stock | null) => void
  setSelectedAnalysisType: (type: AnalysisType | null) => void
  setSelectedWorkflow: (workflow: '7-agent' | '13-agent') => void
  setCurrentAnalysis: (analysis: AnalysisResult | null) => void
  addToHistory: (analysis: AnalysisResult) => void
  setAnalysisRunning: (running: boolean) => void
  setWebsocketConnected: (connected: boolean) => void
  setCancelling: (cancelling: boolean) => void
  updateAnalysisPhase: (analysisId: string, phaseUpdate: any) => void
  resetSelection: () => void
}

export const useStore = create<AppState>()(
  devtools(
    (set, get) => ({
      selectedStock: null,
      selectedAnalysisType: null,
      selectedWorkflow: '13-agent',
      currentAnalysis: null,
      analysisHistory: [],
      isAnalysisRunning: false,
      websocketConnected: false,
      isCancelling: false,
      
      setSelectedStock: (stock) => set({ selectedStock: stock }),
      
      setSelectedAnalysisType: (type) => set({ selectedAnalysisType: type }),
      
      setSelectedWorkflow: (workflow) => set({ selectedWorkflow: workflow }),
      
      setCurrentAnalysis: (analysis) => set({ currentAnalysis: analysis }),
      
      addToHistory: (analysis) => set((state) => ({
        analysisHistory: [analysis, ...state.analysisHistory.slice(0, 9)]
      })),
      
      setAnalysisRunning: (running) => set({ isAnalysisRunning: running }),
      
      setWebsocketConnected: (connected) => set({ websocketConnected: connected }),
      
      setCancelling: (cancelling) => set({ isCancelling: cancelling }),
      
      updateAnalysisPhase: (analysisId, phaseUpdate) => set((state) => {
        if (state.currentAnalysis?.id === analysisId) {
          const updatedPhases = [...state.currentAnalysis.phases]
          const phaseIndex = updatedPhases.findIndex(p => p.phase === phaseUpdate.phase)
          
          if (phaseIndex >= 0) {
            updatedPhases[phaseIndex] = { ...updatedPhases[phaseIndex], ...phaseUpdate }
          } else {
            updatedPhases.push(phaseUpdate)
          }
          
          return {
            currentAnalysis: {
              ...state.currentAnalysis,
              phases: updatedPhases
            }
          }
        }
        return state
      }),
      
      resetSelection: () => set({
        selectedStock: null,
        selectedAnalysisType: null,
        currentAnalysis: null,
        isAnalysisRunning: false,
        isCancelling: false
      })
    }),
    {
      name: 'trading-analysis-store',
    }
  )
)
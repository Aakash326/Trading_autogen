import { useEffect } from 'react'
import { wsManager } from '../utils/websocket'
import { useStore } from '../store/useStore'
import { WebSocketMessage } from '../types'

export const useWebSocket = () => {
  const {
    setWebsocketConnected,
    updateAnalysisPhase,
    setCurrentAnalysis,
    addToHistory,
    setAnalysisRunning,
    setCancelling
  } = useStore()

  useEffect(() => {
    const handleMessage = (message: WebSocketMessage) => {
      switch (message.type) {
        case 'phase_update':
          updateAnalysisPhase(message.analysis_id, message.data)
          break
          
        case 'analysis_complete':
          setCurrentAnalysis(message.data)
          addToHistory(message.data)
          setAnalysisRunning(false)
          setCancelling(false)
          break
          
        case 'analysis_cancelled':
          console.log('Analysis cancelled:', message.data)
          setAnalysisRunning(false)
          setCancelling(false)
          break
          
        case 'error':
          console.error('Analysis error:', message.data)
          setAnalysisRunning(false)
          setCancelling(false)
          break
          
        default:
          console.log('Unknown message type:', message.type)
      }
    }

    const handleConnectionChange = (connected: boolean) => {
      setWebsocketConnected(connected)
    }

    // Connect to WebSocket
    wsManager.connect()
    
    // Set up event listeners
    const unsubscribeMessage = wsManager.onMessage(handleMessage)
    const unsubscribeConnection = wsManager.onConnectionChange(handleConnectionChange)

    // Cleanup on unmount
    return () => {
      unsubscribeMessage()
      unsubscribeConnection()
      wsManager.disconnect()
    }
  }, [setWebsocketConnected, updateAnalysisPhase, setCurrentAnalysis, addToHistory, setAnalysisRunning])

  return {
    isConnected: wsManager.isConnected,
    send: wsManager.send.bind(wsManager)
  }
}
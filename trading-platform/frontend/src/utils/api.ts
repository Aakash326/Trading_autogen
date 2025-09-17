import { AnalysisRequest, AnalysisResult, Stock, AnalysisType, StockQuote } from '../types'

const API_BASE = '/api'

class ApiError extends Error {
  constructor(message: string, public status: number) {
    super(message)
    this.name = 'ApiError'
  }
}

async function fetchApi<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${endpoint}`, {
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
    ...options,
  })

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}))
    throw new ApiError(
      errorData.detail || `HTTP ${response.status}: ${response.statusText}`,
      response.status
    )
  }

  return response.json()
}

export const api = {
  // Stock operations
  getStocks: (): Promise<Stock[]> =>
    fetchApi('/stocks'),

  getStockQuote: (symbol: string): Promise<StockQuote> =>
    fetchApi(`/stocks/${symbol}/quote`),

  searchStocks: (query: string): Promise<Stock[]> =>
    fetchApi(`/stocks/search?q=${encodeURIComponent(query)}`),

  // Analysis types
  getAnalysisTypes: (): Promise<AnalysisType[]> =>
    fetchApi('/analysis-types'),

  // Analysis operations
  startAnalysis: (request: AnalysisRequest): Promise<{ analysis_id: string }> =>
    fetchApi('/analysis/start', {
      method: 'POST',
      body: JSON.stringify(request),
    }),

  getAnalysis: (analysisId: string): Promise<AnalysisResult> =>
    fetchApi(`/analysis/${analysisId}`),

  getAnalysisHistory: (): Promise<AnalysisResult[]> =>
    fetchApi('/analysis/history'),

  cancelAnalysis: (analysisId: string): Promise<{ success: boolean }> =>
    fetchApi(`/analysis/${analysisId}/cancel`, {
      method: 'POST',
    }),

  // Health check
  healthCheck: (): Promise<{ status: string; timestamp: string }> =>
    fetchApi('/health'),
}

export { ApiError }
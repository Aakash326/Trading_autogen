export interface Stock {
  symbol: string;
  name: string;
  price?: number;
  change?: number;
  changePercent?: number;
  marketCap?: string;
  sector?: string;
}

export interface AnalysisType {
  id: string;
  name: string;
  description: string;
  icon: string;
}

export interface AnalysisRequest {
  stock_symbol: string;
  analysis_type: string;
  workflow_type: '7-agent' | '13-agent';
}

export interface AnalysisPhase {
  phase: string;
  agent: string;
  status: 'pending' | 'running' | 'completed' | 'error';
  content?: string;
  timestamp?: string;
}

export interface AnalysisResult {
  id: string;
  stock_symbol: string;
  analysis_type: string;
  workflow_type: string;
  status: 'pending' | 'running' | 'completed' | 'error' | 'cancelled';
  phases: AnalysisPhase[];
  summary?: string;
  recommendation?: string;
  confidence_score?: number;
  created_at: string;
  completed_at?: string;
}

export interface WebSocketMessage {
  type: 'phase_update' | 'analysis_complete' | 'analysis_cancelled' | 'error';
  analysis_id: string;
  data: any;
}

export interface StockQuote {
  symbol: string;
  price: number;
  change: number;
  changePercent: number;
  volume: number;
  marketCap: string;
  pe: number;
  eps: number;
  high52w: number;
  low52w: number;
}
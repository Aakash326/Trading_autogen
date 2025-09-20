import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { MagnifyingGlassIcon } from '@heroicons/react/24/outline'
import { useQuery } from '@tanstack/react-query'
import { Card, CardContent } from './ui/Card'
import { api } from '../utils/api'
import { Stock } from '../types'
import { useStore } from '../store/useStore'

const POPULAR_STOCKS = [
  // Tech Giants
  { symbol: 'AAPL', name: 'Apple Inc.' },
  { symbol: 'MSFT', name: 'Microsoft Corporation' },
  { symbol: 'GOOGL', name: 'Alphabet Inc.' },
  { symbol: 'AMZN', name: 'Amazon.com Inc.' },
  { symbol: 'META', name: 'Meta Platforms Inc.' },
  { symbol: 'NVDA', name: 'NVIDIA Corporation' },
  { symbol: 'TSLA', name: 'Tesla, Inc.' },
  { symbol: 'NFLX', name: 'Netflix Inc.' },
  
  // Financial Services
  { symbol: 'JPM', name: 'JPMorgan Chase & Co.' },
  { symbol: 'BAC', name: 'Bank of America Corp.' },
  { symbol: 'WFC', name: 'Wells Fargo & Company' },
  { symbol: 'GS', name: 'Goldman Sachs Group Inc.' },
  { symbol: 'V', name: 'Visa Inc.' },
  { symbol: 'MA', name: 'Mastercard Inc.' },
  
  // Healthcare & Pharma
  { symbol: 'JNJ', name: 'Johnson & Johnson' },
  { symbol: 'PFE', name: 'Pfizer Inc.' },
  { symbol: 'UNH', name: 'UnitedHealth Group Inc.' },
  { symbol: 'ABBV', name: 'AbbVie Inc.' },
  
  // Consumer & Retail
  { symbol: 'WMT', name: 'Walmart Inc.' },
  { symbol: 'PG', name: 'Procter & Gamble Co.' },
  { symbol: 'KO', name: 'Coca-Cola Company' },
  { symbol: 'PEP', name: 'PepsiCo Inc.' },
  { symbol: 'HD', name: 'Home Depot Inc.' },
  
  // Transportation & Services
  { symbol: 'UBER', name: 'Uber Technologies Inc.' },
  { symbol: 'LYFT', name: 'Lyft Inc.' },
  { symbol: 'SPOT', name: 'Spotify Technology S.A.' },
  
  // Energy & Utilities
  { symbol: 'XOM', name: 'Exxon Mobil Corporation' },
  { symbol: 'CVX', name: 'Chevron Corporation' },
  
  // Aerospace & Defense
  { symbol: 'BA', name: 'Boeing Company' },
  { symbol: 'LMT', name: 'Lockheed Martin Corp.' }
]

export const StockSelector: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('')
  const [customSymbol, setCustomSymbol] = useState('')
  const { selectedStock, setSelectedStock } = useStore()

  const { data: searchResults = [], isLoading: isSearching } = useQuery({
    queryKey: ['stocks', searchQuery],
    queryFn: () => api.searchStocks(searchQuery),
    enabled: searchQuery.length >= 2,
    staleTime: 5 * 60 * 1000
  })

  const handleStockSelect = (stock: Stock) => {
    setSelectedStock(stock)
  }

  const handleCustomSymbolSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (customSymbol.trim()) {
      const stock: Stock = {
        symbol: customSymbol.toUpperCase().trim(),
        name: `Custom: ${customSymbol.toUpperCase().trim()}`
      }
      setSelectedStock(stock)
      setCustomSymbol('')
    }
  }

  const displayStocks = searchQuery.length >= 2 ? searchResults : POPULAR_STOCKS

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          Select a Stock to Analyze
        </h2>
        <p className="text-gray-600">
          Choose from popular stocks or search for any company
        </p>
      </div>

      {/* Search Input */}
      <div className="relative">
        <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
        <input
          type="text"
          placeholder="Search for stocks (e.g., Apple, TSLA, Microsoft)..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
        />
      </div>

      {/* Stock Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {displayStocks.map((stock) => (
          <Card
            key={stock.symbol}
            hover
            onClick={() => handleStockSelect(stock)}
            className={`cursor-pointer transition-all ${
              selectedStock?.symbol === stock.symbol
                ? 'ring-2 ring-primary-500 bg-primary-50'
                : ''
            }`}
          >
            <CardContent className="p-4">
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <h3 className="font-semibold text-lg text-gray-900">
                    {stock.symbol}
                  </h3>
                  <p className="text-sm text-gray-600 mt-1 line-clamp-2">
                    {stock.name}
                  </p>
                  {stock.sector && (
                    <span className="inline-block mt-2 px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded">
                      {stock.sector}
                    </span>
                  )}
                </div>
                {stock.price && (
                  <div className="text-right ml-4">
                    <div className="font-semibold text-gray-900">
                      ${stock.price.toFixed(2)}
                    </div>
                    {stock.changePercent && (
                      <div className={`text-sm ${
                        stock.changePercent >= 0 ? 'text-green-600' : 'text-red-600'
                      }`}>
                        {stock.changePercent >= 0 ? '+' : ''}
                        {stock.changePercent.toFixed(2)}%
                      </div>
                    )}
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {isSearching && (
        <div className="text-center py-8">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500"></div>
          <p className="mt-2 text-gray-600">Searching stocks...</p>
        </div>
      )}

      {searchQuery.length >= 2 && searchResults.length === 0 && !isSearching && (
        <div className="text-center py-8 text-gray-500">
          No stocks found for "{searchQuery}"
        </div>
      )}

      {/* Custom Symbol Input */}
      <Card className="border-dashed border-2 border-gray-300">
        <CardContent className="p-6">
          <h3 className="font-semibold text-gray-900 mb-3">
            Enter Custom Stock Symbol
          </h3>
          <form onSubmit={handleCustomSymbolSubmit} className="flex gap-3">
            <input
              type="text"
              placeholder="e.g., AAPL, TSLA, MSFT"
              value={customSymbol}
              onChange={(e) => setCustomSymbol(e.target.value)}
              className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              type="submit"
              className="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2"
            >
              Add
            </motion.button>
          </form>
        </CardContent>
      </Card>

      {selectedStock && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="p-4 bg-green-50 border border-green-200 rounded-lg"
        >
          <div className="flex items-center">
            <div className="h-3 w-3 bg-green-400 rounded-full mr-3"></div>
            <span className="text-green-800">
              Selected: <strong>{selectedStock.symbol}</strong> - {selectedStock.name}
            </span>
          </div>
        </motion.div>
      )}
    </div>
  )
}
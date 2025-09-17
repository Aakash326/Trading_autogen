import React from 'react'
import { motion } from 'framer-motion'
import { Card, CardContent } from './ui/Card'
import { AnalysisType } from '../types'
import { useStore } from '../store/useStore'

const ANALYSIS_TYPES: AnalysisType[] = [
  {
    id: 'buying',
    name: '💰 Buying Decision',
    description: 'Should I buy this stock now? Complete investment analysis.',
    icon: '💰'
  },
  {
    id: 'selling',
    name: '💸 Selling Decision',
    description: 'Should I sell this stock now? Exit strategy analysis.',
    icon: '💸'
  },
  {
    id: 'health',
    name: '🏥 General Health Check',
    description: 'Overall company and stock health assessment.',
    icon: '🏥'
  },
  {
    id: '5day',
    name: '📈 Next 5-Day Outlook',
    description: 'Short-term price movement and catalysts for next 5 days.',
    icon: '📈'
  },
  {
    id: 'growth',
    name: '🚀 Growth Potential Analysis',
    description: 'Long-term growth prospects and investment potential.',
    icon: '🚀'
  },
  {
    id: 'risk',
    name: '⚠️ Risk Assessment',
    description: 'Comprehensive risk analysis and downside protection.',
    icon: '⚠️'
  },
  {
    id: 'sector',
    name: '🏢 Sector Comparison',
    description: 'How does this company compare to its sector peers?',
    icon: '🏢'
  },
  {
    id: 'options',
    name: '📊 Options Strategy',
    description: 'Options trading opportunities and strategies analysis.',
    icon: '📊'
  },
  {
    id: 'esg',
    name: '🌱 ESG & Sustainability',
    description: 'Environmental, Social, and Governance analysis.',
    icon: '🌱'
  },
  {
    id: 'earnings',
    name: '📅 Earnings Forecast',
    description: 'Upcoming earnings analysis and price impact prediction.',
    icon: '📅'
  }
]

export const AnalysisTypeSelector: React.FC = () => {
  const { selectedAnalysisType, setSelectedAnalysisType } = useStore()

  const handleTypeSelect = (type: AnalysisType) => {
    setSelectedAnalysisType(type)
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          Select Analysis Type
        </h2>
        <p className="text-gray-600">
          Choose what kind of analysis you'd like to perform
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {ANALYSIS_TYPES.map((type) => (
          <Card
            key={type.id}
            hover
            onClick={() => handleTypeSelect(type)}
            className={`cursor-pointer transition-all ${
              selectedAnalysisType?.id === type.id
                ? 'ring-2 ring-primary-500 bg-primary-50'
                : ''
            }`}
          >
            <CardContent className="p-6">
              <div className="flex items-start space-x-4">
                <div className="text-3xl">{type.icon}</div>
                <div className="flex-1">
                  <h3 className="font-semibold text-lg text-gray-900 mb-2">
                    {type.name}
                  </h3>
                  <p className="text-gray-600 text-sm leading-relaxed">
                    {type.description}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {selectedAnalysisType && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="p-4 bg-blue-50 border border-blue-200 rounded-lg"
        >
          <div className="flex items-center">
            <div className="text-2xl mr-3">{selectedAnalysisType.icon}</div>
            <div>
              <span className="text-blue-800 font-medium">
                Selected: {selectedAnalysisType.name}
              </span>
              <p className="text-blue-600 text-sm mt-1">
                {selectedAnalysisType.description}
              </p>
            </div>
          </div>
        </motion.div>
      )}
    </div>
  )
}
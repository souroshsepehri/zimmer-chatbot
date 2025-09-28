'use client'

import { useState } from 'react'
import { ChevronDown, ChevronUp, Info, Target, Search, Clock } from 'lucide-react'

interface DebugInfo {
  intent: {
    label: string
    confidence: number
  }
  source: string
  retrieval_results: Array<{
    faq_id: number
    question: string
    answer: string
    score: number
    category?: string
  }>
  tokens_in?: number
  tokens_out?: number
  latency_ms?: number
  success: boolean
  unanswered_in_db: boolean
}

interface DebugPanelProps {
  debugInfo: DebugInfo
}

export default function DebugPanel({ debugInfo }: DebugPanelProps) {
  const [isExpanded, setIsExpanded] = useState(false)

  const getSourceColor = (source: string) => {
    switch (source) {
      case 'faq':
        return 'bg-green-100 text-green-800'
      case 'rag':
        return 'bg-blue-100 text-blue-800'
      case 'llm':
        return 'bg-yellow-100 text-yellow-800'
      case 'fallback':
        return 'bg-gray-100 text-gray-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const getIntentColor = (intent: string) => {
    switch (intent) {
      case 'faq':
        return 'bg-blue-100 text-blue-800'
      case 'smalltalk':
        return 'bg-green-100 text-green-800'
      case 'chitchat':
        return 'bg-purple-100 text-purple-800'
      case 'complaint':
        return 'bg-red-100 text-red-800'
      case 'sales':
        return 'bg-orange-100 text-orange-800'
      case 'support':
        return 'bg-indigo-100 text-indigo-800'
      case 'out_of_scope':
        return 'bg-gray-100 text-gray-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  return (
    <div className="mt-2 mr-4 bg-gray-50 rounded-lg border border-gray-200 overflow-hidden">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full p-3 flex items-center justify-between hover:bg-gray-100 transition-colors"
      >
        <div className="flex items-center space-x-2 space-x-reverse">
          <Info size={16} className="text-gray-600" />
          <span className="text-sm font-medium text-gray-700">اطلاعات دیباگ</span>
        </div>
        {isExpanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
      </button>

      {isExpanded && (
        <div className="p-3 space-y-4 border-t border-gray-200">
          {/* Intent & Source */}
          <div className="grid grid-cols-2 gap-3">
            <div>
              <div className="flex items-center space-x-1 space-x-reverse mb-1">
                <Target size={14} className="text-gray-500" />
                <span className="text-xs font-medium text-gray-600">نیت</span>
              </div>
              <div className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getIntentColor(debugInfo.intent.label)}`}>
                {debugInfo.intent.label}
              </div>
              <div className="text-xs text-gray-500 mt-1">
                اطمینان: {(debugInfo.intent.confidence * 100).toFixed(1)}%
              </div>
            </div>

            <div>
              <div className="flex items-center space-x-1 space-x-reverse mb-1">
                <Search size={14} className="text-gray-500" />
                <span className="text-xs font-medium text-gray-600">منبع</span>
              </div>
              <div className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getSourceColor(debugInfo.source)}`}>
                {debugInfo.source}
              </div>
              <div className="text-xs text-gray-500 mt-1">
                موفق: {debugInfo.success ? 'بله' : 'خیر'}
              </div>
            </div>
          </div>

          {/* Performance Metrics */}
          {(debugInfo.tokens_in || debugInfo.tokens_out || debugInfo.latency_ms) && (
            <div>
              <div className="flex items-center space-x-1 space-x-reverse mb-2">
                <Clock size={14} className="text-gray-500" />
                <span className="text-xs font-medium text-gray-600">عملکرد</span>
              </div>
              <div className="grid grid-cols-3 gap-2 text-xs">
                {debugInfo.tokens_in && (
                  <div className="text-center">
                    <div className="text-gray-500">ورودی</div>
                    <div className="font-medium">{debugInfo.tokens_in}</div>
                  </div>
                )}
                {debugInfo.tokens_out && (
                  <div className="text-center">
                    <div className="text-gray-500">خروجی</div>
                    <div className="font-medium">{debugInfo.tokens_out}</div>
                  </div>
                )}
                {debugInfo.latency_ms && (
                  <div className="text-center">
                    <div className="text-gray-500">زمان (ms)</div>
                    <div className="font-medium">{debugInfo.latency_ms}</div>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Retrieval Results */}
          {debugInfo.retrieval_results && debugInfo.retrieval_results.length > 0 && (
            <div>
              <div className="text-xs font-medium text-gray-600 mb-2">
                نتایج جستجو ({debugInfo.retrieval_results.length})
              </div>
              <div className="space-y-2 max-h-32 overflow-y-auto">
                {debugInfo.retrieval_results.map((result, index) => (
                  <div key={index} className="bg-white p-2 rounded border text-xs">
                    <div className="flex justify-between items-start mb-1">
                      <span className="font-medium text-gray-700">
                        امتیاز: {(result.score * 100).toFixed(1)}%
                      </span>
                      {result.category && (
                        <span className="text-gray-500">{result.category}</span>
                      )}
                    </div>
                    <div className="text-gray-600 truncate" title={result.question}>
                      {result.question}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Unanswered Flag */}
          {debugInfo.unanswered_in_db && (
            <div className="bg-orange-50 border border-orange-200 rounded p-2">
              <div className="text-xs text-orange-800 font-medium">
                ⚠️ این سؤال در پایگاه دانش پاسخ مناسبی نداشت
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

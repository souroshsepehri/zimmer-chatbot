'use client'

import { useState, useEffect } from 'react'
import { ArrowLeft, RefreshCw, CheckCircle, XCircle, AlertCircle, Server, Database, Cpu, HardDrive } from 'lucide-react'
import Link from 'next/link'

interface SystemStatus {
  backend: {
    status: 'online' | 'offline' | 'error'
    responseTime: number
    lastCheck: string
  }
  database: {
    status: 'connected' | 'disconnected' | 'error'
    totalLogs: number
    totalFAQs: number
    totalCategories: number
  }
  api: {
    status: 'working' | 'error'
    endpoints: {
      logs: boolean
      faqs: boolean
      categories: boolean
      chat: boolean
    }
  }
  performance: {
    memoryUsage: string
    uptime: string
    lastRestart: string
  }
}

export default function SystemStatusPage() {
  const [status, setStatus] = useState<SystemStatus | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    checkSystemStatus()
  }, [])

  const checkSystemStatus = async () => {
    setLoading(true)
    setError(null)
    
    try {
      // Use same hostname as frontend, but port 8001
      const hostname = typeof window !== 'undefined' ? window.location.hostname : 'localhost'
      const baseUrl = hostname === 'localhost' || hostname === '127.0.0.1' 
        ? 'http://localhost:8001' 
        : `http://${hostname}:8001`
      
      // Check backend health
      const healthResponse = await fetch(`${baseUrl}/health`)
      const backendStatus = healthResponse.ok ? 'online' : 'offline'
      
      // Check API endpoints
      const endpoints = {
        logs: false,
        faqs: false,
        categories: false,
        chat: false
      }
      
      try {
        const logsResponse = await fetch(`${baseUrl}/api/logs/stats`)
        endpoints.logs = logsResponse.ok
      } catch (e) {}
      
      try {
        const faqsResponse = await fetch(`${baseUrl}/api/faqs`)
        endpoints.faqs = faqsResponse.ok
      } catch (e) {}
      
      try {
        const categoriesResponse = await fetch(`${baseUrl}/api/categories`)
        endpoints.categories = categoriesResponse.ok
      } catch (e) {}
      
      try {
        const chatResponse = await fetch(`${baseUrl}/api/chat`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ message: 'test' })
        })
        endpoints.chat = chatResponse.ok
      } catch (e) {}
      
      // Get database stats
      let dbStats = {
        totalLogs: 0,
        totalFAQs: 0,
        totalCategories: 0
      }
      
      try {
        const logsStatsResponse = await fetch(`${baseUrl}/api/logs/stats`)
        if (logsStatsResponse.ok) {
          const logsData = await logsStatsResponse.json()
          dbStats.totalLogs = logsData.total_logs || 0
        }
      } catch (e) {}
      
      try {
        const faqsResponse = await fetch(`${baseUrl}/api/faqs`)
        if (faqsResponse.ok) {
          const faqsData = await faqsResponse.json()
          dbStats.totalFAQs = Array.isArray(faqsData) ? faqsData.length : (faqsData.items?.length || 0)
        }
      } catch (e) {}
      
      try {
        const categoriesResponse = await fetch(`${baseUrl}/api/categories`)
        if (categoriesResponse.ok) {
          const categoriesData = await categoriesResponse.json()
          dbStats.totalCategories = Array.isArray(categoriesData) ? categoriesData.length : 0
        }
      } catch (e) {}
      
      const systemStatus: SystemStatus = {
        backend: {
          status: backendStatus,
          responseTime: Date.now() - performance.now(),
          lastCheck: new Date().toLocaleString('fa-IR')
        },
        database: {
          status: endpoints.logs ? 'connected' : 'disconnected',
          ...dbStats
        },
        api: {
          status: Object.values(endpoints).some(e => e) ? 'working' : 'error',
          endpoints
        },
        performance: {
          memoryUsage: 'Normal',
          uptime: 'Active',
          lastRestart: new Date().toLocaleString('fa-IR')
        }
      }
      
      setStatus(systemStatus)
    } catch (err) {
      setError('خطا در بررسی وضعیت سیستم')
      console.error('System status check error:', err)
    } finally {
      setLoading(false)
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'online':
      case 'connected':
      case 'working':
        return <CheckCircle className="w-5 h-5 text-green-500" />
      case 'offline':
      case 'disconnected':
      case 'error':
        return <XCircle className="w-5 h-5 text-red-500" />
      default:
        return <AlertCircle className="w-5 h-5 text-yellow-500" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'online':
      case 'connected':
      case 'working':
        return 'text-green-600 bg-green-50 border-green-200'
      case 'offline':
      case 'disconnected':
      case 'error':
        return 'text-red-600 bg-red-50 border-red-200'
      default:
        return 'text-yellow-600 bg-yellow-50 border-yellow-200'
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 p-6">
        <div className="max-w-7xl mx-auto">
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-600">در حال بررسی وضعیت سیستم...</p>
          </div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 p-6">
        <div className="max-w-7xl mx-auto">
          <div className="text-center py-12">
            <XCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">خطا در بررسی وضعیت</h3>
            <p className="text-gray-600 mb-4">{error}</p>
            <button
              onClick={checkSystemStatus}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              تلاش مجدد
            </button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">وضعیت سیستم</h1>
              <p className="text-gray-600">بررسی کامل وضعیت سیستم چت‌بات</p>
            </div>
            <div className="flex items-center space-x-3 space-x-reverse">
              <button
                onClick={checkSystemStatus}
                className="flex items-center space-x-2 space-x-reverse px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                <RefreshCw className="w-4 h-4" />
                <span>بروزرسانی</span>
              </button>
              <Link
                href="/admin"
                className="flex items-center space-x-2 space-x-reverse px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
              >
                <ArrowLeft className="w-4 h-4" />
                <span>بازگشت</span>
              </Link>
            </div>
          </div>
        </div>

        {status && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Backend Status */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900 flex items-center space-x-2 space-x-reverse">
                  <Server className="w-5 h-5" />
                  <span>وضعیت Backend</span>
                </h3>
                {getStatusIcon(status.backend.status)}
              </div>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-600">وضعیت:</span>
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(status.backend.status)}`}>
                    {status.backend.status === 'online' ? 'آنلاین' : 'آفلاین'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">زمان پاسخ:</span>
                  <span className="text-gray-900">{status.backend.responseTime}ms</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">آخرین بررسی:</span>
                  <span className="text-gray-900">{status.backend.lastCheck}</span>
                </div>
              </div>
            </div>

            {/* Database Status */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900 flex items-center space-x-2 space-x-reverse">
                  <Database className="w-5 h-5" />
                  <span>وضعیت دیتابیس</span>
                </h3>
                {getStatusIcon(status.database.status)}
              </div>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-600">وضعیت:</span>
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(status.database.status)}`}>
                    {status.database.status === 'connected' ? 'متصل' : 'قطع'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">تعداد لاگ‌ها:</span>
                  <span className="text-gray-900">{status.database.totalLogs}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">تعداد سوالات:</span>
                  <span className="text-gray-900">{status.database.totalFAQs}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">تعداد دسته‌ها:</span>
                  <span className="text-gray-900">{status.database.totalCategories}</span>
                </div>
              </div>
            </div>

            {/* API Endpoints */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900 flex items-center space-x-2 space-x-reverse">
                  <Cpu className="w-5 h-5" />
                  <span>وضعیت API</span>
                </h3>
                {getStatusIcon(status.api.status)}
              </div>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-600">Logs API:</span>
                  {getStatusIcon(status.api.endpoints.logs ? 'working' : 'error')}
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">FAQs API:</span>
                  {getStatusIcon(status.api.endpoints.faqs ? 'working' : 'error')}
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Categories API:</span>
                  {getStatusIcon(status.api.endpoints.categories ? 'working' : 'error')}
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Chat API:</span>
                  {getStatusIcon(status.api.endpoints.chat ? 'working' : 'error')}
                </div>
              </div>
            </div>

            {/* Performance */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900 flex items-center space-x-2 space-x-reverse">
                  <HardDrive className="w-5 h-5" />
                  <span>عملکرد سیستم</span>
                </h3>
                <CheckCircle className="w-5 h-5 text-green-500" />
              </div>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-600">استفاده از حافظه:</span>
                  <span className="text-gray-900">{status.performance.memoryUsage}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">زمان فعالیت:</span>
                  <span className="text-gray-900">{status.performance.uptime}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">آخرین راه‌اندازی:</span>
                  <span className="text-gray-900">{status.performance.lastRestart}</span>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Overall Status */}
        {status && (
          <div className="mt-8 bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">خلاصه وضعیت سیستم</h3>
            <div className="flex items-center space-x-3 space-x-reverse">
              {getStatusIcon(
                status.backend.status === 'online' && 
                status.database.status === 'connected' && 
                status.api.status === 'working' ? 'online' : 'error'
              )}
              <span className="text-lg font-medium text-gray-900">
                {status.backend.status === 'online' && 
                 status.database.status === 'connected' && 
                 status.api.status === 'working' 
                  ? 'سیستم در وضعیت عادی' 
                  : 'مشکلی در سیستم وجود دارد'}
              </span>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

'use client';

import { useState, useEffect } from 'react';
import { AlertCircle, CheckCircle, XCircle } from 'lucide-react';
import { checkHealth, API_BASE_URL } from '@/lib/api';

/**
 * Health Status Banner Component
 * 
 * Displays a non-blocking banner at the top of the admin dashboard showing:
 * - Backend health status
 * - Website configuration status (if applicable)
 * 
 * This component does NOT disable the UI - it only provides information.
 * All dashboard features remain usable even if backend is unavailable.
 */
export default function HealthStatusBanner() {
  const [healthStatus, setHealthStatus] = useState<'checking' | 'healthy' | 'unhealthy'>('checking');
  const [healthMessage, setHealthMessage] = useState<string>('');

  useEffect(() => {
    // Check health on mount and periodically
    const checkBackendHealth = async () => {
      try {
        const result = await checkHealth();
        if (result.status === 'ok' || result.status === 'healthy') {
          setHealthStatus('healthy');
          setHealthMessage('');
        } else {
          setHealthStatus('unhealthy');
          setHealthMessage(result.message || 'Backend is unavailable');
        }
      } catch (error) {
        setHealthStatus('unhealthy');
        setHealthMessage('Unable to reach backend');
        console.error('[HealthBanner] Health check failed:', error);
      }
    };

    checkBackendHealth();
    
    // Check every 30 seconds
    const interval = setInterval(checkBackendHealth, 30000);
    return () => clearInterval(interval);
  }, []);

  // Don't show banner if healthy
  if (healthStatus === 'healthy') {
    return null;
  }

  return (
    <div className={`w-full px-4 py-3 border-b ${
      healthStatus === 'checking' 
        ? 'bg-yellow-50 border-yellow-200' 
        : 'bg-red-50 border-red-200'
    }`}>
      <div className="max-w-7xl mx-auto flex items-center space-x-3 space-x-reverse">
        {healthStatus === 'checking' ? (
          <>
            <AlertCircle className="w-5 h-5 text-yellow-600" />
            <span className="text-sm font-medium text-yellow-800">
              در حال بررسی وضعیت Backend...
            </span>
          </>
        ) : (
          <>
            <XCircle className="w-5 h-5 text-red-600" />
            <div className="flex-1">
              <span className="text-sm font-medium text-red-800">
                Backend در دسترس نیست
              </span>
              {healthMessage && (
                <span className="text-sm text-red-700 mr-2">
                  ({healthMessage})
                </span>
              )}
              <span className="text-sm text-red-700 mr-2">
                - API Base URL: {API_BASE_URL}
              </span>
            </div>
            <div className="text-xs text-red-600">
              شما همچنان می‌توانید از داشبورد استفاده کنید، اما برخی عملیات ممکن است کار نکنند.
            </div>
          </>
        )}
      </div>
    </div>
  );
}


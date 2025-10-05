'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { 
  Plus, 
  Trash2, 
  ExternalLink, 
  Globe, 
  ArrowLeft,
  CheckCircle,
  AlertCircle,
  Loader2
} from 'lucide-react';

interface Website {
  id: string;
  url: string;
  title: string;
  status: 'active' | 'inactive' | 'error';
  addedDate: string;
  lastScraped?: string;
}

export default function WebsiteManagement() {
  const [websites, setWebsites] = useState<Website[]>([]);
  const [newUrl, setNewUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Load websites from localStorage (simple storage for demo)
  useEffect(() => {
    const savedWebsites = localStorage.getItem('chatbot-websites');
    if (savedWebsites) {
      setWebsites(JSON.parse(savedWebsites));
    }
  }, []);

  // Save websites to localStorage
  const saveWebsites = (updatedWebsites: Website[]) => {
    localStorage.setItem('chatbot-websites', JSON.stringify(updatedWebsites));
    setWebsites(updatedWebsites);
  };

  const addWebsite = async () => {
    if (!newUrl.trim()) {
      setError('لطفاً URL را وارد کنید');
      return;
    }

    // Basic URL validation
    try {
      new URL(newUrl);
    } catch {
      setError('URL نامعتبر است');
      return;
    }

    setLoading(true);
    setError('');

    // Simulate adding website (in real implementation, this would call backend API)
    const newWebsite: Website = {
      id: Date.now().toString(),
      url: newUrl,
      title: newUrl.replace(/^https?:\/\//, '').replace(/\/$/, ''),
      status: 'active',
      addedDate: new Date().toLocaleDateString('fa-IR'),
      lastScraped: new Date().toLocaleDateString('fa-IR')
    };

    setTimeout(() => {
      const updatedWebsites = [...websites, newWebsite];
      saveWebsites(updatedWebsites);
      setNewUrl('');
      setLoading(false);
    }, 1000);
  };

  const removeWebsite = (id: string) => {
    const updatedWebsites = websites.filter(w => w.id !== id);
    saveWebsites(updatedWebsites);
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'error':
        return <AlertCircle className="w-4 h-4 text-red-500" />;
      default:
        return <AlertCircle className="w-4 h-4 text-gray-400" />;
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'active':
        return 'فعال';
      case 'error':
        return 'خطا';
      default:
        return 'غیرفعال';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4 space-x-reverse">
          <Link 
            href="/admin"
            className="flex items-center space-x-2 space-x-reverse text-gray-600 hover:text-gray-900 transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
            <span>بازگشت به پنل مدیریت</span>
          </Link>
        </div>
        <div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
            مدیریت وب‌سایت‌ها
          </h1>
          <p className="mt-2 text-gray-600">
            افزودن و مدیریت وب‌سایت‌هایی که بات می‌تواند از آن‌ها اطلاعات دریافت کند
          </p>
        </div>
      </div>

      {/* Add Website Form */}
      <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg border border-gray-200/50 p-6">
        <div className="flex items-center space-x-3 space-x-reverse mb-4">
          <Globe className="w-6 h-6 text-blue-600" />
          <h3 className="text-xl font-semibold text-gray-900">افزودن وب‌سایت جدید</h3>
        </div>
        
        <div className="flex space-x-4 space-x-reverse">
          <div className="flex-1">
            <input
              type="url"
              value={newUrl}
              onChange={(e) => setNewUrl(e.target.value)}
              placeholder="https://example.com"
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              disabled={loading}
            />
            {error && (
              <p className="mt-2 text-sm text-red-600">{error}</p>
            )}
          </div>
          <button
            onClick={addWebsite}
            disabled={loading || !newUrl.trim()}
            className="flex items-center space-x-2 space-x-reverse px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:from-blue-700 hover:to-purple-700 transition-all duration-200 shadow-lg disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <Plus className="w-5 h-5" />
            )}
            <span>{loading ? 'در حال افزودن...' : 'افزودن وب‌سایت'}</span>
          </button>
        </div>
      </div>

      {/* Websites List */}
      <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg border border-gray-200/50 overflow-hidden">
        <div className="px-6 py-5 border-b border-gray-200/50">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3 space-x-reverse">
              <Globe className="w-6 h-6 text-gray-700" />
              <h3 className="text-xl font-semibold text-gray-900">وب‌سایت‌های متصل</h3>
            </div>
            <span className="text-sm text-gray-500">
              {websites.length} وب‌سایت
            </span>
          </div>
        </div>

        <div className="p-6">
          {websites.length === 0 ? (
            <div className="text-center py-12">
              <Globe className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <h4 className="text-lg font-medium text-gray-900 mb-2">هیچ وب‌سایتی اضافه نشده</h4>
              <p className="text-gray-500">وب‌سایت اول خود را اضافه کنید تا بات بتواند از آن اطلاعات دریافت کند</p>
            </div>
          ) : (
            <div className="space-y-4">
              {websites.map((website) => (
                <div key={website.id} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg border border-gray-200">
                  <div className="flex items-center space-x-4 space-x-reverse">
                    {getStatusIcon(website.status)}
                    <div>
                      <h4 className="font-medium text-gray-900">{website.title}</h4>
                      <p className="text-sm text-gray-500">{website.url}</p>
                      <div className="flex items-center space-x-4 space-x-reverse mt-1">
                        <span className="text-xs text-gray-400">
                          اضافه شده: {website.addedDate}
                        </span>
                        {website.lastScraped && (
                          <span className="text-xs text-gray-400">
                            آخرین بروزرسانی: {website.lastScraped}
                          </span>
                        )}
                        <span className={`text-xs px-2 py-1 rounded-full ${
                          website.status === 'active' 
                            ? 'bg-green-100 text-green-700' 
                            : website.status === 'error'
                            ? 'bg-red-100 text-red-700'
                            : 'bg-gray-100 text-gray-700'
                        }`}>
                          {getStatusText(website.status)}
                        </span>
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2 space-x-reverse">
                    <a
                      href={website.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="p-2 text-gray-400 hover:text-blue-600 transition-colors"
                      title="مشاهده وب‌سایت"
                    >
                      <ExternalLink className="w-4 h-4" />
                    </a>
                    <button
                      onClick={() => removeWebsite(website.id)}
                      className="p-2 text-gray-400 hover:text-red-600 transition-colors"
                      title="حذف وب‌سایت"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Info Box */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div className="flex items-start space-x-3 space-x-reverse">
          <AlertCircle className="w-5 h-5 text-blue-600 mt-0.5" />
          <div>
            <h4 className="font-medium text-blue-900 mb-1">نحوه عملکرد</h4>
            <p className="text-sm text-blue-700">
              وب‌سایت‌هایی که اضافه می‌کنید به عنوان منبع اطلاعات ثانویه برای بات استفاده می‌شوند. 
              بات می‌تواند از محتوای این وب‌سایت‌ها برای پاسخ به سؤالات کاربران استفاده کند.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

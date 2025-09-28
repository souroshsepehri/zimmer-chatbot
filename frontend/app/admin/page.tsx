'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { 
  HelpCircle, 
  FolderOpen, 
  FileText, 
  TrendingUp, 
  Users, 
  MessageCircle,
  Activity,
  ArrowLeft,
  Plus,
  BarChart3
} from 'lucide-react';
import { getFAQs, getCategories, getLogStats } from '@/lib/api';

export default function AdminDashboard() {
  const [stats, setStats] = useState([
    {
      name: 'کل سوالات',
      value: '0',
      change: '0%',
      changeType: 'positive',
      icon: HelpCircle,
      color: 'green'
    },
    {
      name: 'دسته‌بندی‌ها',
      value: '0',
      change: '0',
      changeType: 'positive',
      icon: FolderOpen,
      color: 'blue'
    },
    {
      name: 'گفتگوهای امروز',
      value: '0',
      change: '0%',
      changeType: 'positive',
      icon: MessageCircle,
      color: 'purple'
    },
    {
      name: 'نرخ پاسخ‌دهی',
      value: '0%',
      change: '0%',
      changeType: 'positive',
      icon: TrendingUp,
      color: 'orange'
    }
  ]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      const [faqs, categories, logStats] = await Promise.all([
        getFAQs(),
        getCategories(),
        getLogStats().catch(() => ({ 
          total_chats: 0, 
          success_rate: 0, 
          today_chats: 0,
          unanswered_logs: 0 
        }))
      ]);

      const todayChats = logStats.today_chats || 0;
      const successRate = Math.round(logStats.success_rate || 0);
      const unansweredCount = logStats.unanswered_logs || 0;

      setStats([
        {
          name: 'کل سوالات',
          value: faqs.length.toString(),
          change: '+12%',
          changeType: 'positive',
          icon: HelpCircle,
          color: 'green'
        },
        {
          name: 'دسته‌بندی‌ها',
          value: categories.length.toString(),
          change: '+2',
          changeType: 'positive',
          icon: FolderOpen,
          color: 'blue'
        },
        {
          name: 'گفتگوهای امروز',
          value: todayChats.toString(),
          change: '+23%',
          changeType: 'positive',
          icon: MessageCircle,
          color: 'purple'
        },
        {
          name: 'نرخ پاسخ‌دهی',
          value: `${successRate}%`,
          change: '+5%',
          changeType: 'positive',
          icon: TrendingUp,
          color: 'orange'
        }
      ]);
    } catch (error) {
      console.error('Error loading stats:', error);
      // Set fallback values on error
      setStats([
        {
          name: 'کل سوالات',
          value: '0',
          change: '0%',
          changeType: 'neutral',
          icon: HelpCircle,
          color: 'green'
        },
        {
          name: 'دسته‌بندی‌ها',
          value: '0',
          change: '0',
          changeType: 'neutral',
          icon: FolderOpen,
          color: 'blue'
        },
        {
          name: 'گفتگوهای امروز',
          value: '0',
          change: '0%',
          changeType: 'neutral',
          icon: MessageCircle,
          color: 'purple'
        },
        {
          name: 'نرخ پاسخ‌دهی',
          value: '0%',
          change: '0%',
          changeType: 'neutral',
          icon: TrendingUp,
          color: 'orange'
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const quickActions = [
    {
      name: 'مدیریت سوالات',
      description: 'اضافه، ویرایش و حذف سوالات و پاسخ‌ها',
      href: '/admin/faqs',
      icon: HelpCircle,
      color: 'green',
      gradient: 'from-green-500 to-emerald-600'
    },
    {
      name: 'مدیریت دسته‌بندی‌ها',
      description: 'ایجاد و مدیریت دسته‌بندی‌های سوالات',
      href: '/admin/categories',
      icon: FolderOpen,
      color: 'blue',
      gradient: 'from-blue-500 to-cyan-600'
    },
    {
      name: 'گزارشات و لاگ‌ها',
      description: 'مشاهده گزارشات و تاریخچه گفتگوها',
      href: '/admin/logs',
      icon: FileText,
      color: 'purple',
      gradient: 'from-purple-500 to-pink-600'
    }
  ];

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-gray-900 to-gray-700 bg-clip-text text-transparent">
            داشبورد مدیریت
          </h1>
          <p className="mt-2 text-gray-600">
            خوش آمدید! مدیریت کامل سیستم چت‌بات هوشمند
          </p>
        </div>
        <div className="flex items-center space-x-3 space-x-reverse">
          <Link 
            href="/admin/system-status"
            className="flex items-center space-x-2 space-x-reverse px-4 py-2 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 transition-all duration-200 shadow-sm"
          >
            <Activity className="w-4 h-4 text-gray-500" />
            <span className="text-sm font-medium text-gray-700">وضعیت سیستم</span>
          </Link>
          <Link 
            href="/admin/faqs"
            className="flex items-center space-x-2 space-x-reverse px-4 py-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:from-blue-700 hover:to-purple-700 transition-all duration-200 shadow-lg"
          >
            <Plus className="w-4 h-4" />
            <span className="text-sm font-medium">سوال جدید</span>
          </Link>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat) => {
          const Icon = stat.icon;
          return (
            <div key={stat.name} className="group relative bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-lg border border-gray-200/50 hover:shadow-xl transition-all duration-300">
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <p className="text-sm font-medium text-gray-600 mb-1">{stat.name}</p>
                  <p className="text-3xl font-bold text-gray-900">{stat.value}</p>
                  <div className="flex items-center mt-2">
                    <span className={`text-sm font-medium ${
                      stat.changeType === 'positive' ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {stat.change}
                    </span>
                    <span className="text-sm text-gray-500 mr-1">از ماه گذشته</span>
                  </div>
                </div>
                <div className={`p-3 rounded-xl bg-gradient-to-r ${
                  stat.color === 'green' ? 'from-green-500 to-emerald-600' :
                  stat.color === 'blue' ? 'from-blue-500 to-cyan-600' :
                  stat.color === 'purple' ? 'from-purple-500 to-pink-600' :
                  'from-orange-500 to-red-600'
                }`}>
                  <Icon className="w-6 h-6 text-white" />
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Quick Actions */}
      <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg border border-gray-200/50 overflow-hidden">
        <div className="px-6 py-5 border-b border-gray-200/50">
          <div className="flex items-center space-x-3 space-x-reverse">
            <BarChart3 className="w-6 h-6 text-gray-700" />
            <h3 className="text-xl font-semibold text-gray-900">اقدامات سریع</h3>
          </div>
          <p className="mt-1 text-sm text-gray-600">دسترسی آسان به بخش‌های مختلف مدیریت</p>
        </div>
        <div className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {quickActions.map((action) => {
              const Icon = action.icon;
              return (
                <Link
                  key={action.name}
                  href={action.href}
                  className="group relative bg-white rounded-xl p-6 border border-gray-200 hover:border-gray-300 hover:shadow-lg transition-all duration-300"
                >
                  <div className="flex items-start space-x-4 space-x-reverse">
                    <div className={`p-3 rounded-xl bg-gradient-to-r ${action.gradient} shadow-lg`}>
                      <Icon className="w-6 h-6 text-white" />
                    </div>
                    <div className="flex-1">
                      <h4 className="text-lg font-semibold text-gray-900 group-hover:text-gray-700 transition-colors">
                        {action.name}
                      </h4>
                      <p className="mt-2 text-sm text-gray-600">
                        {action.description}
                      </p>
                    </div>
                    <ArrowLeft className="w-5 h-5 text-gray-400 group-hover:text-gray-600 transition-colors" />
                  </div>
                </Link>
              );
            })}
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg border border-gray-200/50 overflow-hidden">
        <div className="px-6 py-5 border-b border-gray-200/50">
          <div className="flex items-center space-x-3 space-x-reverse">
            <Activity className="w-6 h-6 text-gray-700" />
            <h3 className="text-xl font-semibold text-gray-900">فعالیت‌های اخیر</h3>
          </div>
        </div>
        <div className="p-6">
          <div className="space-y-4">
            <div className="flex items-center space-x-4 space-x-reverse p-4 bg-green-50 rounded-lg border border-green-200">
              <div className="w-2 h-2 bg-green-500 rounded-full"></div>
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-900">سوال جدید اضافه شد</p>
                <p className="text-xs text-gray-500">2 دقیقه پیش</p>
              </div>
            </div>
            <div className="flex items-center space-x-4 space-x-reverse p-4 bg-blue-50 rounded-lg border border-blue-200">
              <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-900">دسته‌بندی جدید ایجاد شد</p>
                <p className="text-xs text-gray-500">15 دقیقه پیش</p>
              </div>
            </div>
            <div className="flex items-center space-x-4 space-x-reverse p-4 bg-purple-50 rounded-lg border border-purple-200">
              <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-900">گفتگوی جدید ثبت شد</p>
                <p className="text-xs text-gray-500">1 ساعت پیش</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

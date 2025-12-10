'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import Navigation from '@/components/Navigation';
import AdminGuard from '@/components/AdminGuard';
import HealthStatusBanner from '@/components/HealthStatusBanner';
import { 
  LayoutDashboard, 
  HelpCircle, 
  FolderOpen, 
  FileText, 
  ArrowRight,
  Settings,
  Bell,
  User
} from 'lucide-react';

export default function AdminLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();

  const menuItems = [
    { href: '/admin', label: 'داشبورد', icon: LayoutDashboard, color: 'blue' },
    { href: '/admin/faqs', label: 'مدیریت سوالات', icon: HelpCircle, color: 'green' },
    { href: '/admin/categories', label: 'دسته‌بندی‌ها', icon: FolderOpen, color: 'purple' },
    { href: '/admin/logs', label: 'گزارشات', icon: FileText, color: 'orange' },
    { href: '/admin/system-status', label: 'وضعیت سیستم', icon: Settings, color: 'gray' },
  ];

  const getColorClasses = (color: string, isActive: boolean) => {
    const colors = {
      blue: isActive ? 'bg-blue-50 text-blue-700 border-blue-200' : 'text-gray-600 hover:bg-blue-50 hover:text-blue-700',
      green: isActive ? 'bg-green-50 text-green-700 border-green-200' : 'text-gray-600 hover:bg-green-50 hover:text-green-700',
      purple: isActive ? 'bg-purple-50 text-purple-700 border-purple-200' : 'text-gray-600 hover:bg-purple-50 hover:text-purple-700',
      orange: isActive ? 'bg-orange-50 text-orange-700 border-orange-200' : 'text-gray-600 hover:bg-orange-50 hover:text-orange-700',
      gray: isActive ? 'bg-gray-50 text-gray-700 border-gray-200' : 'text-gray-600 hover:bg-gray-50 hover:text-gray-700',
    };
    return colors[color as keyof typeof colors] || colors.blue;
  };

  return (
    <AdminGuard>
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100" dir="rtl">
        <Navigation variant="admin" />
        <HealthStatusBanner />

      <div className="flex">
        {/* Modern Sidebar */}
        <aside className="w-72 bg-white/70 backdrop-blur-md shadow-xl min-h-screen border-l border-gray-200/50">
          <nav className="p-6">
            <div className="space-y-2">
              {menuItems.map((item) => {
                const isActive = pathname === item.href;
                const Icon = item.icon;
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    className={`group flex items-center justify-between px-4 py-3 text-sm font-medium rounded-xl transition-all duration-200 ${
                      isActive 
                        ? getColorClasses(item.color, true) + ' border shadow-sm' 
                        : getColorClasses(item.color, false)
                    }`}
                  >
                    <div className="flex items-center space-x-3 space-x-reverse">
                      <div className={`p-2 rounded-lg ${
                        isActive 
                          ? 'bg-white/50' 
                          : 'bg-gray-100 group-hover:bg-white/50'
                      } transition-all duration-200`}>
                        <Icon className={`w-5 h-5 ${
                          isActive 
                            ? `text-${item.color}-600` 
                            : 'text-gray-500 group-hover:text-gray-700'
                        }`} />
                      </div>
                      <span className="font-medium">{item.label}</span>
                    </div>
                    {isActive && (
                      <div className={`w-2 h-2 rounded-full bg-${item.color}-500`} />
                    )}
                  </Link>
                );
              })}
            </div>
            
            {/* Sidebar Footer */}
            <div className="mt-8 pt-6 border-t border-gray-200/50">
              <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl p-4">
                <div className="flex items-center space-x-3 space-x-reverse">
                  <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-500 rounded-lg flex items-center justify-center">
                    <Settings className="w-5 h-5 text-white" />
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-900">سیستم فعال</p>
                    <p className="text-xs text-gray-500">آخرین بروزرسانی: امروز</p>
                  </div>
                </div>
              </div>
            </div>
          </nav>
        </aside>

        {/* Main Content with Modern Styling */}
        <main className="flex-1 p-8">
          <div className="max-w-7xl mx-auto">
            {children}
          </div>
        </main>
      </div>
      </div>
    </AdminGuard>
  );
}

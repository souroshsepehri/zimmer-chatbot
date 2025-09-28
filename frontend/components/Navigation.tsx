'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { 
  Home, 
  Settings, 
  MessageCircle, 
  ArrowLeft, 
  ArrowRight,
  HelpCircle
} from 'lucide-react';

interface NavigationProps {
  variant?: 'main' | 'admin';
}

export default function Navigation({ variant = 'main' }: NavigationProps) {
  const pathname = usePathname();
  const isAdmin = pathname.startsWith('/admin');

  if (variant === 'main' && !isAdmin) {
    return (
      <nav className="bg-white/80 backdrop-blur-md shadow-lg border-b border-gray-200/50 sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-4 space-x-reverse">
              <div className="flex items-center space-x-3 space-x-reverse">
                <div className="w-10 h-10 bg-gradient-to-r from-purple-600 to-blue-600 rounded-xl flex items-center justify-center">
                  <MessageCircle className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h1 className="text-xl font-bold bg-gradient-to-r from-gray-900 to-gray-700 bg-clip-text text-transparent">
                    بات هوشمند زیمر
                  </h1>
                  <p className="text-sm text-gray-500">دستیار هوشمند فارسی</p>
                </div>
              </div>
            </div>
            <div className="flex items-center space-x-4 space-x-reverse">
              <Link
                href="/admin"
                className="flex items-center space-x-2 space-x-reverse px-4 py-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:from-blue-700 hover:to-purple-700 transition-all duration-200 shadow-lg"
              >
                <Settings className="w-5 h-5" />
                <span className="text-sm font-medium">پنل مدیریت</span>
              </Link>
            </div>
          </div>
        </div>
      </nav>
    );
  }

  if (variant === 'admin' || isAdmin) {
    return (
      <nav className="bg-white/80 backdrop-blur-md shadow-lg border-b border-gray-200/50 sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-4 space-x-reverse">
              <div className="flex items-center space-x-3 space-x-reverse">
                <div className="w-10 h-10 bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl flex items-center justify-center">
                  <Settings className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h1 className="text-xl font-bold bg-gradient-to-r from-gray-900 to-gray-700 bg-clip-text text-transparent">
                    پنل مدیریت چت‌بات
                  </h1>
                  <p className="text-sm text-gray-500">مدیریت هوشمند سیستم</p>
                </div>
              </div>
            </div>
            <div className="flex items-center space-x-4 space-x-reverse">
              <Link
                href="/"
                className="flex items-center space-x-2 space-x-reverse px-4 py-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg text-sm font-medium transition-all duration-200"
              >
                <span>بازگشت به سایت</span>
                <ArrowRight className="w-4 h-4" />
              </Link>
            </div>
          </div>
        </div>
      </nav>
    );
  }

  return null;
}

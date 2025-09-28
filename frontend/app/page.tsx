'use client'

import ChatWidget from '@/components/ChatWidget'
import Navigation from '@/components/Navigation'

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-gray-100">
      <Navigation variant="main" />
      <main className="container mx-auto px-4 py-8">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            بات هوشمند زیمر
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            دستیار هوشمند فارسی برای پاسخ به سؤالات شما. 
            از طریق چت آنلاین با ما در ارتباط باشید.
          </p>
        </div>
        
        <div className="max-w-4xl mx-auto">
          <div className="bg-white rounded-2xl shadow-lg p-8 mb-8">
            <h2 className="text-2xl font-semibold text-gray-800 mb-6">
              ویژگی‌های بات
            </h2>
            <div className="grid md:grid-cols-2 gap-6">
              <div className="flex items-start space-x-3 space-x-reverse">
                <div className="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center flex-shrink-0">
                  <span className="text-primary-600 text-sm">💬</span>
                </div>
                <div>
                  <h3 className="font-medium text-gray-800 mb-1">پاسخ‌های هوشمند</h3>
                  <p className="text-gray-600 text-sm">
                    با استفاده از هوش مصنوعی پیشرفته، پاسخ‌های دقیق و مفید ارائه می‌دهد
                  </p>
                </div>
              </div>
              
              <div className="flex items-start space-x-3 space-x-reverse">
                <div className="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center flex-shrink-0">
                  <span className="text-primary-600 text-sm">🔍</span>
                </div>
                <div>
                  <h3 className="font-medium text-gray-800 mb-1">جستجوی معنایی</h3>
                  <p className="text-gray-600 text-sm">
                    با استفاده از تکنولوژی جستجوی معنایی، بهترین پاسخ‌ها را پیدا می‌کند
                  </p>
                </div>
              </div>
              
              <div className="flex items-start space-x-3 space-x-reverse">
                <div className="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center flex-shrink-0">
                  <span className="text-primary-600 text-sm">📚</span>
                </div>
                <div>
                  <h3 className="font-medium text-gray-800 mb-1">پایگاه دانش</h3>
                  <p className="text-gray-600 text-sm">
                    از مجموعه‌ای غنی از سؤالات و پاسخ‌های متداول استفاده می‌کند
                  </p>
                </div>
              </div>
              
              <div className="flex items-start space-x-3 space-x-reverse">
                <div className="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center flex-shrink-0">
                  <span className="text-primary-600 text-sm">⚡</span>
                </div>
                <div>
                  <h3 className="font-medium text-gray-800 mb-1">پاسخ سریع</h3>
                  <p className="text-gray-600 text-sm">
                    در کمترین زمان ممکن پاسخ سؤالات شما را ارائه می‌دهد
                  </p>
                </div>
              </div>
            </div>
          </div>
          
          <div className="text-center">
            <p className="text-gray-600 mb-4">
              برای شروع گفت‌وگو، روی دکمه چت کلیک کنید
            </p>
          </div>
        </div>
        
        <ChatWidget />
      </main>
    </div>
  )
}

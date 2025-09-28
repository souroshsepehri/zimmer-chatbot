'use client'

import { useState, useRef, useEffect } from 'react'
import { Send, X, Settings, MessageCircle, Bot, User, Sparkles, Zap } from 'lucide-react'
import { postChat } from '@/lib/api'
import DebugPanel from './DebugPanel'

interface Message {
  id: string
  text: string
  isUser: boolean
  timestamp: Date
  debugInfo?: any
}

export default function ChatWidget() {
  const [isOpen, setIsOpen] = useState(false)
  const [messages, setMessages] = useState<Message[]>([])
  const [inputText, setInputText] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [debugMode, setDebugMode] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  // Add welcome message on mount
  useEffect(() => {
    setMessages([{
      id: 'welcome',
      text: 'سلام وقت بخیر ربات هوشمند زیمر هستم چطور می تونم کمکتون کنم',
      isUser: false,
      timestamp: new Date()
    }])
  }, [])

  // Scroll to bottom when new message is added
  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // Focus input when chat opens
  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus()
    }
  }, [isOpen])

  // Debug input changes
  useEffect(() => {
    console.log('Input text changed:', inputText)
  }, [inputText])



  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const handleSendMessage = async () => {
    if (!inputText.trim() || isLoading) return

    const userMessage: Message = {
      id: Date.now().toString(),
      text: inputText,
      isUser: true,
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    const messageText = inputText
    setInputText('')
    setIsLoading(true)

    try {
      const response = await postChat({
        message: messageText,
        debug: debugMode
      })

      const botMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: response.answer,
        isUser: false,
        timestamp: new Date(),
        debugInfo: response.debug_info
      }

      setMessages(prev => [...prev, botMessage])
    } catch (error) {
      console.error('Error sending message:', error)
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: 'متأسفانه خطایی رخ داده است. لطفاً دوباره تلاش کنید.',
        isUser: false,
        timestamp: new Date()
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  return (
    <>
      {/* Ultra Modern Chat Button */}
      {!isOpen && (
        <div className="fixed bottom-6 left-6 z-50">
          <button
            onClick={() => setIsOpen(true)}
            className="group relative w-16 h-16 bg-gradient-to-br from-blue-500 via-purple-600 to-pink-500 rounded-full shadow-2xl hover:shadow-3xl hover:scale-110 transition-all duration-500 flex items-center justify-center overflow-hidden"
          >
            {/* Animated background */}
            <div className="absolute inset-0 bg-gradient-to-br from-blue-400 via-purple-500 to-pink-400 rounded-full animate-pulse opacity-75"></div>
            
            {/* Button content */}
            <div className="relative z-10">
              <MessageCircle size={28} className="text-white group-hover:rotate-12 transition-transform duration-300" />
            </div>
            
            {/* Floating particles */}
            <div className="absolute -top-2 -right-2 w-6 h-6 bg-green-400 rounded-full border-4 border-white animate-bounce"></div>
            <div className="absolute -top-1 -left-1 w-3 h-3 bg-yellow-400 rounded-full animate-ping"></div>
            
            {/* Ripple effect */}
            <div className="absolute inset-0 rounded-full bg-white/20 scale-0 group-hover:scale-100 transition-transform duration-500"></div>
          </button>
          
          {/* Tooltip */}
          <div className="absolute bottom-full left-0 mb-4 px-3 py-2 bg-gray-900 text-white text-sm rounded-lg opacity-0 group-hover:opacity-100 transition-opacity duration-300 whitespace-nowrap">
            شروع گفتگو
            <div className="absolute top-full left-4 w-0 h-0 border-l-4 border-r-4 border-t-4 border-transparent border-t-gray-900"></div>
          </div>
        </div>
      )}

      {/* Ultra Modern Chat Panel */}
      {isOpen && (
        <div className="fixed bottom-24 left-6 w-[380px] h-[600px] bg-white/95 backdrop-blur-2xl rounded-3xl shadow-2xl border border-white/20 z-50 flex flex-col overflow-hidden animate-in slide-in-from-bottom-4 duration-500">
          {/* Ultra Modern Header */}
          <div className="relative bg-gradient-to-br from-blue-600 via-purple-600 to-pink-600 text-white p-4 rounded-t-3xl overflow-hidden">
            {/* Animated background pattern */}
            <div className="absolute inset-0 opacity-20">
              <div className="absolute top-0 left-0 w-full h-full bg-gradient-to-br from-white/10 to-transparent"></div>
              <div className="absolute -top-10 -right-10 w-32 h-32 bg-white/5 rounded-full"></div>
              <div className="absolute -bottom-5 -left-5 w-24 h-24 bg-white/5 rounded-full"></div>
            </div>
            
            <div className="relative flex items-center justify-between">
              <div className="flex items-center space-x-4 space-x-reverse">
                <div className="relative">
                  <div className="w-12 h-12 bg-white/20 rounded-2xl flex items-center justify-center backdrop-blur-sm border border-white/30">
                    <Bot size={24} className="text-white" />
                  </div>
                  <div className="absolute -bottom-1 -right-1 w-5 h-5 bg-green-400 rounded-full border-3 border-white animate-pulse"></div>
                </div>
                <div>
                  <h3 className="font-bold text-lg bg-gradient-to-r from-white to-blue-100 bg-clip-text text-transparent">
                    بات هوشمند زیمر
                  </h3>
                  <div className="flex items-center space-x-2 space-x-reverse">
                    <div className="flex items-center space-x-1 space-x-reverse">
                      <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                      <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" style={{ animationDelay: '0.2s' }}></div>
                      <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" style={{ animationDelay: '0.4s' }}></div>
                    </div>
                    <p className="text-sm text-white/90 font-medium">آنلاین و آماده پاسخ</p>
                  </div>
                </div>
              </div>
              
              <div className="flex items-center space-x-2 space-x-reverse">
                <button
                  onClick={() => setDebugMode(!debugMode)}
                  className={`p-3 rounded-xl transition-all duration-300 ${
                    debugMode 
                      ? 'bg-white/30 text-white shadow-lg' 
                      : 'bg-white/10 text-white/80 hover:bg-white/20 hover:scale-105'
                  }`}
                  title="حالت دیباگ"
                >
                  <Settings size={20} />
                </button>
                <button
                  onClick={() => setIsOpen(false)}
                  className="p-3 rounded-xl bg-white/10 text-white/80 hover:bg-white/20 hover:scale-105 transition-all duration-300"
                >
                  <X size={20} />
                </button>
              </div>
            </div>
          </div>

          {/* Ultra Modern Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gradient-to-b from-gray-50/30 to-white/50">
            {messages.map((message) => (
              <div key={message.id} className="fade-in">
                <div className={`flex ${message.isUser ? 'justify-end' : 'justify-start'} items-start space-x-3 space-x-reverse`}>
                  {/* Avatar */}
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                    message.isUser 
                      ? 'bg-gradient-to-br from-blue-500 to-purple-600 order-2' 
                      : 'bg-gradient-to-br from-purple-500 to-pink-600 order-1'
                  }`}>
                    {message.isUser ? <User size={16} className="text-white" /> : <Bot size={16} className="text-white" />}
                  </div>
                  
                  {/* Message bubble */}
                  <div
                    className={`max-w-[280px] p-3 rounded-3xl shadow-lg ${
                      message.isUser
                        ? 'bg-gradient-to-br from-blue-500 to-purple-600 text-white order-1'
                        : 'bg-white text-gray-800 border border-gray-200/50 order-2'
                    }`}
                  >
                    <p className="text-sm leading-relaxed font-medium">{message.text}</p>
                    <div className={`flex items-center justify-between mt-2 ${
                      message.isUser ? 'text-white/70' : 'text-gray-500'
                    }`}>
                      <p className="text-xs">
                        {message.timestamp.toLocaleTimeString('fa-IR', {
                          hour: '2-digit',
                          minute: '2-digit'
                        })}
                      </p>
                      {message.isUser && (
                        <div className="flex items-center space-x-1 space-x-reverse">
                          <div className="w-1 h-1 bg-white/50 rounded-full"></div>
                          <div className="w-1 h-1 bg-white/50 rounded-full"></div>
                          <div className="w-1 h-1 bg-white/50 rounded-full"></div>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
                
                {/* Debug Panel */}
                {debugMode && message.debugInfo && !message.isUser && (
                  <div className="mt-3 mr-11">
                    <DebugPanel debugInfo={message.debugInfo} />
                  </div>
                )}
              </div>
            ))}
            
            {/* Ultra Modern Loading Animation */}
            {isLoading && (
              <div className="flex justify-start items-start space-x-3 space-x-reverse">
                <div className="w-8 h-8 rounded-full bg-gradient-to-br from-purple-500 to-pink-600 flex items-center justify-center">
                  <Bot size={16} className="text-white" />
                </div>
                <div className="bg-white border border-gray-200/50 rounded-3xl p-4 shadow-lg">
                  <div className="flex items-center space-x-2 space-x-reverse">
                    <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-purple-500 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                    <div className="w-2 h-2 bg-pink-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                    <span className="text-xs text-gray-500 mr-2">در حال پاسخ‌دهی...</span>
                  </div>
                </div>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>

          {/* Ultra Modern Input */}
          <div className="p-4 bg-white/80 backdrop-blur-sm border-t border-gray-200/50">
            <div className="flex items-end space-x-3 space-x-reverse">
              <div className="flex-1 relative">
                <input
                  ref={inputRef}
                  type="text"
                  value={inputText}
                  onChange={(e) => setInputText(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="پیام خود را بنویسید..."
                  className="w-full px-4 py-3 pr-12 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
                />
                <div className="absolute left-4 top-1/2 transform -translate-y-1/2">
                  <MessageCircle size={18} className="text-gray-400" />
                </div>
              </div>
              <button
                onClick={handleSendMessage}
                disabled={!inputText.trim() || isLoading}
                className="group p-3 bg-gradient-to-br from-blue-500 to-purple-600 text-white rounded-2xl hover:from-blue-600 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300 shadow-lg hover:shadow-xl disabled:shadow-none hover:scale-105"
              >
                <Send size={18} className="group-hover:scale-110 transition-transform duration-200" />
              </button>
            </div>
            
            {/* Input hints */}
            <div className="mt-3 flex items-center justify-between text-xs text-gray-500">
              <div className="flex items-center space-x-2 space-x-reverse">
                <Zap size={14} className="text-blue-500" />
                <span>Enter برای ارسال</span>
              </div>
              <div className="flex items-center space-x-2 space-x-reverse">
                <Sparkles size={14} className="text-purple-500" />
                <span>Shift+Enter برای خط جدید</span>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  )
}

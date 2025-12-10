/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  trailingSlash: true,
  images: {
    unoptimized: true,
  },
  env: {
    // NEXT_PUBLIC_API_BASE_URL is the single source of truth for backend API
    // Set it in .env.local for production: NEXT_PUBLIC_API_BASE_URL=https://chatbot.zimmerai.com/api
    // Defaults to http://localhost:8001/api in lib/api.ts
    NEXT_PUBLIC_CHATBOT_API_BASE: process.env.NEXT_PUBLIC_CHATBOT_API_BASE || 'https://chatbot.zimmerai.com',
  },
}

module.exports = nextConfig

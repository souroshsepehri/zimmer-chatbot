/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',
  trailingSlash: true,
  images: {
    unoptimized: true,
  },
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001/api',
    NEXT_PUBLIC_CHATBOT_API_BASE: process.env.NEXT_PUBLIC_CHATBOT_API_BASE || 'https://chatbot.zimmerai.com',
  },
}

module.exports = nextConfig

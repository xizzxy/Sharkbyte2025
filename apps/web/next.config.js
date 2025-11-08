/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,

  // Environment variables that should be exposed to the browser
  env: {
    NEXT_PUBLIC_WORKER_API_URL: process.env.NEXT_PUBLIC_WORKER_API_URL || 'http://localhost:8787',
    GEMINI_API_KEY: process.env.GEMINI_API_KEY,
  },

  // For Cloudflare Pages deployment
  output: 'standalone',

  // Image optimization
  images: {
    unoptimized: true, // Required for Cloudflare Pages
  },
}

module.exports = nextConfig

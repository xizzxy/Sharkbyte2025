/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,

  // For Cloudflare Pages static export
  output: 'export',

  // Disable features not supported in static export
  images: {
    unoptimized: true, // Required for static export
  },

  // Optional: Add trailing slashes for better static hosting
  trailingSlash: true,
}

module.exports = nextConfig

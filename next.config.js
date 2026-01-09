/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:6543/api/:path*', // Proxy vers le backend Pyramid
      },
    ]
  },
}

module.exports = nextConfig
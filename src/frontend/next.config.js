/** @type {import('next').NextConfig} */
const nextConfig = {
  // Configuración experimental para Next.js 15
  experimental: {
    appDir: true,
    serverComponentsExternalPackages: ['@prisma/client'],
  },

  // Configuración de imágenes
  images: {
    domains: [
      'localhost',
      'siame.maeuec.es',
      'blob.core.windows.net', // Azure Blob Storage
    ],
    formats: ['image/webp', 'image/avif'],
  },

  // Variables de entorno públicas
  env: {
    NEXT_PUBLIC_APP_NAME: 'SIAME 2026v3',
    NEXT_PUBLIC_APP_VERSION: '3.0.0',
    NEXT_PUBLIC_MINISTRY: 'Ministerio de Asuntos Exteriores, Unión Europea y Cooperación',
  },

  // Configuración de headers de seguridad
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'X-Frame-Options',
            value: 'DENY',
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
          {
            key: 'Referrer-Policy',
            value: 'strict-origin-when-cross-origin',
          },
          {
            key: 'Permissions-Policy',
            value: 'camera=(), microphone=(), geolocation=()',
          },
        ],
      },
    ];
  },

  // Redirects para rutas de autenticación
  async redirects() {
    return [
      {
        source: '/login',
        destination: '/auth/login',
        permanent: true,
      },
      {
        source: '/register',
        destination: '/auth/register',
        permanent: true,
      },
    ];
  },

  // Configuración para desarrollo
  ...(process.env.NODE_ENV === 'development' && {
    eslint: {
      ignoreDuringBuilds: false,
    },
    typescript: {
      ignoreBuildErrors: false,
    },
  }),

  // Configuración para producción
  ...(process.env.NODE_ENV === 'production' && {
    output: 'standalone',
    compress: true,
    poweredByHeader: false,
    generateEtags: false,
  }),
};

module.exports = nextConfig;
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Output standalone para Docker
  output: 'standalone',

  // Configuración para evitar problemas con antivirus (Norton, Windows Defender)
  webpack: (config, { dev, isServer }) => {
    // Reduce file watching aggressiveness to avoid antivirus conflicts
    if (dev && !isServer) {
      config.watchOptions = {
        poll: 1000, // Check for changes every second
        aggregateTimeout: 300,
        ignored: /node_modules/,
      };
    }
    return config;
  },

  // Experimental features para mejor performance
  experimental: {
    // Optimized package imports
    optimizePackageImports: ['@prisma/client'],
  },
};

export default nextConfig;

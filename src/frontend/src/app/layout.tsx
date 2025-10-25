import type { Metadata } from 'next'
import { Inter, JetBrains_Mono } from 'next/font/google'
import './globals.css'
import { SessionProvider } from '@/components/providers/session-provider'

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-inter',
})

const jetbrainsMono = JetBrains_Mono({
  subsets: ['latin'],
  variable: '--font-jetbrains-mono',
})

export const metadata: Metadata = {
  title: {
    template: '%s | SIAME 2026v3',
    default: 'SIAME 2026v3 - Sistema Inteligente de Administración y Manejo de Expedientes',
  },
  description: 'Sistema Inteligente de Administración y Manejo de Expedientes de la Embajada del Perú en Japón',
  keywords: ['SIAME', 'diplomático', 'documentos', 'gestión', 'Perú', 'Japón', 'embajada'],
  authors: [{ name: 'Embajada del Perú en Japón - Desarrollo Digital' }],
  creator: 'Embajada del Perú en Japón',
  publisher: 'Ministerio de Relaciones Exteriores del Perú',
  robots: {
    index: false,
    follow: false,
  },
  viewport: {
    width: 'device-width',
    initialScale: 1,
    maximumScale: 1,
  },
  other: {
    'security-classification': 'RESTRINGIDO',
    'government-agency': 'Embajada del Perú en Japón',
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="es" className={`${inter.variable} ${jetbrainsMono.variable}`}>
      <body className="min-h-screen bg-background font-sans antialiased">
        <SessionProvider>
          <div className="relative flex min-h-screen flex-col">
            {children}
          </div>
        </SessionProvider>
      </body>
    </html>
  )
}
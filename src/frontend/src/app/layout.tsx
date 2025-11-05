import type { Metadata } from 'next'
import { Inter, JetBrains_Mono } from 'next/font/google'
import './globals.css'
import { SessionProvider } from '@/components/providers/session-provider'
import { Toaster } from '@/components/ui/toaster'

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-inter',
  display: 'swap',
  weight: ['300', '400', '500', '600', '700'],
})

const jetbrainsMono = JetBrains_Mono({
  subsets: ['latin'],
  variable: '--font-jetbrains-mono',
  display: 'swap',
  weight: ['400', '500', '600', '700'],
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
  other: {
    'security-classification': 'RESTRINGIDO',
    'government-agency': 'Embajada del Perú en Japón',
  },
}

export const viewport = {
  width: 'device-width',
  initialScale: 1,
  maximumScale: 1,
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html
      lang="es"
      className={`${inter.variable} ${jetbrainsMono.variable}`}
      suppressHydrationWarning
    >
      <body className="min-h-screen bg-background font-sans text-foreground antialiased" suppressHydrationWarning>
        <a href="#main-content" className="skip-to-content">
          Saltar al contenido principal
        </a>
        <SessionProvider>
          <div className="relative flex min-h-screen flex-col">
            <main id="main-content" className="flex-1">
              {children}
            </main>
          </div>
          <Toaster />
        </SessionProvider>
      </body>
    </html>
  )
}
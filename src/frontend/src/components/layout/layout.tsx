/**
 * SIAME 2026v3 - Layout Principal
 * Componente de layout principal para la aplicación diplomática
 */

"use client"

import * as React from "react"
import { SiteHeader } from "./site-header"
import { SiteFooter } from "./site-footer"
import { SecurityClassification, DiplomaticRole } from "@/types"
import { cn } from "@/lib/utils"

// Componente de contenido principal
interface LayoutProps {
  children: React.ReactNode
  user?: {
    id: string
    name: string
    email: string
    avatar?: string
    role: DiplomaticRole
    securityClearance: SecurityClassification
    embassy?: string
    department?: string
    lastLoginAt?: Date
    sessionExpiresAt?: Date
  }
  showHeader?: boolean
  showFooter?: boolean
  className?: string
}

export function Layout({
  children,
  user,
  showHeader = true,
  showFooter = true,
  className
}: LayoutProps) {
  return (
    <div className="relative flex min-h-screen flex-col">
      {showHeader && <SiteHeader user={user} />}

      <main className={cn("flex-1", className)}>
        {children}
      </main>

      {showFooter && <SiteFooter />}
    </div>
  );
}

// Componente de layout para páginas de autenticación
export function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
      <div className="max-w-md w-full space-y-8">
        {/* Logo del ministerio */}
        <div className="text-center">
          <div className="mx-auto h-16 w-16 bg-blue-600 rounded-full flex items-center justify-center">
            <svg
              className="h-8 w-8 text-white"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"
              />
            </svg>
          </div>
          <h2 className="mt-6 text-center text-3xl font-bold tracking-tight text-gray-900 dark:text-gray-100">
            SIAME 2026v3
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600 dark:text-gray-400">
            Sistema Inteligente de Administración y Manejo de Expedientes
          </p>
          <p className="text-center text-xs text-gray-500 dark:text-gray-500">
            Ministerio de Asuntos Exteriores, Unión Europea y Cooperación
          </p>
        </div>

        {children}
      </div>
    </div>
  );
}

// Componente de layout para dashboards con sidebar
export function DashboardLayout({
  children,
  user,
  sidebar,
  className
}: {
  children: React.ReactNode
  user?: any
  sidebar?: React.ReactNode
  className?: string
}) {
  return (
    <Layout user={user} className="bg-gray-50 dark:bg-gray-900">
      <div className="container mx-auto px-4 py-6">
        <div className={cn("flex gap-6", className)}>
          {sidebar && (
            <aside className="w-64 flex-shrink-0 hidden lg:block">
              <div className="sticky top-24 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
                {sidebar}
              </div>
            </aside>
          )}

          <div className="flex-1 min-w-0">
            {children}
          </div>
        </div>
      </div>
    </Layout>
  );
}

export default Layout;
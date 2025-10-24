"use client"

/**
 * SIAME 2026v3 - Dashboard Principal
 * Panel de control para usuarios diplomáticos
 */

import { useState } from "react"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"

// Tipos para los datos del dashboard
interface DashboardStats {
  totalDocuments: number
  pendingReview: number
  recentUploads: number
  activeWorkflows: number
}

interface RecentDocument {
  id: string
  title: string
  type: string
  classification: string
  uploadedAt: Date
  status: string
}

export default function DashboardPage() {
  // Datos de ejemplo (en producción vendrían de la API)
  const [stats] = useState<DashboardStats>({
    totalDocuments: 1247,
    pendingReview: 23,
    recentUploads: 15,
    activeWorkflows: 8,
  })

  const [recentDocuments] = useState<RecentDocument[]>([
    {
      id: "1",
      title: "Hoja de Remisión OGA-2024-001",
      type: "HOJA_REMISION",
      classification: "CONFIDENCIAL",
      uploadedAt: new Date(Date.now() - 2 * 60 * 60 * 1000),
      status: "PENDING_REVIEW",
    },
    {
      id: "2",
      title: "Guía de Valija Francia-España",
      type: "GUIA_VALIJA",
      classification: "SECRETO",
      uploadedAt: new Date(Date.now() - 5 * 60 * 60 * 1000),
      status: "APPROVED",
    },
    {
      id: "3",
      title: "Comunicación Bilateral",
      type: "NOTA_VERBAL",
      classification: "RESTRINGIDO",
      uploadedAt: new Date(Date.now() - 24 * 60 * 60 * 1000),
      status: "DRAFT",
    },
  ])

  const getClassificationBadge = (classification: string) => {
    const variants: Record<string, any> = {
      PUBLICO: "publico",
      RESTRINGIDO: "restringido",
      CONFIDENCIAL: "confidencial",
      SECRETO: "secreto",
      ALTO_SECRETO: "alto_secreto",
    }
    return variants[classification] || "default"
  }

  const getStatusBadge = (status: string) => {
    const labels: Record<string, string> = {
      DRAFT: "Borrador",
      PENDING_REVIEW: "Pendiente",
      APPROVED: "Aprobado",
      REJECTED: "Rechazado",
    }
    return labels[status] || status
  }

  const formatRelativeTime = (date: Date) => {
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60))

    if (diffHours < 1) return "Hace menos de 1 hora"
    if (diffHours === 1) return "Hace 1 hora"
    if (diffHours < 24) return `Hace ${diffHours} horas`
    const diffDays = Math.floor(diffHours / 24)
    if (diffDays === 1) return "Hace 1 día"
    return `Hace ${diffDays} días`
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <header className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                Dashboard
              </h1>
              <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                Sistema Inteligente de Administración y Manejo de Expedientes
              </p>
            </div>
            <div className="flex items-center gap-4">
              <Button asChild variant="outline">
                <Link href="/documents/search">Buscar</Link>
              </Button>
              <Button asChild>
                <Link href="/documents/upload">Subir Documento</Link>
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {/* Total Documents */}
          <Card>
            <CardHeader className="pb-3">
              <CardDescription>Total de Documentos</CardDescription>
              <CardTitle className="text-3xl">{stats.totalDocuments}</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                En toda la plataforma
              </p>
            </CardContent>
          </Card>

          {/* Pending Review */}
          <Card>
            <CardHeader className="pb-3">
              <CardDescription>Pendientes de Revisión</CardDescription>
              <CardTitle className="text-3xl text-yellow-600 dark:text-yellow-500">
                {stats.pendingReview}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                Requieren atención
              </p>
            </CardContent>
          </Card>

          {/* Recent Uploads */}
          <Card>
            <CardHeader className="pb-3">
              <CardDescription>Subidos Recientemente</CardDescription>
              <CardTitle className="text-3xl text-blue-600 dark:text-blue-500">
                {stats.recentUploads}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                Últimas 24 horas
              </p>
            </CardContent>
          </Card>

          {/* Active Workflows */}
          <Card>
            <CardHeader className="pb-3">
              <CardDescription>Workflows Activos</CardDescription>
              <CardTitle className="text-3xl text-green-600 dark:text-green-500">
                {stats.activeWorkflows}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                En proceso
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Recent Documents */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>Documentos Recientes</CardTitle>
                <CardDescription>
                  Últimos documentos procesados en el sistema
                </CardDescription>
              </div>
              <Button variant="outline" asChild>
                <Link href="/documents">Ver Todos</Link>
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {recentDocuments.map((doc) => (
                <div
                  key={doc.id}
                  className="flex items-center justify-between p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
                >
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-2">
                      <h3 className="text-sm font-medium text-gray-900 dark:text-white truncate">
                        {doc.title}
                      </h3>
                      <Badge variant={getClassificationBadge(doc.classification)}>
                        {doc.classification}
                      </Badge>
                    </div>
                    <div className="flex items-center gap-4 text-xs text-gray-500 dark:text-gray-400">
                      <span>{doc.type.replace(/_/g, " ")}</span>
                      <span>•</span>
                      <span>{formatRelativeTime(doc.uploadedAt)}</span>
                      <span>•</span>
                      <span className="px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded">
                        {getStatusBadge(doc.status)}
                      </span>
                    </div>
                  </div>
                  <Button variant="ghost" size="sm" asChild>
                    <Link href={`/documents/${doc.id}`}>Ver Detalles</Link>
                  </Button>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8">
          <Card className="hover:shadow-lg transition-shadow cursor-pointer">
            <CardHeader>
              <CardTitle className="text-lg flex items-center gap-2">
                <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                Hojas de Remisión
              </CardTitle>
              <CardDescription>
                Gestionar hojas de remisión por unidad
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Button variant="outline" className="w-full" asChild>
                <Link href="/documents/remision">Ir a Remisiones</Link>
              </Button>
            </CardContent>
          </Card>

          <Card className="hover:shadow-lg transition-shadow cursor-pointer">
            <CardHeader>
              <CardTitle className="text-lg flex items-center gap-2">
                <svg className="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
                </svg>
                Valijas Diplomáticas
              </CardTitle>
              <CardDescription>
                Control de valijas y precintos
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Button variant="outline" className="w-full" asChild>
                <Link href="/documents/valija">Ir a Valijas</Link>
              </Button>
            </CardContent>
          </Card>

          <Card className="hover:shadow-lg transition-shadow cursor-pointer">
            <CardHeader>
              <CardTitle className="text-lg flex items-center gap-2">
                <svg className="w-5 h-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                </svg>
                Workflows
              </CardTitle>
              <CardDescription>
                Gestionar flujos de aprobación
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Button variant="outline" className="w-full" asChild>
                <Link href="/workflows">Ir a Workflows</Link>
              </Button>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  )
}

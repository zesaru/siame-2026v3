"use client"

/**
 * SIAME 2026v3 - Detalle de Documento
 * Vista detallada de un documento diplomático
 */

import { useParams } from "next/navigation"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"

export default function DocumentDetailPage() {
  const params = useParams()
  const documentId = params.id as string

  // Datos de ejemplo (en producción vendrían de la API/BD)
  const document = {
    id: documentId,
    title: "Hoja de Remisión OGA-2024-001",
    type: "HOJA_REMISION_OGA",
    classification: "CONFIDENCIAL",
    status: "APPROVED",
    description: "Documentación oficial para tramitación de expediente diplomático relacionado con asuntos bilaterales entre España y Francia.",

    // Metadata
    createdBy: {
      name: "Ana García López",
      role: "CONSEJERO",
      email: "ana.garcia@maeuec.es",
    },
    createdAt: new Date(Date.now() - 2 * 60 * 60 * 1000),
    updatedAt: new Date(Date.now() - 1 * 60 * 60 * 1000),

    // Detalles específicos
    details: {
      numeroDocumento: "OGA-2024-001",
      unidadRemitente: "OGA",
      destino: "Embajada de España en París",
      asunto: "Coordinación de Asuntos Bilaterales",
      observaciones: "Urgente - Requiere respuesta en 48 horas",
    },

    // Archivo
    file: {
      name: "hoja_remision_oga_001.pdf",
      size: "245 KB",
      mimeType: "application/pdf",
      uploadedAt: new Date(Date.now() - 2 * 60 * 60 * 1000),
    },

    // Historial
    history: [
      {
        id: "1",
        action: "APPROVED",
        user: "Carlos Martínez",
        timestamp: new Date(Date.now() - 30 * 60 * 1000),
        comment: "Aprobado para su tramitación",
      },
      {
        id: "2",
        action: "REVIEWED",
        user: "María López",
        timestamp: new Date(Date.now() - 1 * 60 * 60 * 1000),
        comment: "Revisión completada - Todo correcto",
      },
      {
        id: "3",
        action: "CREATED",
        user: "Ana García López",
        timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000),
        comment: "Documento creado",
      },
    ],
  }

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

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      DRAFT: "bg-gray-100 text-gray-800",
      PENDING_REVIEW: "bg-yellow-100 text-yellow-800",
      APPROVED: "bg-green-100 text-green-800",
      REJECTED: "bg-red-100 text-red-800",
      ARCHIVED: "bg-blue-100 text-blue-800",
    }
    return colors[status] || colors.DRAFT
  }

  const formatDateTime = (date: Date) => {
    return new Intl.DateTimeFormat('es-ES', {
      dateStyle: 'medium',
      timeStyle: 'short',
    }).format(date)
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <header className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div>
              <div className="flex items-center gap-3 mb-2">
                <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                  {document.title}
                </h1>
                <Badge variant={getClassificationBadge(document.classification)}>
                  {document.classification}
                </Badge>
                <span className={`text-xs px-3 py-1 rounded-full ${getStatusColor(document.status)}`}>
                  {document.status}
                </span>
              </div>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                {document.type.replace(/_/g, " ")}
              </p>
            </div>
            <div className="flex items-center gap-3">
              <Button variant="outline" asChild>
                <Link href="/documents">Volver a Documentos</Link>
              </Button>
              <Button variant="outline">Descargar PDF</Button>
              <Button>Editar</Button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Columna Principal */}
          <div className="lg:col-span-2 space-y-6">
            {/* Descripción */}
            <Card>
              <CardHeader>
                <CardTitle>Descripción</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-700 dark:text-gray-300">
                  {document.description}
                </p>
              </CardContent>
            </Card>

            {/* Detalles del Documento */}
            <Card>
              <CardHeader>
                <CardTitle>Detalles del Documento</CardTitle>
                <CardDescription>Información específica del documento</CardDescription>
              </CardHeader>
              <CardContent>
                <dl className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <dt className="text-sm font-medium text-gray-500 dark:text-gray-400">
                      Número de Documento
                    </dt>
                    <dd className="mt-1 text-sm text-gray-900 dark:text-white font-semibold">
                      {document.details.numeroDocumento}
                    </dd>
                  </div>
                  <div>
                    <dt className="text-sm font-medium text-gray-500 dark:text-gray-400">
                      Unidad Remitente
                    </dt>
                    <dd className="mt-1 text-sm text-gray-900 dark:text-white">
                      {document.details.unidadRemitente}
                    </dd>
                  </div>
                  <div>
                    <dt className="text-sm font-medium text-gray-500 dark:text-gray-400">
                      Destino
                    </dt>
                    <dd className="mt-1 text-sm text-gray-900 dark:text-white">
                      {document.details.destino}
                    </dd>
                  </div>
                  <div>
                    <dt className="text-sm font-medium text-gray-500 dark:text-gray-400">
                      Asunto
                    </dt>
                    <dd className="mt-1 text-sm text-gray-900 dark:text-white">
                      {document.details.asunto}
                    </dd>
                  </div>
                  <div className="md:col-span-2">
                    <dt className="text-sm font-medium text-gray-500 dark:text-gray-400">
                      Observaciones
                    </dt>
                    <dd className="mt-1 text-sm text-gray-900 dark:text-white">
                      {document.details.observaciones}
                    </dd>
                  </div>
                </dl>
              </CardContent>
            </Card>

            {/* Historial */}
            <Card>
              <CardHeader>
                <CardTitle>Historial de Actividad</CardTitle>
                <CardDescription>Registro de acciones sobre el documento</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {document.history.map((item, index) => (
                    <div key={item.id} className="flex gap-4">
                      <div className="flex flex-col items-center">
                        <div className="w-3 h-3 rounded-full bg-blue-600" />
                        {index < document.history.length - 1 && (
                          <div className="w-px h-full bg-gray-300 dark:bg-gray-600 mt-2" />
                        )}
                      </div>
                      <div className="flex-1 pb-6">
                        <div className="flex items-center justify-between">
                          <div>
                            <p className="text-sm font-medium text-gray-900 dark:text-white">
                              {item.action.replace(/_/g, " ")}
                            </p>
                            <p className="text-xs text-gray-500 dark:text-gray-400">
                              por {item.user}
                            </p>
                          </div>
                          <p className="text-xs text-gray-500 dark:text-gray-400">
                            {formatDateTime(item.timestamp)}
                          </p>
                        </div>
                        {item.comment && (
                          <p className="mt-2 text-sm text-gray-600 dark:text-gray-300">
                            {item.comment}
                          </p>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Información del Archivo */}
            <Card>
              <CardHeader>
                <CardTitle>Archivo</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex items-center gap-3 p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                  <svg className="w-10 h-10 text-red-600" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z" />
                  </svg>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
                      {document.file.name}
                    </p>
                    <p className="text-xs text-gray-500 dark:text-gray-400">
                      {document.file.size} • {document.file.mimeType.split('/')[1].toUpperCase()}
                    </p>
                  </div>
                </div>
                <Button className="w-full" variant="outline">
                  Descargar
                </Button>
                <Button className="w-full" variant="outline">
                  Vista Previa
                </Button>
              </CardContent>
            </Card>

            {/* Metadata */}
            <Card>
              <CardHeader>
                <CardTitle>Información</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <p className="text-xs font-medium text-gray-500 dark:text-gray-400 mb-1">
                    Creado por
                  </p>
                  <p className="text-sm text-gray-900 dark:text-white font-medium">
                    {document.createdBy.name}
                  </p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    {document.createdBy.role}
                  </p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    {document.createdBy.email}
                  </p>
                </div>
                <div>
                  <p className="text-xs font-medium text-gray-500 dark:text-gray-400 mb-1">
                    Fecha de creación
                  </p>
                  <p className="text-sm text-gray-900 dark:text-white">
                    {formatDateTime(document.createdAt)}
                  </p>
                </div>
                <div>
                  <p className="text-xs font-medium text-gray-500 dark:text-gray-400 mb-1">
                    Última modificación
                  </p>
                  <p className="text-sm text-gray-900 dark:text-white">
                    {formatDateTime(document.updatedAt)}
                  </p>
                </div>
              </CardContent>
            </Card>

            {/* Acciones */}
            <Card>
              <CardHeader>
                <CardTitle>Acciones</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                <Button className="w-full" variant="outline">
                  Compartir
                </Button>
                <Button className="w-full" variant="outline">
                  Duplicar
                </Button>
                <Button className="w-full" variant="outline">
                  Archivar
                </Button>
                <Button className="w-full" variant="outline">
                  Exportar
                </Button>
              </CardContent>
            </Card>
          </div>
        </div>
      </main>
    </div>
  )
}

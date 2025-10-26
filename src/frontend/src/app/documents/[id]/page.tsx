"use client"

/**
 * SIAME 2026v3 - Pagina de Detalles de Documento
 * Vista completa de un documento con opciones de descarga y edicion
 */

import { useState, useEffect } from "react"
import { useParams, useRouter } from "next/navigation"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { useToast } from "@/hooks/use-toast"
import { LoadingPage } from "@/components/ui/spinner"
import { Download, Edit, Trash2, ArrowLeft, FileText, Calendar, User, Shield } from "lucide-react"

interface Document {
  id: string
  title: string
  description?: string
  type: string
  classification: string
  status: string
  documentNumber?: string
  originalFileName?: string
  fileSize?: number
  mimeType?: string
  createdAt: string
  updatedAt: string
  creator: {
    id: string
    name: string
    email: string
  }
}

export default function DocumentDetailPage() {
  const params = useParams()
  const router = useRouter()
  const { toast } = useToast()
  const [document, setDocument] = useState<Document | null>(null)
  const [loading, setLoading] = useState(true)
  const [downloading, setDownloading] = useState(false)

  useEffect(() => {
    loadDocument()
  }, [params.id])

  const loadDocument = async () => {
    try {
      const response = await fetch(`/api/documents/${params.id}`)
      const result = await response.json()

      if (!response.ok || !result.success) {
        throw new Error(result.error || "Error al cargar documento")
      }

      setDocument(result.data)
    } catch (error) {
      console.error("Error loading document:", error)
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "No se pudo cargar el documento",
        variant: "destructive",
      })
    } finally {
      setLoading(false)
    }
  }

  const handleDownload = async () => {
    if (!document) return

    setDownloading(true)
    try {
      const response = await fetch(`/api/documents/${document.id}/download`)

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.error || "Error al descargar")
      }

      // Crear blob y descargar
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = window.document.createElement("a")
      a.href = url
      a.download = document.originalFileName || `documento-${document.documentNumber}.pdf`
      window.document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      window.document.body.removeChild(a)

      toast({
        title: "Descarga exitosa",
        description: `${document.originalFileName} descargado`,
        variant: "success",
      })
    } catch (error) {
      console.error("Download error:", error)
      toast({
        title: "Error al descargar",
        description: error instanceof Error ? error.message : "No se pudo descargar el documento",
        variant: "destructive",
      })
    } finally {
      setDownloading(false)
    }
  }

  const formatFileSize = (bytes?: number) => {
    if (!bytes) return "N/A"
    if (bytes < 1024) return `${bytes} B`
    if (bytes < 1048576) return `${(bytes / 1024).toFixed(1)} KB`
    return `${(bytes / 1048576).toFixed(1)} MB`
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("es-ES", {
      year: "numeric",
      month: "long",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    })
  }

  const getDocumentTypeLabel = (type: string) => {
    const labels: Record<string, string> = {
      HOJA_REMISION_OGA: "Hoja de Remision OGA",
      HOJA_REMISION_PCO: "Hoja de Remision PCO",
      HOJA_REMISION_PRU: "Hoja de Remision PRU",
      GUIA_VALIJA_ENTRADA_ORDINARIA: "Guia de Valija - Entrada Ordinaria",
      GUIA_VALIJA_ENTRADA_EXTRAORDINARIA: "Guia de Valija - Entrada Extraordinaria",
      GUIA_VALIJA_SALIDA_ORDINARIA: "Guia de Valija - Salida Ordinaria",
      GUIA_VALIJA_SALIDA_EXTRAORDINARIA: "Guia de Valija - Salida Extraordinaria",
      NOTA_DIPLOMATICA: "Nota Diplomatica",
      DESPACHO_TELEGRAFICO: "Despacho Telegrafico",
      MEMORANDUM_INTERNO: "Memorandum Interno",
      MEMORANDUM_EXTERNO: "Memorandum Externo",
      COMUNICADO_PRENSA: "Comunicado de Prensa",
      INFORME_TECNICO: "Informe Tecnico",
      OTRO: "Otro",
    }
    return labels[type] || type
  }

  const getStatusLabel = (status: string) => {
    const labels: Record<string, string> = {
      DRAFT: "Borrador",
      PENDING_REVIEW: "Pendiente de Revision",
      UNDER_REVIEW: "En Revision",
      APPROVED: "Aprobado",
      REJECTED: "Rechazado",
      ARCHIVED: "Archivado",
      DELETED: "Eliminado",
    }
    return labels[status] || status
  }

  if (loading) {
    return <LoadingPage message="Cargando documento..." />
  }

  if (!document) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Card className="max-w-md">
          <CardHeader>
            <CardTitle>Documento no encontrado</CardTitle>
            <CardDescription>El documento solicitado no existe o no tienes permisos para verlo</CardDescription>
          </CardHeader>
          <CardContent>
            <Button asChild>
              <Link href="/documents">Volver a Documentos</Link>
            </Button>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <div className="border-b bg-card">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Button variant="ghost" size="icon" asChild>
                <Link href="/documents">
                  <ArrowLeft className="h-5 w-5" />
                </Link>
              </Button>
              <div>
                <h1 className="text-2xl font-bold text-foreground">{document.title}</h1>
                {document.documentNumber && (
                  <p className="text-sm text-muted-foreground mt-1">
                    Numero de documento: {document.documentNumber}
                  </p>
                )}
              </div>
            </div>

            <div className="flex items-center gap-2">
              <Button
                onClick={handleDownload}
                disabled={downloading}
                variant="default"
              >
                <Download className="mr-2 h-4 w-4" />
                {downloading ? "Descargando..." : "Descargar"}
              </Button>
              <Button variant="outline" asChild>
                <Link href={`/documents/${document.id}/edit`}>
                  <Edit className="mr-2 h-4 w-4" />
                  Editar
                </Link>
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="container mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Info */}
          <div className="lg:col-span-2 space-y-6">
            {/* Informacion General */}
            <Card>
              <CardHeader>
                <CardTitle>Informacion General</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-muted-foreground">Tipo de Documento</p>
                    <p className="font-medium">{getDocumentTypeLabel(document.type)}</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Estado</p>
                    <Badge variant="outline">{getStatusLabel(document.status)}</Badge>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Clasificacion</p>
                    <Badge variant={document.classification.toLowerCase() as any}>
                      {document.classification}
                    </Badge>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Tamano de Archivo</p>
                    <p className="font-medium">{formatFileSize(document.fileSize)}</p>
                  </div>
                </div>

                {document.description && (
                  <div>
                    <p className="text-sm text-muted-foreground mb-1">Descripcion</p>
                    <p className="text-sm">{document.description}</p>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Archivo */}
            <Card>
              <CardHeader>
                <CardTitle>Archivo</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center gap-4 p-4 border rounded-lg">
                  <div className="p-3 bg-primary/10 rounded-lg">
                    <FileText className="h-8 w-8 text-primary" />
                  </div>
                  <div className="flex-1">
                    <p className="font-medium">{document.originalFileName}</p>
                    <p className="text-sm text-muted-foreground">
                      {document.mimeType} • {formatFileSize(document.fileSize)}
                    </p>
                  </div>
                  <Button onClick={handleDownload} disabled={downloading} size="sm">
                    <Download className="h-4 w-4" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Metadata */}
            <Card>
              <CardHeader>
                <CardTitle>Metadatos</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-start gap-3">
                  <User className="h-5 w-5 text-muted-foreground mt-0.5" />
                  <div>
                    <p className="text-sm text-muted-foreground">Creado por</p>
                    <p className="font-medium">{document.creator.name}</p>
                    <p className="text-xs text-muted-foreground">{document.creator.email}</p>
                  </div>
                </div>

                <div className="flex items-start gap-3">
                  <Calendar className="h-5 w-5 text-muted-foreground mt-0.5" />
                  <div>
                    <p className="text-sm text-muted-foreground">Fecha de creacion</p>
                    <p className="text-sm">{formatDate(document.createdAt)}</p>
                  </div>
                </div>

                <div className="flex items-start gap-3">
                  <Calendar className="h-5 w-5 text-muted-foreground mt-0.5" />
                  <div>
                    <p className="text-sm text-muted-foreground">Ultima modificacion</p>
                    <p className="text-sm">{formatDate(document.updatedAt)}</p>
                  </div>
                </div>

                <div className="flex items-start gap-3">
                  <Shield className="h-5 w-5 text-muted-foreground mt-0.5" />
                  <div>
                    <p className="text-sm text-muted-foreground">Nivel de seguridad</p>
                    <Badge variant={document.classification.toLowerCase() as any} className="mt-1">
                      {document.classification}
                    </Badge>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Acciones */}
            <Card>
              <CardHeader>
                <CardTitle>Acciones</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                <Button variant="outline" className="w-full justify-start" asChild>
                  <Link href={`/documents/${document.id}/edit`}>
                    <Edit className="mr-2 h-4 w-4" />
                    Editar Documento
                  </Link>
                </Button>
                <Button variant="outline" className="w-full justify-start text-destructive hover:text-destructive">
                  <Trash2 className="mr-2 h-4 w-4" />
                  Eliminar Documento
                </Button>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  )
}

"use client"

/**
 * SIAME 2026v3 - Página de Documentos
 * Listado y gestión de documentos diplomáticos con sorting y paginación
 */

import * as React from "react"
import { useState } from "react"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Select } from "@/components/ui/select"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { EmptyState } from "@/components/ui/empty-state"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { FileText, ChevronUp, ChevronDown, ChevronsUpDown, ChevronLeft, ChevronRight, Download } from "lucide-react"

// Tipos de documentos
interface Document {
  id: string
  title: string
  type: string
  classification: string
  status: string
  createdBy: string
  createdAt: Date
  size: string
}

export default function DocumentsPage() {
  // Datos de ejemplo
  const [documents] = useState<Document[]>([
    {
      id: "1",
      title: "Hoja de Remisión OGA-2024-001",
      type: "HOJA_REMISION_OGA",
      classification: "CONFIDENCIAL",
      status: "APPROVED",
      createdBy: "Ana García",
      createdAt: new Date(Date.now() - 2 * 60 * 60 * 1000),
      size: "245 KB",
    },
    {
      id: "2",
      title: "Guía de Valija Diplomática GV-FR-001",
      type: "GUIA_VALIJA",
      classification: "SECRETO",
      status: "PENDING_REVIEW",
      createdBy: "Carlos Martínez",
      createdAt: new Date(Date.now() - 5 * 60 * 60 * 1000),
      size: "1.2 MB",
    },
    {
      id: "3",
      title: "Nota Verbal - Asunto Bilateral",
      type: "NOTA_VERBAL",
      classification: "RESTRINGIDO",
      status: "DRAFT",
      createdBy: "María López",
      createdAt: new Date(Date.now() - 24 * 60 * 60 * 1000),
      size: "156 KB",
    },
    {
      id: "4",
      title: "Telegrama Ordinario TO-2024-042",
      type: "TELEGRAMA_ORDINARIO",
      classification: "CONFIDENCIAL",
      status: "APPROVED",
      createdBy: "Juan Rodríguez",
      createdAt: new Date(Date.now() - 48 * 60 * 60 * 1000),
      size: "89 KB",
    },
    {
      id: "5",
      title: "Informe de Seguridad IS-2024-03",
      type: "INFORME",
      classification: "ALTO_SECRETO",
      status: "ARCHIVED",
      createdBy: "Patricia Sánchez",
      createdAt: new Date(Date.now() - 72 * 60 * 60 * 1000),
      size: "3.4 MB",
    },
  ])

  const [searchTerm, setSearchTerm] = useState("")
  const [filterType, setFilterType] = useState("all")
  const [filterClassification, setFilterClassification] = useState("all")

  // Sorting
  type SortField = "title" | "type" | "classification" | "status" | "createdBy" | "createdAt" | "size"
  const [sortField, setSortField] = useState<SortField>("createdAt")
  const [sortDirection, setSortDirection] = useState<"asc" | "desc">("desc")

  // Paginación
  const [currentPage, setCurrentPage] = useState(1)
  const itemsPerPage = 10

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

  const getStatusLabel = (status: string) => {
    const labels: Record<string, string> = {
      DRAFT: "Borrador",
      PENDING_REVIEW: "Pendiente",
      APPROVED: "Aprobado",
      REJECTED: "Rechazado",
      ARCHIVED: "Archivado",
    }
    return labels[status] || status
  }

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      DRAFT: "bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-300",
      PENDING_REVIEW: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-400",
      APPROVED: "bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400",
      REJECTED: "bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400",
      ARCHIVED: "bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-400",
    }
    return colors[status] || colors.DRAFT
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

  // Funciones de sorting
  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortDirection(sortDirection === "asc" ? "desc" : "asc")
    } else {
      setSortField(field)
      setSortDirection("asc")
    }
    setCurrentPage(1) // Reset to first page when sorting
  }

  const getSortIcon = (field: SortField) => {
    if (sortField !== field) {
      return <ChevronsUpDown className="h-4 w-4 ml-1 text-muted-foreground" />
    }
    return sortDirection === "asc" ? (
      <ChevronUp className="h-4 w-4 ml-1" />
    ) : (
      <ChevronDown className="h-4 w-4 ml-1" />
    )
  }

  // Filtrar documentos
  const filteredDocuments = documents.filter(doc => {
    const matchesSearch = doc.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         doc.createdBy.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesType = filterType === "all" || doc.type === filterType
    const matchesClassification = filterClassification === "all" || doc.classification === filterClassification

    return matchesSearch && matchesType && matchesClassification
  })

  // Ordenar documentos
  const sortedDocuments = [...filteredDocuments].sort((a, b) => {
    let aValue: any = a[sortField]
    let bValue: any = b[sortField]

    if (sortField === "createdAt") {
      aValue = a.createdAt.getTime()
      bValue = b.createdAt.getTime()
    }

    if (aValue < bValue) return sortDirection === "asc" ? -1 : 1
    if (aValue > bValue) return sortDirection === "asc" ? 1 : -1
    return 0
  })

  // Paginación
  const totalPages = Math.ceil(sortedDocuments.length / itemsPerPage)
  const startIndex = (currentPage - 1) * itemsPerPage
  const endIndex = startIndex + itemsPerPage
  const paginatedDocuments = sortedDocuments.slice(startIndex, endIndex)

  const goToPage = (page: number) => {
    setCurrentPage(Math.max(1, Math.min(page, totalPages)))
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <header className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                Documentos
              </h1>
              <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                Gestión de documentos diplomáticos
              </p>
            </div>
            <div className="flex items-center gap-4">
              <Button variant="outline" asChild>
                <Link href="/dashboard">Volver al Dashboard</Link>
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
        {/* Filtros */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>Filtros de Búsqueda</CardTitle>
            <CardDescription>
              Busca y filtra documentos por diferentes criterios
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {/* Búsqueda */}
              <div className="space-y-2">
                <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  Buscar
                </label>
                <Input
                  type="text"
                  placeholder="Título o autor..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>

              {/* Tipo de Documento */}
              <div className="space-y-2">
                <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  Tipo de Documento
                </label>
                <Select
                  value={filterType}
                  onChange={(e) => setFilterType(e.target.value)}
                >
                  <option value="all">Todos los tipos</option>
                  <option value="HOJA_REMISION_OGA">Hoja de Remisión OGA</option>
                  <option value="GUIA_VALIJA">Guía de Valija</option>
                  <option value="NOTA_VERBAL">Nota Verbal</option>
                  <option value="TELEGRAMA_ORDINARIO">Telegrama</option>
                  <option value="INFORME">Informe</option>
                </Select>
              </div>

              {/* Clasificación */}
              <div className="space-y-2">
                <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  Clasificación
                </label>
                <Select
                  value={filterClassification}
                  onChange={(e) => setFilterClassification(e.target.value)}
                >
                  <option value="all">Todas las clasificaciones</option>
                  <option value="PUBLICO">Público</option>
                  <option value="RESTRINGIDO">Restringido</option>
                  <option value="CONFIDENCIAL">Confidencial</option>
                  <option value="SECRETO">Secreto</option>
                  <option value="ALTO_SECRETO">Alto Secreto</option>
                </Select>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Tabla de Documentos */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>Lista de Documentos</CardTitle>
                <CardDescription>
                  {filteredDocuments.length} documento(s) encontrado(s)
                </CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>
                    <button
                      onClick={() => handleSort("title")}
                      className="flex items-center hover:text-foreground"
                      aria-label="Ordenar por documento"
                    >
                      Documento
                      {getSortIcon("title")}
                    </button>
                  </TableHead>
                  <TableHead>
                    <button
                      onClick={() => handleSort("type")}
                      className="flex items-center hover:text-foreground"
                      aria-label="Ordenar por tipo"
                    >
                      Tipo
                      {getSortIcon("type")}
                    </button>
                  </TableHead>
                  <TableHead>
                    <button
                      onClick={() => handleSort("classification")}
                      className="flex items-center hover:text-foreground"
                      aria-label="Ordenar por clasificación"
                    >
                      Clasificación
                      {getSortIcon("classification")}
                    </button>
                  </TableHead>
                  <TableHead>
                    <button
                      onClick={() => handleSort("status")}
                      className="flex items-center hover:text-foreground"
                      aria-label="Ordenar por estado"
                    >
                      Estado
                      {getSortIcon("status")}
                    </button>
                  </TableHead>
                  <TableHead>
                    <button
                      onClick={() => handleSort("createdBy")}
                      className="flex items-center hover:text-foreground"
                      aria-label="Ordenar por creador"
                    >
                      Creado por
                      {getSortIcon("createdBy")}
                    </button>
                  </TableHead>
                  <TableHead>
                    <button
                      onClick={() => handleSort("createdAt")}
                      className="flex items-center hover:text-foreground"
                      aria-label="Ordenar por fecha"
                    >
                      Fecha
                      {getSortIcon("createdAt")}
                    </button>
                  </TableHead>
                  <TableHead>Tamaño</TableHead>
                  <TableHead className="text-right">Acciones</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {paginatedDocuments.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={8} className="p-0">
                      <EmptyState
                        icon={FileText}
                        title="No se encontraron documentos"
                        description="Intenta ajustar los filtros de búsqueda para encontrar lo que buscas."
                      />
                    </TableCell>
                  </TableRow>
                ) : (
                  paginatedDocuments.map((doc) => (
                    <TableRow key={doc.id}>
                      <TableCell className="font-medium">
                        <Link
                          href={`/documents/${doc.id}`}
                          className="hover:text-blue-600 dark:hover:text-blue-400"
                        >
                          {doc.title}
                        </Link>
                      </TableCell>
                      <TableCell>
                        <span className="text-xs text-gray-600 dark:text-gray-400">
                          {doc.type.replace(/_/g, " ")}
                        </span>
                      </TableCell>
                      <TableCell>
                        <Badge variant={getClassificationBadge(doc.classification)}>
                          {doc.classification}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <span className={`text-xs px-2 py-1 rounded-full ${getStatusColor(doc.status)}`}>
                          {getStatusLabel(doc.status)}
                        </span>
                      </TableCell>
                      <TableCell className="text-sm text-gray-600 dark:text-gray-400">
                        {doc.createdBy}
                      </TableCell>
                      <TableCell className="text-sm text-gray-600 dark:text-gray-400">
                        {formatRelativeTime(doc.createdAt)}
                      </TableCell>
                      <TableCell className="text-sm text-gray-600 dark:text-gray-400">
                        {doc.size}
                      </TableCell>
                      <TableCell className="text-right">
                        <div className="flex items-center justify-end gap-2">
                          <Button variant="ghost" size="sm" asChild>
                            <Link href={`/documents/${doc.id}`}>Ver</Link>
                          </Button>
                          <Button variant="ghost" size="sm" asChild>
                            <Link href={`/api/documents/${doc.id}/download`} download>
                              <Download className="h-4 w-4" />
                            </Link>
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>

            {/* Paginación */}
            {sortedDocuments.length > itemsPerPage && (
              <div className="flex items-center justify-between mt-4 pt-4 border-t">
                <div className="text-sm text-muted-foreground">
                  Mostrando {startIndex + 1} a {Math.min(endIndex, sortedDocuments.length)} de {sortedDocuments.length} documentos
                </div>
                <div className="flex items-center space-x-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => goToPage(currentPage - 1)}
                    disabled={currentPage === 1}
                    aria-label="Página anterior"
                  >
                    <ChevronLeft className="h-4 w-4" />
                  </Button>

                  <div className="flex items-center gap-1">
                    {Array.from({ length: totalPages }, (_, i) => i + 1)
                      .filter(page => {
                        // Show first page, last page, current page, and pages around current
                        return (
                          page === 1 ||
                          page === totalPages ||
                          (page >= currentPage - 1 && page <= currentPage + 1)
                        )
                      })
                      .map((page, index, array) => (
                        <React.Fragment key={page}>
                          {index > 0 && array[index - 1] !== page - 1 && (
                            <span className="px-2 text-muted-foreground">...</span>
                          )}
                          <Button
                            variant={currentPage === page ? "default" : "outline"}
                            size="sm"
                            onClick={() => goToPage(page)}
                            className="w-10"
                            aria-label={`Ir a página ${page}`}
                            aria-current={currentPage === page ? "page" : undefined}
                          >
                            {page}
                          </Button>
                        </React.Fragment>
                      ))}
                  </div>

                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => goToPage(currentPage + 1)}
                    disabled={currentPage === totalPages}
                    aria-label="Página siguiente"
                  >
                    <ChevronRight className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </main>
    </div>
  )
}

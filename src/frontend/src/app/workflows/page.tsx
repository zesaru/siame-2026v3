"use client"

/**
 * SIAME 2026v3 - Workflows
 * Gestión de flujos de trabajo y aprobaciones
 */

import { useState } from "react"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Select } from "@/components/ui/select"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"

interface Workflow {
  id: string
  name: string
  type: string
  status: string
  currentStep: string
  totalSteps: number
  completedSteps: number
  assignedTo: string
  dueDate: Date
  priority: string
  documents: number
}

export default function WorkflowsPage() {
  const [workflows] = useState<Workflow[]>([
    {
      id: "1",
      name: "Aprobación de Hoja de Remisión OGA-2024-001",
      type: "DOCUMENT_APPROVAL",
      status: "IN_PROGRESS",
      currentStep: "Revisión Legal",
      totalSteps: 4,
      completedSteps: 2,
      assignedTo: "María López",
      dueDate: new Date(Date.now() + 24 * 60 * 60 * 1000),
      priority: "HIGH",
      documents: 1,
    },
    {
      id: "2",
      name: "Validación de Guía de Valija Diplomática",
      type: "VALIJA_VALIDATION",
      status: "PENDING",
      currentStep: "Pendiente de Inicio",
      totalSteps: 5,
      completedSteps: 0,
      assignedTo: "Carlos Martínez",
      dueDate: new Date(Date.now() + 48 * 60 * 60 * 1000),
      priority: "URGENT",
      documents: 3,
    },
    {
      id: "3",
      name: "Archivo de Documentos Q4 2024",
      type: "ARCHIVAL",
      status: "COMPLETED",
      currentStep: "Completado",
      totalSteps: 3,
      completedSteps: 3,
      assignedTo: "Ana García",
      dueDate: new Date(Date.now() - 48 * 60 * 60 * 1000),
      priority: "NORMAL",
      documents: 45,
    },
    {
      id: "4",
      name: "Revisión de Seguridad Mensual",
      type: "SECURITY_REVIEW",
      status: "IN_PROGRESS",
      currentStep: "Análisis de Clasificación",
      totalSteps: 6,
      completedSteps: 4,
      assignedTo: "Juan Rodríguez",
      dueDate: new Date(Date.now() + 72 * 60 * 60 * 1000),
      priority: "HIGH",
      documents: 12,
    },
  ])

  const [filterStatus, setFilterStatus] = useState("all")
  const [filterPriority, setFilterPriority] = useState("all")

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      PENDING: "bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-300",
      IN_PROGRESS: "bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-400",
      COMPLETED: "bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400",
      CANCELLED: "bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400",
    }
    return colors[status] || colors.PENDING
  }

  const getPriorityBadge = (priority: string) => {
    const variants: Record<string, any> = {
      URGENT: "alto_secreto",
      HIGH: "secreto",
      NORMAL: "restringido",
      LOW: "publico",
    }
    return variants[priority] || "default"
  }

  const getPriorityLabel = (priority: string) => {
    const labels: Record<string, string> = {
      URGENT: "Urgente",
      HIGH: "Alta",
      NORMAL: "Normal",
      LOW: "Baja",
    }
    return labels[priority] || priority
  }

  const formatDate = (date: Date) => {
    const now = new Date()
    const diffMs = date.getTime() - now.getTime()
    const diffDays = Math.ceil(diffMs / (1000 * 60 * 60 * 24))

    if (diffDays < 0) return `Vencido hace ${Math.abs(diffDays)} días`
    if (diffDays === 0) return "Vence hoy"
    if (diffDays === 1) return "Vence mañana"
    return `Vence en ${diffDays} días`
  }

  const filteredWorkflows = workflows.filter(wf => {
    const matchesStatus = filterStatus === "all" || wf.status === filterStatus
    const matchesPriority = filterPriority === "all" || wf.priority === filterPriority
    return matchesStatus && matchesPriority
  })

  const stats = {
    total: workflows.length,
    pending: workflows.filter(w => w.status === "PENDING").length,
    inProgress: workflows.filter(w => w.status === "IN_PROGRESS").length,
    completed: workflows.filter(w => w.status === "COMPLETED").length,
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <header className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                Workflows
              </h1>
              <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                Gestión de flujos de trabajo y aprobaciones
              </p>
            </div>
            <div className="flex items-center gap-4">
              <Button variant="outline" asChild>
                <Link href="/dashboard">Volver al Dashboard</Link>
              </Button>
              <Button asChild>
                <Link href="/workflows/new">Crear Workflow</Link>
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Estadísticas */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardHeader className="pb-3">
              <CardDescription>Total de Workflows</CardDescription>
              <CardTitle className="text-3xl">{stats.total}</CardTitle>
            </CardHeader>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <CardDescription>Pendientes</CardDescription>
              <CardTitle className="text-3xl text-gray-600 dark:text-gray-400">
                {stats.pending}
              </CardTitle>
            </CardHeader>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <CardDescription>En Progreso</CardDescription>
              <CardTitle className="text-3xl text-blue-600 dark:text-blue-500">
                {stats.inProgress}
              </CardTitle>
            </CardHeader>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <CardDescription>Completados</CardDescription>
              <CardTitle className="text-3xl text-green-600 dark:text-green-500">
                {stats.completed}
              </CardTitle>
            </CardHeader>
          </Card>
        </div>

        {/* Filtros */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>Filtros</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  Estado
                </label>
                <Select
                  value={filterStatus}
                  onChange={(e) => setFilterStatus(e.target.value)}
                >
                  <option value="all">Todos los estados</option>
                  <option value="PENDING">Pendiente</option>
                  <option value="IN_PROGRESS">En Progreso</option>
                  <option value="COMPLETED">Completado</option>
                  <option value="CANCELLED">Cancelado</option>
                </Select>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  Prioridad
                </label>
                <Select
                  value={filterPriority}
                  onChange={(e) => setFilterPriority(e.target.value)}
                >
                  <option value="all">Todas las prioridades</option>
                  <option value="URGENT">Urgente</option>
                  <option value="HIGH">Alta</option>
                  <option value="NORMAL">Normal</option>
                  <option value="LOW">Baja</option>
                </Select>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Tabla de Workflows */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>Lista de Workflows</CardTitle>
                <CardDescription>
                  {filteredWorkflows.length} workflow(s) encontrado(s)
                </CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Workflow</TableHead>
                  <TableHead>Progreso</TableHead>
                  <TableHead>Estado</TableHead>
                  <TableHead>Prioridad</TableHead>
                  <TableHead>Asignado a</TableHead>
                  <TableHead>Vencimiento</TableHead>
                  <TableHead>Docs</TableHead>
                  <TableHead className="text-right">Acciones</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredWorkflows.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={8} className="text-center text-gray-500 py-8">
                      No se encontraron workflows
                    </TableCell>
                  </TableRow>
                ) : (
                  filteredWorkflows.map((workflow) => (
                    <TableRow key={workflow.id}>
                      <TableCell>
                        <div>
                          <Link
                            href={`/workflows/${workflow.id}`}
                            className="font-medium hover:text-blue-600 dark:hover:text-blue-400"
                          >
                            {workflow.name}
                          </Link>
                          <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                            {workflow.type.replace(/_/g, " ")}
                          </p>
                        </div>
                      </TableCell>
                      <TableCell>
                        <div className="space-y-1">
                          <div className="flex items-center gap-2">
                            <div className="flex-1 h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                              <div
                                className="h-full bg-blue-600"
                                style={{
                                  width: `${(workflow.completedSteps / workflow.totalSteps) * 100}%`,
                                }}
                              />
                            </div>
                          </div>
                          <p className="text-xs text-gray-500 dark:text-gray-400">
                            {workflow.completedSteps}/{workflow.totalSteps} - {workflow.currentStep}
                          </p>
                        </div>
                      </TableCell>
                      <TableCell>
                        <span className={`text-xs px-2 py-1 rounded-full ${getStatusColor(workflow.status)}`}>
                          {workflow.status.replace(/_/g, " ")}
                        </span>
                      </TableCell>
                      <TableCell>
                        <Badge variant={getPriorityBadge(workflow.priority)}>
                          {getPriorityLabel(workflow.priority)}
                        </Badge>
                      </TableCell>
                      <TableCell className="text-sm">
                        {workflow.assignedTo}
                      </TableCell>
                      <TableCell>
                        <span
                          className={`text-xs ${
                            workflow.dueDate < new Date()
                              ? "text-red-600 dark:text-red-400 font-semibold"
                              : "text-gray-600 dark:text-gray-400"
                          }`}
                        >
                          {formatDate(workflow.dueDate)}
                        </span>
                      </TableCell>
                      <TableCell className="text-sm text-gray-600 dark:text-gray-400">
                        {workflow.documents}
                      </TableCell>
                      <TableCell className="text-right">
                        <Button variant="ghost" size="sm" asChild>
                          <Link href={`/workflows/${workflow.id}`}>Ver</Link>
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      </main>
    </div>
  )
}

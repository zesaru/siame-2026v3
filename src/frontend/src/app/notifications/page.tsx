"use client"

/**
 * SIAME 2026v3 - Notificaciones
 * Centro de notificaciones del sistema
 */

import { useState } from "react"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"

interface Notification {
  id: string
  type: string
  title: string
  message: string
  read: boolean
  createdAt: Date
  actionUrl?: string
  metadata?: any
}

export default function NotificationsPage() {
  const [notifications, setNotifications] = useState<Notification[]>([
    {
      id: "1",
      type: "DOCUMENT_APPROVED",
      title: "Documento Aprobado",
      message: "Tu hoja de remisión OGA-2024-001 ha sido aprobada",
      read: false,
      createdAt: new Date(Date.now() - 30 * 60 * 1000),
      actionUrl: "/documents/1",
    },
    {
      id: "2",
      type: "WORKFLOW_ASSIGNED",
      title: "Workflow Asignado",
      message: "Se te ha asignado el workflow 'Validación de Guía de Valija'",
      read: false,
      createdAt: new Date(Date.now() - 2 * 60 * 60 * 1000),
      actionUrl: "/workflows/2",
    },
    {
      id: "3",
      type: "COMMENT_ADDED",
      title: "Nuevo Comentario",
      message: "María López comentó en tu documento",
      read: true,
      createdAt: new Date(Date.now() - 5 * 60 * 60 * 1000),
      actionUrl: "/documents/1#comments",
    },
    {
      id: "4",
      type: "SECURITY_ALERT",
      title: "Alerta de Seguridad",
      message: "Intento de acceso no autorizado a documento clasificado",
      read: true,
      createdAt: new Date(Date.now() - 24 * 60 * 60 * 1000),
      actionUrl: "/admin/security",
    },
  ])

  const [filter, setFilter] = useState<"all" | "unread">("all")

  const getNotificationIcon = (type: string) => {
    const icons: Record<string, string> = {
      DOCUMENT_APPROVED: "✅",
      DOCUMENT_REJECTED: "❌",
      WORKFLOW_ASSIGNED: "📋",
      COMMENT_ADDED: "💬",
      SECURITY_ALERT: "🔒",
      MENTION: "👤",
      SYSTEM: "⚙️",
    }
    return icons[type] || "📬"
  }

  const getNotificationColor = (type: string) => {
    const colors: Record<string, string> = {
      DOCUMENT_APPROVED: "bg-green-50 dark:bg-green-900/10 border-green-200 dark:border-green-800",
      DOCUMENT_REJECTED: "bg-red-50 dark:bg-red-900/10 border-red-200 dark:border-red-800",
      WORKFLOW_ASSIGNED: "bg-blue-50 dark:bg-blue-900/10 border-blue-200 dark:border-blue-800",
      COMMENT_ADDED: "bg-purple-50 dark:bg-purple-900/10 border-purple-200 dark:border-purple-800",
      SECURITY_ALERT: "bg-orange-50 dark:bg-orange-900/10 border-orange-200 dark:border-orange-800",
      MENTION: "bg-yellow-50 dark:bg-yellow-900/10 border-yellow-200 dark:border-yellow-800",
      SYSTEM: "bg-gray-50 dark:bg-gray-900/10 border-gray-200 dark:border-gray-800",
    }
    return colors[type] || colors.SYSTEM
  }

  const formatTime = (date: Date) => {
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffMins = Math.floor(diffMs / (1000 * 60))
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60))
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))

    if (diffMins < 1) return "Ahora"
    if (diffMins < 60) return `Hace ${diffMins}m`
    if (diffHours < 24) return `Hace ${diffHours}h`
    return `Hace ${diffDays}d`
  }

  const markAsRead = (id: string) => {
    setNotifications(notifications.map(n =>
      n.id === id ? { ...n, read: true } : n
    ))
  }

  const markAllAsRead = () => {
    setNotifications(notifications.map(n => ({ ...n, read: true })))
  }

  const deleteNotification = (id: string) => {
    setNotifications(notifications.filter(n => n.id !== id))
  }

  const filteredNotifications = filter === "unread"
    ? notifications.filter(n => !n.read)
    : notifications

  const unreadCount = notifications.filter(n => !n.read).length

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <header className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                Notificaciones
                {unreadCount > 0 && (
                  <Badge variant="secreto" className="ml-3">
                    {unreadCount} nueva{unreadCount !== 1 ? "s" : ""}
                  </Badge>
                )}
              </h1>
              <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                Centro de notificaciones del sistema
              </p>
            </div>
            <Button variant="outline" asChild>
              <Link href="/dashboard">Volver</Link>
            </Button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Actions */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex gap-2">
            <Button
              variant={filter === "all" ? "default" : "outline"}
              size="sm"
              onClick={() => setFilter("all")}
            >
              Todas ({notifications.length})
            </Button>
            <Button
              variant={filter === "unread" ? "default" : "outline"}
              size="sm"
              onClick={() => setFilter("unread")}
            >
              No leídas ({unreadCount})
            </Button>
          </div>

          {unreadCount > 0 && (
            <Button variant="ghost" size="sm" onClick={markAllAsRead}>
              Marcar todas como leídas
            </Button>
          )}
        </div>

        {/* Notifications List */}
        <div className="space-y-3">
          {filteredNotifications.length === 0 ? (
            <Card>
              <CardContent className="flex flex-col items-center justify-center py-12">
                <div className="text-6xl mb-4">📭</div>
                <p className="text-gray-600 dark:text-gray-400 text-center">
                  {filter === "unread"
                    ? "No tienes notificaciones sin leer"
                    : "No tienes notificaciones"}
                </p>
              </CardContent>
            </Card>
          ) : (
            filteredNotifications.map((notification) => (
              <Card
                key={notification.id}
                className={cn(
                  "transition-all hover:shadow-md",
                  !notification.read && "border-l-4",
                  !notification.read && getNotificationColor(notification.type)
                )}
              >
                <CardContent className="flex items-start gap-4 p-4">
                  {/* Icon */}
                  <div className="text-3xl">
                    {getNotificationIcon(notification.type)}
                  </div>

                  {/* Content */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex-1">
                        <h3 className={cn(
                          "text-sm font-medium",
                          !notification.read ? "text-gray-900 dark:text-white" : "text-gray-600 dark:text-gray-400"
                        )}>
                          {notification.title}
                        </h3>
                        <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                          {notification.message}
                        </p>
                      </div>
                      <span className="text-xs text-gray-500 dark:text-gray-500 whitespace-nowrap">
                        {formatTime(notification.createdAt)}
                      </span>
                    </div>

                    {/* Actions */}
                    <div className="flex items-center gap-3 mt-3">
                      {notification.actionUrl && (
                        <Button
                          variant="ghost"
                          size="sm"
                          asChild
                          onClick={() => markAsRead(notification.id)}
                        >
                          <Link href={notification.actionUrl}>
                            Ver detalles
                          </Link>
                        </Button>
                      )}
                      {!notification.read && (
                        <button
                          onClick={() => markAsRead(notification.id)}
                          className="text-xs text-blue-600 dark:text-blue-400 hover:underline"
                        >
                          Marcar como leída
                        </button>
                      )}
                      <button
                        onClick={() => deleteNotification(notification.id)}
                        className="text-xs text-red-600 dark:text-red-400 hover:underline"
                      >
                        Eliminar
                      </button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))
          )}
        </div>
      </main>
    </div>
  )
}

function cn(...classes: any[]) {
  return classes.filter(Boolean).join(" ")
}

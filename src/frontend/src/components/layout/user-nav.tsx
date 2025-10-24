/**
 * SIAME 2026v3 - Navegación de Usuario
 * Componente de navegación específico del usuario con información diplomática
 */

"use client"

import * as React from "react"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { SecurityClassification, DiplomaticRole } from "@/types"

// Iconos
import {
  User,
  Settings,
  Shield,
  LogOut,
  ChevronDown,
  Building,
  Mail,
  Clock,
  Key,
  AlertTriangle
} from "lucide-react"

interface UserNavProps {
  user: {
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
}

// Función para obtener el color del avatar basado en el rol
function getAvatarColor(role: DiplomaticRole): string {
  switch (role) {
    case DiplomaticRole.EMBAJADOR:
      return "bg-purple-600";
    case DiplomaticRole.MINISTRO_CONSEJERO:
      return "bg-indigo-600";
    case DiplomaticRole.CONSEJERO:
      return "bg-blue-600";
    case DiplomaticRole.PRIMER_SECRETARIO:
      return "bg-green-600";
    case DiplomaticRole.SEGUNDO_SECRETARIO:
      return "bg-yellow-600";
    case DiplomaticRole.TERCER_SECRETARIO:
      return "bg-orange-600";
    case DiplomaticRole.AGREGADO:
      return "bg-teal-600";
    case DiplomaticRole.FUNCIONARIO_ADMINISTRATIVO:
      return "bg-gray-600";
    case DiplomaticRole.CONSULTOR_EXTERNO:
      return "bg-pink-600";
    case DiplomaticRole.INVITADO:
      return "bg-red-600";
    default:
      return "bg-gray-600";
  }
}

// Función para obtener las iniciales del nombre
function getInitials(name: string): string {
  return name
    .split(" ")
    .map((n) => n[0])
    .join("")
    .toUpperCase()
    .slice(0, 2);
}

// Función para formatear la fecha de última conexión
function formatLastLogin(date?: Date): string {
  if (!date) return "Nunca";

  const now = new Date();
  const diffInHours = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60));

  if (diffInHours < 1) return "Hace menos de 1 hora";
  if (diffInHours < 24) return `Hace ${diffInHours} horas`;

  const diffInDays = Math.floor(diffInHours / 24);
  return `Hace ${diffInDays} días`;
}

// Función para verificar si la sesión está próxima a expirar
function isSessionNearExpiry(expiresAt?: Date): boolean {
  if (!expiresAt) return false;

  const now = new Date();
  const timeDiff = expiresAt.getTime() - now.getTime();
  const minutesLeft = Math.floor(timeDiff / (1000 * 60));

  return minutesLeft <= 15 && minutesLeft > 0;
}

// Función para obtener el color del badge de clearance
function getClearanceBadgeVariant(clearance: SecurityClassification) {
  switch (clearance) {
    case SecurityClassification.PUBLICO:
      return "publico";
    case SecurityClassification.RESTRINGIDO:
      return "restringido";
    case SecurityClassification.CONFIDENCIAL:
      return "confidencial";
    case SecurityClassification.SECRETO:
      return "secreto";
    case SecurityClassification.ALTO_SECRETO:
      return "alto_secreto";
    default:
      return "default";
  }
}

export function UserNav({ user }: UserNavProps) {
  const [isOpen, setIsOpen] = React.useState(false);
  const nearExpiry = isSessionNearExpiry(user.sessionExpiresAt);

  return (
    <div className="relative">
      <Button
        variant="ghost"
        className="relative h-10 w-auto px-2 flex items-center space-x-2"
        onClick={() => setIsOpen(!isOpen)}
      >
        {/* Avatar */}
        <div className={`h-8 w-8 rounded-full ${getAvatarColor(user.role)} flex items-center justify-center text-white text-sm font-medium`}>
          {user.avatar ? (
            <img
              src={user.avatar}
              alt={user.name}
              className="h-8 w-8 rounded-full object-cover"
            />
          ) : (
            getInitials(user.name)
          )}
        </div>

        {/* Información del usuario */}
        <div className="hidden md:block text-left">
          <div className="text-sm font-medium leading-none">{user.name}</div>
          <div className="text-xs text-muted-foreground leading-none mt-1">
            {user.embassy || user.department || user.email}
          </div>
        </div>

        <ChevronDown className="h-4 w-4" />

        {/* Indicador de sesión próxima a expirar */}
        {nearExpiry && (
          <div className="absolute -top-1 -right-1 h-3 w-3 bg-orange-500 rounded-full animate-pulse" />
        )}
      </Button>

      {/* Menú desplegable */}
      {isOpen && (
        <>
          {/* Overlay para cerrar el menú */}
          <div
            className="fixed inset-0 z-40"
            onClick={() => setIsOpen(false)}
          />

          {/* Contenido del menú */}
          <div className="absolute right-0 top-full mt-2 w-80 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-md shadow-lg z-50">
            {/* Información del usuario */}
            <div className="p-4 border-b border-gray-200 dark:border-gray-700">
              <div className="flex items-start space-x-3">
                <div className={`h-12 w-12 rounded-full ${getAvatarColor(user.role)} flex items-center justify-center text-white text-lg font-medium`}>
                  {user.avatar ? (
                    <img
                      src={user.avatar}
                      alt={user.name}
                      className="h-12 w-12 rounded-full object-cover"
                    />
                  ) : (
                    getInitials(user.name)
                  )}
                </div>

                <div className="flex-1 min-w-0">
                  <div className="text-sm font-medium text-gray-900 dark:text-gray-100 truncate">
                    {user.name}
                  </div>
                  <div className="text-xs text-gray-500 dark:text-gray-400 truncate">
                    {user.email}
                  </div>

                  {/* Badges de rol y clearance */}
                  <div className="flex items-center space-x-2 mt-2">
                    <Badge
                      variant={getClearanceBadgeVariant(user.securityClearance)}
                      className="text-xs"
                    >
                      {user.securityClearance}
                    </Badge>
                    <Badge variant="outline" className="text-xs">
                      {user.role.replace("_", " ")}
                    </Badge>
                  </div>

                  {/* Información adicional */}
                  {user.embassy && (
                    <div className="flex items-center space-x-1 mt-1">
                      <Building className="h-3 w-3 text-gray-400" />
                      <span className="text-xs text-gray-500 dark:text-gray-400 truncate">
                        {user.embassy}
                      </span>
                    </div>
                  )}

                  {user.department && (
                    <div className="flex items-center space-x-1">
                      <Mail className="h-3 w-3 text-gray-400" />
                      <span className="text-xs text-gray-500 dark:text-gray-400 truncate">
                        {user.department}
                      </span>
                    </div>
                  )}
                </div>
              </div>

              {/* Información de sesión */}
              <div className="mt-3 text-xs text-gray-500 dark:text-gray-400">
                <div className="flex items-center space-x-1">
                  <Clock className="h-3 w-3" />
                  <span>Última conexión: {formatLastLogin(user.lastLoginAt)}</span>
                </div>

                {/* Advertencia de sesión próxima a expirar */}
                {nearExpiry && (
                  <div className="flex items-center space-x-1 mt-1 text-orange-600 dark:text-orange-400">
                    <AlertTriangle className="h-3 w-3" />
                    <span>Sesión expira pronto</span>
                  </div>
                )}
              </div>
            </div>

            {/* Opciones del menú */}
            <div className="py-2">
              <Link
                href="/profile"
                className="flex items-center space-x-2 px-4 py-2 text-sm hover:bg-gray-100 dark:hover:bg-gray-700"
                onClick={() => setIsOpen(false)}
              >
                <User className="h-4 w-4" />
                <span>Mi Perfil</span>
              </Link>

              <Link
                href="/settings"
                className="flex items-center space-x-2 px-4 py-2 text-sm hover:bg-gray-100 dark:hover:bg-gray-700"
                onClick={() => setIsOpen(false)}
              >
                <Settings className="h-4 w-4" />
                <span>Configuración</span>
              </Link>

              <Link
                href="/security"
                className="flex items-center space-x-2 px-4 py-2 text-sm hover:bg-gray-100 dark:hover:bg-gray-700"
                onClick={() => setIsOpen(false)}
              >
                <Shield className="h-4 w-4" />
                <span>Seguridad</span>
              </Link>

              <Link
                href="/change-password"
                className="flex items-center space-x-2 px-4 py-2 text-sm hover:bg-gray-100 dark:hover:bg-gray-700"
                onClick={() => setIsOpen(false)}
              >
                <Key className="h-4 w-4" />
                <span>Cambiar Contraseña</span>
              </Link>

              <hr className="my-2 border-gray-200 dark:border-gray-700" />

              <button
                className="flex items-center space-x-2 px-4 py-2 text-sm hover:bg-gray-100 dark:hover:bg-gray-700 w-full text-left text-red-600 dark:text-red-400"
                onClick={() => {
                  setIsOpen(false);
                  // Aquí iría la lógica de logout
                  console.log("Logout clicked");
                }}
              >
                <LogOut className="h-4 w-4" />
                <span>Cerrar Sesión</span>
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
}

export default UserNav;
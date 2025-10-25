/**
 * SIAME 2026v3 - Encabezado del Sitio
 * Componente de encabezado con navegación y información de usuario
 */

"use client"

import * as React from "react"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { MainNav } from "./main-nav"
import { UserNav } from "./user-nav"
import { SecurityClassification, DiplomaticRole } from "@/types"
import { cn } from "@/lib/utils"

// Iconos
import { Shield, Bell, Search, Menu } from "lucide-react"

interface SiteHeaderProps {
  user?: {
    id: string
    name: string
    email: string
    avatar?: string
    role: DiplomaticRole
    securityClearance: SecurityClassification
    embassy?: string
    department?: string
  }
  className?: string
}

// Logo de la Embajada del Perú en Japón
const EmbassyLogo = () => (
  <div className="flex items-center space-x-2">
    <div className="w-8 h-8 bg-red-600 rounded-full flex items-center justify-center">
      <Shield className="h-5 w-5 text-white" />
    </div>
    <div className="hidden md:block">
      <div className="text-sm font-bold text-foreground">Embajada del Perú</div>
      <div className="text-xs text-muted-foreground">Tokio, Japón</div>
    </div>
  </div>
);

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

// Función para obtener la descripción del rol
function getRoleDescription(role: DiplomaticRole): string {
  switch (role) {
    case DiplomaticRole.EMBAJADOR:
      return "Embajador";
    case DiplomaticRole.MINISTRO_CONSEJERO:
      return "Ministro Consejero";
    case DiplomaticRole.CONSEJERO:
      return "Consejero";
    case DiplomaticRole.PRIMER_SECRETARIO:
      return "Primer Secretario";
    case DiplomaticRole.SEGUNDO_SECRETARIO:
      return "Segundo Secretario";
    case DiplomaticRole.TERCER_SECRETARIO:
      return "Tercer Secretario";
    case DiplomaticRole.AGREGADO:
      return "Agregado";
    case DiplomaticRole.FUNCIONARIO_ADMINISTRATIVO:
      return "Funcionario Administrativo";
    case DiplomaticRole.CONSULTOR_EXTERNO:
      return "Consultor Externo";
    case DiplomaticRole.INVITADO:
      return "Invitado";
    default:
      return "Usuario";
  }
}

export function SiteHeader({ user, className }: SiteHeaderProps) {
  const [mobileMenuOpen, setMobileMenuOpen] = React.useState(false);

  return (
    <header className={cn("sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60", className)}>
      <div className="container flex h-16 items-center justify-between">
        {/* Logo y título */}
        <div className="flex items-center space-x-4">
          <Link href="/dashboard" className="flex items-center space-x-2">
            <EmbassyLogo />
          </Link>

          <div className="hidden lg:block">
            <div className="text-lg font-bold text-foreground">SIAME 2026v3</div>
            <div className="text-xs text-muted-foreground">Sistema Inteligente de Administración y Manejo de Expedientes</div>
          </div>
        </div>

        {/* Navegación principal - Desktop */}
        <div className="hidden md:flex flex-1 items-center justify-center px-6">
          <MainNav
            userRole={user?.role}
            securityClearance={user?.securityClearance}
          />
        </div>

        {/* Sección derecha */}
        <div className="flex items-center space-x-4">
          {/* Información de clearance del usuario */}
          {user && (
            <div className="hidden sm:flex items-center space-x-2">
              <Badge
                variant={getClearanceBadgeVariant(user.securityClearance)}
                className="text-xs"
              >
                {user.securityClearance}
              </Badge>
              <div className="text-xs text-muted-foreground">
                {getRoleDescription(user.role)}
              </div>
            </div>
          )}

          {/* Botón de búsqueda rápida */}
          <Button variant="ghost" size="icon" className="hidden md:flex">
            <Search className="h-4 w-4" />
            <span className="sr-only">Búsqueda rápida</span>
          </Button>

          {/* Notificaciones */}
          <Button variant="ghost" size="icon" className="relative">
            <Bell className="h-4 w-4" />
            <span className="sr-only">Notificaciones</span>
            {/* Indicador de notificaciones pendientes */}
            <div className="absolute -top-1 -right-1 h-3 w-3 bg-red-500 rounded-full text-xs text-white flex items-center justify-center">
              3
            </div>
          </Button>

          {/* Navegación del usuario */}
          {user ? (
            <UserNav user={user} />
          ) : (
            <div className="flex items-center space-x-2">
              <Button variant="ghost" size="sm" asChild>
                <Link href="/auth/login">Iniciar Sesión</Link>
              </Button>
              <Button size="sm" asChild>
                <Link href="/auth/register">Registrarse</Link>
              </Button>
            </div>
          )}

          {/* Menú móvil */}
          <Button
            variant="ghost"
            size="icon"
            className="md:hidden"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          >
            <Menu className="h-4 w-4" />
            <span className="sr-only">Menú</span>
          </Button>
        </div>
      </div>

      {/* Navegación móvil */}
      {mobileMenuOpen && (
        <div className="md:hidden border-t bg-background">
          <div className="container py-4">
            <MainNav
              userRole={user?.role}
              securityClearance={user?.securityClearance}
              className="flex-col items-start space-x-0 space-y-4"
            />

            {/* Información de usuario en móvil */}
            {user && (
              <div className="mt-4 pt-4 border-t">
                <div className="flex items-center space-x-2">
                  <Badge
                    variant={getClearanceBadgeVariant(user.securityClearance)}
                    className="text-xs"
                  >
                    {user.securityClearance}
                  </Badge>
                  <div className="text-sm font-medium">{user.name}</div>
                </div>
                <div className="text-xs text-muted-foreground mt-1">
                  {getRoleDescription(user.role)}
                  {user.embassy && ` - ${user.embassy}`}
                </div>
                {user.department && (
                  <div className="text-xs text-muted-foreground">
                    {user.department}
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Barra de estado de clasificación */}
      {user && user.securityClearance !== SecurityClassification.PUBLICO && (
        <div className={cn(
          "w-full py-1 text-center text-xs font-medium text-white",
          user.securityClearance === SecurityClassification.RESTRINGIDO && "bg-blue-500",
          user.securityClearance === SecurityClassification.CONFIDENCIAL && "bg-amber-500",
          user.securityClearance === SecurityClassification.SECRETO && "bg-red-500",
          user.securityClearance === SecurityClassification.ALTO_SECRETO && "bg-purple-600"
        )}>
          Sesión con Clearance {user.securityClearance} - {getRoleDescription(user.role)}
          {user.embassy && ` - ${user.embassy}`}
        </div>
      )}
    </header>
  );
}

export default SiteHeader;
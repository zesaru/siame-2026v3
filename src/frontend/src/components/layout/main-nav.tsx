/**
 * SIAME 2026v3 - Navegación Principal
 * Componente de navegación con diferentes niveles de acceso diplomático
 */

"use client"

import * as React from "react"
import Link from "next/link"
import { usePathname } from "next/navigation"
import { cn } from "@/lib/utils"
import { Badge } from "@/components/ui/badge"
import { SecurityClassification, DiplomaticRole, type NavItem } from "@/types"

// Iconos (usando Lucide React)
import {
  FileText,
  Upload,
  Search,
  Archive,
  Users,
  Shield,
  BarChart3,
  Settings,
  Home,
  Mail,
  Calendar,
  Clock,
  AlertTriangle,
  Eye,
  Lock,
  UserCheck,
  Building,
  Globe
} from "lucide-react"

interface MainNavProps {
  userRole?: DiplomaticRole
  securityClearance?: SecurityClassification
  className?: string
}

// Configuración de navegación basada en roles y niveles de seguridad
const navigationConfig: NavItem[] = [
  {
    title: "Inicio",
    href: "/dashboard",
    icon: "Home",
  },
  {
    title: "Documentos",
    href: "/documents",
    icon: "FileText",
    children: [
      {
        title: "Ver Documentos",
        href: "/documents/view",
        icon: "Eye",
      },
      {
        title: "Subir Documento",
        href: "/documents/upload",
        icon: "Upload",
        requiredClearance: SecurityClassification.RESTRINGIDO,
      },
      {
        title: "Buscar",
        href: "/documents/search",
        icon: "Search",
      },
      {
        title: "Clasificación",
        href: "/documents/classification",
        icon: "Lock",
        requiredClearance: SecurityClassification.CONFIDENCIAL,
      },
      {
        title: "Archivo",
        href: "/documents/archive",
        icon: "Archive",
        requiredRole: DiplomaticRole.TERCER_SECRETARIO,
      },
    ],
  },
  {
    title: "Comunicaciones",
    href: "/communications",
    icon: "Mail",
    children: [
      {
        title: "Valija Diplomática",
        href: "/communications/diplomatic-bag",
        icon: "Mail",
        requiredRole: DiplomaticRole.SEGUNDO_SECRETARIO,
      },
      {
        title: "Despachos",
        href: "/communications/dispatches",
        icon: "FileText",
        requiredClearance: SecurityClassification.CONFIDENCIAL,
      },
      {
        title: "Notas Diplomáticas",
        href: "/communications/diplomatic-notes",
        icon: "FileText",
        requiredRole: DiplomaticRole.PRIMER_SECRETARIO,
      },
    ],
  },
  {
    title: "Workflows",
    href: "/workflows",
    icon: "Clock",
    requiredRole: DiplomaticRole.CONSEJERO,
    children: [
      {
        title: "Aprobaciones Pendientes",
        href: "/workflows/approvals",
        icon: "UserCheck",
      },
      {
        title: "Estado de Procesos",
        href: "/workflows/status",
        icon: "BarChart3",
      },
    ],
  },
  {
    title: "Embajadas",
    href: "/embassies",
    icon: "Building",
    requiredRole: DiplomaticRole.CONSEJERO,
    children: [
      {
        title: "Directorio",
        href: "/embassies/directory",
        icon: "Globe",
      },
      {
        title: "Comunicaciones",
        href: "/embassies/communications",
        icon: "Mail",
      },
    ],
  },
  {
    title: "Administración",
    href: "/admin",
    icon: "Settings",
    requiredRole: DiplomaticRole.MINISTRO_CONSEJERO,
    children: [
      {
        title: "Usuarios",
        href: "/admin/users",
        icon: "Users",
        requiredRole: DiplomaticRole.MINISTRO_CONSEJERO,
      },
      {
        title: "Roles y Permisos",
        href: "/admin/roles",
        icon: "Shield",
        requiredRole: DiplomaticRole.EMBAJADOR,
      },
      {
        title: "Auditoría",
        href: "/admin/audit",
        icon: "Eye",
        requiredClearance: SecurityClassification.SECRETO,
      },
      {
        title: "Configuración",
        href: "/admin/settings",
        icon: "Settings",
        requiredRole: DiplomaticRole.EMBAJADOR,
      },
    ],
  },
  {
    title: "Reportes",
    href: "/reports",
    icon: "BarChart3",
    requiredRole: DiplomaticRole.CONSEJERO,
    children: [
      {
        title: "Analytics",
        href: "/reports/analytics",
        icon: "BarChart3",
      },
      {
        title: "Seguridad",
        href: "/reports/security",
        icon: "Shield",
        requiredClearance: SecurityClassification.SECRETO,
      },
      {
        title: "Actividad",
        href: "/reports/activity",
        icon: "Clock",
        requiredClearance: SecurityClassification.CONFIDENCIAL,
      },
    ],
  },
];

// Mapeo de iconos
const iconMap = {
  Home,
  FileText,
  Upload,
  Search,
  Archive,
  Users,
  Shield,
  BarChart3,
  Settings,
  Mail,
  Calendar,
  Clock,
  AlertTriangle,
  Eye,
  Lock,
  UserCheck,
  Building,
  Globe,
};

// Función para verificar si el usuario tiene acceso a un elemento de navegación
function hasAccess(
  item: NavItem,
  userRole?: DiplomaticRole,
  securityClearance?: SecurityClassification
): boolean {
  // Verificar rol requerido
  if (item.requiredRole && userRole) {
    const roleHierarchy = Object.values(DiplomaticRole);
    const userRoleIndex = roleHierarchy.indexOf(userRole);
    const requiredRoleIndex = roleHierarchy.indexOf(item.requiredRole);

    if (userRoleIndex > requiredRoleIndex) {
      return false;
    }
  }

  // Verificar clearance de seguridad requerido
  if (item.requiredClearance && securityClearance) {
    const clearanceHierarchy = Object.values(SecurityClassification);
    const userClearanceIndex = clearanceHierarchy.indexOf(securityClearance);
    const requiredClearanceIndex = clearanceHierarchy.indexOf(item.requiredClearance);

    if (userClearanceIndex < requiredClearanceIndex) {
      return false;
    }
  }

  return true;
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

export function MainNav({
  userRole = DiplomaticRole.INVITADO,
  securityClearance = SecurityClassification.PUBLICO,
  className
}: MainNavProps) {
  const pathname = usePathname();

  // Filtrar elementos de navegación basado en permisos
  const accessibleNavItems = navigationConfig.filter(item =>
    hasAccess(item, userRole, securityClearance)
  ).map(item => ({
    ...item,
    children: item.children?.filter(child =>
      hasAccess(child, userRole, securityClearance)
    )
  }));

  return (
    <nav className={cn("flex items-center space-x-4 lg:space-x-6", className)}>
      {accessibleNavItems.map((item) => {
        const Icon = iconMap[item.icon as keyof typeof iconMap];
        const isActive = pathname === item.href || pathname.startsWith(item.href + "/");

        return (
          <div key={item.href} className="relative">
            <Link
              href={item.href}
              className={cn(
                "flex items-center space-x-2 text-sm font-medium transition-colors hover:text-primary",
                isActive
                  ? "text-foreground"
                  : "text-muted-foreground"
              )}
            >
              {Icon && <Icon className="h-4 w-4" />}
              <span>{item.title}</span>

              {/* Badge de clearance requerido */}
              {item.requiredClearance && (
                <Badge
                  variant={getClearanceBadgeVariant(item.requiredClearance)}
                  className="ml-2 text-xs"
                >
                  {item.requiredClearance}
                </Badge>
              )}

              {/* Indicador de rol requerido */}
              {item.requiredRole && (
                <Shield className="h-3 w-3 ml-1 text-amber-500" />
              )}
            </Link>

            {/* Submenú - se puede expandir en versiones futuras */}
            {item.children && item.children.length > 0 && isActive && (
              <div className="absolute top-full left-0 mt-2 w-48 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-md shadow-lg z-50">
                {item.children.map((child) => {
                  const ChildIcon = iconMap[child.icon as keyof typeof iconMap];

                  return (
                    <Link
                      key={child.href}
                      href={child.href}
                      className="flex items-center space-x-2 px-3 py-2 text-sm hover:bg-gray-100 dark:hover:bg-gray-700"
                    >
                      {ChildIcon && <ChildIcon className="h-4 w-4" />}
                      <span>{child.title}</span>

                      {child.requiredClearance && (
                        <Badge
                          variant={getClearanceBadgeVariant(child.requiredClearance)}
                          className="ml-auto text-xs"
                        >
                          {child.requiredClearance}
                        </Badge>
                      )}
                    </Link>
                  );
                })}
              </div>
            )}
          </div>
        );
      })}
    </nav>
  );
}

export default MainNav;
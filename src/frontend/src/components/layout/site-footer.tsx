/**
 * SIAME 2026v3 - Footer del Sitio
 * Componente de footer con información institucional y enlaces
 */

import * as React from "react"
import Link from "next/link"
import { Shield, Mail, Phone, Globe, ExternalLink } from "lucide-react"

export function SiteFooter() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="border-t bg-background">
      <div className="container py-8 md:py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Información institucional */}
          <div className="space-y-4">
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
                <Shield className="h-5 w-5 text-white" />
              </div>
              <div>
                <div className="font-bold">MAEUEC</div>
                <div className="text-xs text-muted-foreground">Asuntos Exteriores</div>
              </div>
            </div>
            <p className="text-sm text-muted-foreground">
              Sistema Inteligente de Administración y Manejo de Expedientes para la gestión
              segura de documentos diplomáticos.
            </p>
            <div className="space-y-1">
              <div className="flex items-center space-x-2 text-sm text-muted-foreground">
                <Mail className="h-4 w-4" />
                <span>siame@maeuec.es</span>
              </div>
              <div className="flex items-center space-x-2 text-sm text-muted-foreground">
                <Phone className="h-4 w-4" />
                <span>+34 91 379 97 00</span>
              </div>
              <div className="flex items-center space-x-2 text-sm text-muted-foreground">
                <Globe className="h-4 w-4" />
                <span>Madrid, España</span>
              </div>
            </div>
          </div>

          {/* Enlaces rápidos */}
          <div className="space-y-4">
            <h4 className="text-sm font-medium">Enlaces Rápidos</h4>
            <nav className="space-y-2">
              <Link href="/dashboard" className="block text-sm text-muted-foreground hover:text-foreground">
                Dashboard
              </Link>
              <Link href="/documents/upload" className="block text-sm text-muted-foreground hover:text-foreground">
                Subir Documento
              </Link>
              <Link href="/documents/search" className="block text-sm text-muted-foreground hover:text-foreground">
                Búsqueda
              </Link>
              <Link href="/communications" className="block text-sm text-muted-foreground hover:text-foreground">
                Comunicaciones
              </Link>
              <Link href="/reports" className="block text-sm text-muted-foreground hover:text-foreground">
                Reportes
              </Link>
            </nav>
          </div>

          {/* Recursos */}
          <div className="space-y-4">
            <h4 className="text-sm font-medium">Recursos</h4>
            <nav className="space-y-2">
              <Link href="/help" className="block text-sm text-muted-foreground hover:text-foreground">
                Centro de Ayuda
              </Link>
              <Link href="/documentation" className="block text-sm text-muted-foreground hover:text-foreground">
                Documentación
              </Link>
              <Link href="/training" className="block text-sm text-muted-foreground hover:text-foreground">
                Capacitación
              </Link>
              <Link href="/support" className="block text-sm text-muted-foreground hover:text-foreground">
                Soporte Técnico
              </Link>
              <Link href="/security-guidelines" className="block text-sm text-muted-foreground hover:text-foreground">
                Directrices de Seguridad
              </Link>
            </nav>
          </div>

          {/* Enlaces institucionales */}
          <div className="space-y-4">
            <h4 className="text-sm font-medium">Institucional</h4>
            <nav className="space-y-2">
              <a
                href="https://www.exteriores.gob.es"
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center space-x-1 text-sm text-muted-foreground hover:text-foreground"
              >
                <span>Portal Principal</span>
                <ExternalLink className="h-3 w-3" />
              </a>
              <a
                href="https://sede.maeuec.gob.es"
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center space-x-1 text-sm text-muted-foreground hover:text-foreground"
              >
                <span>Sede Electrónica</span>
                <ExternalLink className="h-3 w-3" />
              </a>
              <Link href="/privacy" className="block text-sm text-muted-foreground hover:text-foreground">
                Política de Privacidad
              </Link>
              <Link href="/terms" className="block text-sm text-muted-foreground hover:text-foreground">
                Términos de Uso
              </Link>
              <Link href="/accessibility" className="block text-sm text-muted-foreground hover:text-foreground">
                Accesibilidad
              </Link>
            </nav>
          </div>
        </div>

        {/* Separador */}
        <hr className="my-8 border-border" />

        {/* Información de copyright y versión */}
        <div className="flex flex-col md:flex-row justify-between items-center space-y-4 md:space-y-0">
          <div className="text-sm text-muted-foreground">
            © {currentYear} Ministerio de Asuntos Exteriores, Unión Europea y Cooperación.
            Todos los derechos reservados.
          </div>

          <div className="flex items-center space-x-4 text-sm text-muted-foreground">
            <span>SIAME 2026v3</span>
            <span>•</span>
            <span>Versión 3.0.0</span>
            <span>•</span>
            <span>Entorno: Desarrollo</span>
          </div>
        </div>

        {/* Aviso de clasificación */}
        <div className="mt-4 p-3 bg-blue-50 dark:bg-blue-950 border border-blue-200 dark:border-blue-800 rounded-md">
          <div className="flex items-start space-x-2">
            <Shield className="h-4 w-4 text-blue-600 dark:text-blue-400 mt-0.5 flex-shrink-0" />
            <div className="text-xs text-blue-800 dark:text-blue-200">
              <strong>AVISO IMPORTANTE:</strong> Este sistema maneja información clasificada del Estado.
              El acceso y uso están restringidos a personal autorizado del Ministerio de Asuntos Exteriores.
              Todas las actividades están monitoreadas y registradas conforme a la normativa de seguridad nacional.
            </div>
          </div>
        </div>

        {/* Indicadores de seguridad y cumplimiento */}
        <div className="flex flex-wrap items-center justify-center gap-4 mt-6 text-xs text-muted-foreground">
          <div className="flex items-center space-x-1">
            <Shield className="h-3 w-3" />
            <span>ENS Alto</span>
          </div>
          <span>•</span>
          <div className="flex items-center space-x-1">
            <Shield className="h-3 w-3" />
            <span>ISO 27001</span>
          </div>
          <span>•</span>
          <div className="flex items-center space-x-1">
            <Shield className="h-3 w-3" />
            <span>GDPR Compatible</span>
          </div>
          <span>•</span>
          <div className="flex items-center space-x-1">
            <Shield className="h-3 w-3" />
            <span>CCN-CERT</span>
          </div>
        </div>
      </div>
    </footer>
  );
}

export default SiteFooter;
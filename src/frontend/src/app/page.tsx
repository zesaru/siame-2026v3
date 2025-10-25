/**
 * SIAME 2026v3 - Página Principal
 * Landing page del sistema diplomático
 */

import Link from "next/link"
import { Layout } from "@/components/layout/layout"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { SecurityClassification, DiplomaticRole } from "@/types"

// Datos de ejemplo para demostrar el layout
const mockUser = {
  id: "1",
  name: "María Elena Castillo Ayala",
  email: "mcastillo@embaperu.jp",
  avatar: "",
  role: DiplomaticRole.CONSEJERO,
  securityClearance: SecurityClassification.CONFIDENCIAL,
  embassy: "Embajada del Perú en Japón",
  department: "Asuntos Políticos y Económicos",
  lastLoginAt: new Date(Date.now() - 2 * 60 * 60 * 1000), // Hace 2 horas
  sessionExpiresAt: new Date(Date.now() + 30 * 60 * 1000), // Expira en 30 minutos
};

export default function Home() {
  return (
    <Layout user={mockUser}>
      <div className="container mx-auto px-4 py-12">
        {/* Hero Section */}
        <div className="text-center space-y-6 mb-16">
          <div className="space-y-2">
            <h1 className="text-4xl font-bold tracking-tight text-gray-900 dark:text-gray-100 sm:text-6xl">
              SIAME 2026v3
            </h1>
            <p className="text-xl text-gray-600 dark:text-gray-400">
              Sistema Inteligente de Administración y Manejo de Expedientes
            </p>
            <p className="text-sm text-gray-500 dark:text-gray-500">
              Ministerio de Asuntos Exteriores, Unión Europea y Cooperación
            </p>
          </div>

          <div className="flex justify-center">
            <Badge variant="confidencial" className="text-sm px-4 py-2">
              Sistema Clasificado - Acceso Restringido
            </Badge>
          </div>
        </div>

        {/* Características principales */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-16">
          <div className="text-center space-y-4">
            <div className="w-12 h-12 bg-blue-600 rounded-lg flex items-center justify-center mx-auto">
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <h3 className="text-lg font-semibold">Gestión de Documentos</h3>
            <p className="text-gray-600 dark:text-gray-400">
              Procesamiento inteligente de hojas de remisión, guías de valija y documentos diplomáticos
            </p>
          </div>

          <div className="text-center space-y-4">
            <div className="w-12 h-12 bg-green-600 rounded-lg flex items-center justify-center mx-auto">
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h3 className="text-lg font-semibold">Clasificación Automática</h3>
            <p className="text-gray-600 dark:text-gray-400">
              IA avanzada para clasificación automática con Azure Form Recognizer
            </p>
          </div>

          <div className="text-center space-y-4">
            <div className="w-12 h-12 bg-red-600 rounded-lg flex items-center justify-center mx-auto">
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
              </svg>
            </div>
            <h3 className="text-lg font-semibold">Seguridad Avanzada</h3>
            <p className="text-gray-600 dark:text-gray-400">
              5 niveles de clasificación con Row Level Security y auditoría completa
            </p>
          </div>
        </div>

        {/* Niveles de clasificación soportados */}
        <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-8 mb-16">
          <h2 className="text-2xl font-bold text-center mb-8">Niveles de Clasificación Soportados</h2>

          <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
            <div className="text-center space-y-2">
              <Badge variant="publico" className="w-full py-2">PÚBLICO</Badge>
              <p className="text-xs text-gray-500">Acceso general</p>
            </div>
            <div className="text-center space-y-2">
              <Badge variant="restringido" className="w-full py-2">RESTRINGIDO</Badge>
              <p className="text-xs text-gray-500">Personal autorizado</p>
            </div>
            <div className="text-center space-y-2">
              <Badge variant="confidencial" className="w-full py-2">CONFIDENCIAL</Badge>
              <p className="text-xs text-gray-500">Información sensible</p>
            </div>
            <div className="text-center space-y-2">
              <Badge variant="secreto" className="w-full py-2">SECRETO</Badge>
              <p className="text-xs text-gray-500">Altamente clasificado</p>
            </div>
            <div className="text-center space-y-2">
              <Badge variant="alto_secreto" className="w-full py-2">ALTO SECRETO</Badge>
              <p className="text-xs text-gray-500">Máxima seguridad</p>
            </div>
          </div>
        </div>

        {/* Acciones rápidas */}
        <div className="text-center space-y-8">
          <h2 className="text-2xl font-bold">Acceso al Sistema</h2>

          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button asChild size="lg">
              <Link href="/dashboard">Ir al Dashboard</Link>
            </Button>
            <Button variant="outline" asChild size="lg">
              <Link href="/documents/upload">Subir Documento</Link>
            </Button>
            <Button variant="outline" asChild size="lg">
              <Link href="/documents/search">Búsqueda Avanzada</Link>
            </Button>
          </div>

          <p className="text-sm text-gray-500 dark:text-gray-500 max-w-2xl mx-auto">
            Conectado como: <strong>{mockUser.name}</strong> ({mockUser.role})
            con clearance <strong>{mockUser.securityClearance}</strong>
            <br />
            {mockUser.embassy} - {mockUser.department}
          </p>
        </div>

        {/* Información del sistema */}
        <div className="mt-16 pt-8 border-t border-gray-200 dark:border-gray-700">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 text-sm text-gray-500 dark:text-gray-500">
            <div>
              <h4 className="font-medium text-gray-900 dark:text-gray-100 mb-2">Información del Sistema</h4>
              <ul className="space-y-1">
                <li>Versión: 3.0.0</li>
                <li>Entorno: Desarrollo</li>
                <li>Base de datos: PostgreSQL + Prisma</li>
                <li>Cloud: Microsoft Azure</li>
              </ul>
            </div>
            <div>
              <h4 className="font-medium text-gray-900 dark:text-gray-100 mb-2">Cumplimiento</h4>
              <ul className="space-y-1">
                <li>✅ ENS Alto</li>
                <li>✅ ISO 27001</li>
                <li>✅ GDPR</li>
                <li>✅ CCN-CERT</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
}

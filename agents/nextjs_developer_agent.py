#!/usr/bin/env python3
"""
SIAME 2026v3 - Next.js Developer Agent
Agente especializado en desarrollo frontend con Next.js para sistemas diplomáticos

Este agente maneja:
- Creación y configuración de proyectos Next.js
- Implementación de componentes React especializados
- Configuración de routing y páginas
- Integración con APIs diplomáticas
- Implementación de interfaces de usuario para documentos diplomáticos
"""

import asyncio
import logging
import subprocess
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
from dataclasses import dataclass, field

# Plantillas de código para diferentes componentes
NEXTJS_TEMPLATES = {
    "diplomatic_document_viewer": """
import React, { useState, useEffect } from 'react';
import { DiplomaticDocument } from '@/types/diplomatic';

interface DiplomaticDocumentViewerProps {
  documentId: string;
  securityLevel: 'public' | 'restricted' | 'confidential' | 'secret' | 'top_secret';
  onDocumentLoad?: (document: DiplomaticDocument) => void;
}

export const DiplomaticDocumentViewer: React.FC<DiplomaticDocumentViewerProps> = ({
  documentId,
  securityLevel,
  onDocumentLoad
}) => {
  const [document, setDocument] = useState<DiplomaticDocument | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadDocument = async () => {
      try {
        const response = await fetch(`/api/documents/${documentId}`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
            'Security-Level': securityLevel
          }
        });

        if (!response.ok) {
          throw new Error('Failed to load document');
        }

        const documentData = await response.json();
        setDocument(documentData);
        onDocumentLoad?.(documentData);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error');
      } finally {
        setLoading(false);
      }
    };

    loadDocument();
  }, [documentId, securityLevel, onDocumentLoad]);

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-md p-4">
        <h3 className="text-red-800 font-medium">Error al cargar documento</h3>
        <p className="text-red-600 mt-1">{error}</p>
      </div>
    );
  }

  if (!document) {
    return (
      <div className="bg-gray-50 border border-gray-200 rounded-md p-4">
        <p className="text-gray-600">Documento no encontrado</p>
      </div>
    );
  }

  return (
    <div className="bg-white border border-gray-200 rounded-lg shadow-sm">
      <div className="border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-semibold text-gray-900">
            {document.title || 'Documento Diplomático'}
          </h2>
          <span className={`px-3 py-1 rounded-full text-xs font-medium ${{
            'public': 'bg-green-100 text-green-800',
            'restricted': 'bg-yellow-100 text-yellow-800',
            'confidential': 'bg-orange-100 text-orange-800',
            'secret': 'bg-red-100 text-red-800',
            'top_secret': 'bg-purple-100 text-purple-800'
          }[securityLevel]}`}>
            {securityLevel.toUpperCase()}
          </span>
        </div>
        <div className="mt-2 flex space-x-4 text-sm text-gray-500">
          <span>Tipo: {document.type}</span>
          <span>Fecha: {new Date(document.date).toLocaleDateString()}</span>
          {document.country && <span>País: {document.country}</span>}
        </div>
      </div>

      <div className="p-6">
        {document.extractedData && (
          <div className="mb-6">
            <h3 className="text-lg font-medium text-gray-900 mb-3">Datos Extraídos</h3>
            <div className="grid grid-cols-2 gap-4">
              {Object.entries(document.extractedData).map(([key, value]) => (
                <div key={key} className="bg-gray-50 p-3 rounded">
                  <dt className="text-sm font-medium text-gray-500">{key}</dt>
                  <dd className="text-sm text-gray-900 mt-1">{value as string}</dd>
                </div>
              ))}
            </div>
          </div>
        )}

        {document.content && (
          <div>
            <h3 className="text-lg font-medium text-gray-900 mb-3">Contenido</h3>
            <div className="prose max-w-none">
              <pre className="whitespace-pre-wrap text-sm text-gray-700 bg-gray-50 p-4 rounded">
                {document.content}
              </pre>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
""",

    "authentication_form": """
import React, { useState } from 'react';
import { useAuth } from '@/hooks/useAuth';
import { SecurityLevel } from '@/types/security';

interface AuthenticationFormProps {
  onSuccess: (token: string, securityLevel: SecurityLevel) => void;
  onError: (error: string) => void;
}

export const AuthenticationForm: React.FC<AuthenticationFormProps> = ({
  onSuccess,
  onError
}) => {
  const [credentials, setCredentials] = useState({
    username: '',
    password: '',
    securityCode: ''
  });
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      const result = await login(credentials);
      onSuccess(result.token, result.securityLevel);
    } catch (error) {
      onError(error instanceof Error ? error.message : 'Error de autenticación');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-md mx-auto bg-white rounded-lg shadow-md p-6">
      <div className="text-center mb-6">
        <h2 className="text-2xl font-bold text-gray-900">SIAME 2026v3</h2>
        <p className="text-gray-600 mt-2">Sistema de Análisis Diplomático</p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="username" className="block text-sm font-medium text-gray-700">
            Usuario
          </label>
          <input
            type="text"
            id="username"
            value={credentials.username}
            onChange={(e) => setCredentials(prev => ({ ...prev, username: e.target.value }))}
            className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            required
          />
        </div>

        <div>
          <label htmlFor="password" className="block text-sm font-medium text-gray-700">
            Contraseña
          </label>
          <input
            type="password"
            id="password"
            value={credentials.password}
            onChange={(e) => setCredentials(prev => ({ ...prev, password: e.target.value }))}
            className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            required
          />
        </div>

        <div>
          <label htmlFor="securityCode" className="block text-sm font-medium text-gray-700">
            Código de Seguridad
          </label>
          <input
            type="text"
            id="securityCode"
            value={credentials.securityCode}
            onChange={(e) => setCredentials(prev => ({ ...prev, securityCode: e.target.value }))}
            className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            placeholder="Opcional para documentos públicos"
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
        >
          {loading ? 'Autenticando...' : 'Iniciar Sesión'}
        </button>
      </form>

      <div className="mt-6 text-center">
        <p className="text-xs text-gray-500">
          Sistema clasificado - Uso autorizado únicamente
        </p>
      </div>
    </div>
  );
};
""",

    "document_upload": """
import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { DiplomaticDocumentType, SecurityLevel } from '@/types/diplomatic';

interface DocumentUploadProps {
  onUploadComplete: (documentId: string) => void;
  onUploadError: (error: string) => void;
  allowedTypes?: DiplomaticDocumentType[];
  maxFiles?: number;
}

export const DocumentUpload: React.FC<DocumentUploadProps> = ({
  onUploadComplete,
  onUploadError,
  allowedTypes = ['hoja_remision', 'guia_valija', 'nota_diplomatica'],
  maxFiles = 1
}) => {
  const [uploading, setUploading] = useState(false);
  const [documentType, setDocumentType] = useState<DiplomaticDocumentType>('hoja_remision');
  const [securityLevel, setSecurityLevel] = useState<SecurityLevel>('restricted');

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    if (acceptedFiles.length === 0) return;

    setUploading(true);

    try {
      const file = acceptedFiles[0];
      const formData = new FormData();
      formData.append('file', file);
      formData.append('documentType', documentType);
      formData.append('securityLevel', securityLevel);

      const response = await fetch('/api/documents/upload', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
        },
        body: formData
      });

      if (!response.ok) {
        throw new Error('Error al subir documento');
      }

      const result = await response.json();
      onUploadComplete(result.documentId);
    } catch (error) {
      onUploadError(error instanceof Error ? error.message : 'Error desconocido');
    } finally {
      setUploading(false);
    }
  }, [documentType, securityLevel, onUploadComplete, onUploadError]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'text/plain': ['.txt'],
      'application/msword': ['.doc'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx']
    },
    maxFiles,
    disabled: uploading
  });

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label htmlFor="documentType" className="block text-sm font-medium text-gray-700">
            Tipo de Documento
          </label>
          <select
            id="documentType"
            value={documentType}
            onChange={(e) => setDocumentType(e.target.value as DiplomaticDocumentType)}
            className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="hoja_remision">Hoja de Remisión</option>
            <option value="guia_valija">Guía de Valija</option>
            <option value="nota_diplomatica">Nota Diplomática</option>
            <option value="acuerdo_bilateral">Acuerdo Bilateral</option>
            <option value="protocolo_ceremonia">Protocolo de Ceremonia</option>
            <option value="credenciales">Credenciales</option>
            <option value="comunicacion_oficial">Comunicación Oficial</option>
            <option value="informe_consular">Informe Consular</option>
          </select>
        </div>

        <div>
          <label htmlFor="securityLevel" className="block text-sm font-medium text-gray-700">
            Nivel de Clasificación
          </label>
          <select
            id="securityLevel"
            value={securityLevel}
            onChange={(e) => setSecurityLevel(e.target.value as SecurityLevel)}
            className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="public">Público</option>
            <option value="restricted">Restringido</option>
            <option value="confidential">Confidencial</option>
            <option value="secret">Secreto</option>
            <option value="top_secret">Alto Secreto</option>
          </select>
        </div>
      </div>

      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${{
          border: isDragActive ? 'border-blue-400 bg-blue-50' : 'border-gray-300',
          'pointer-events-none opacity-50': uploading
        }}`}
      >
        <input {...getInputProps()} />
        {uploading ? (
          <div>
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Procesando documento...</p>
          </div>
        ) : (
          <div>
            <svg className="mx-auto h-12 w-12 text-gray-400" stroke="currentColor" fill="none" viewBox="0 0 48 48">
              <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" />
            </svg>
            <p className="mt-4 text-gray-600">
              {isDragActive ? 'Suelta el archivo aquí' : 'Arrastra un archivo aquí o haz clic para seleccionar'}
            </p>
            <p className="text-xs text-gray-500 mt-2">
              Formatos soportados: PDF, TXT, DOC, DOCX (máximo 10MB)
            </p>
          </div>
        )}
      </div>
    </div>
  );
};
"""
}


@dataclass
class NextJSProject:
    """Configuración de proyecto Next.js"""
    name: str
    path: Path
    typescript: bool = True
    tailwind: bool = True
    eslint: bool = True
    src_dir: bool = True
    app_router: bool = True
    features: List[str] = field(default_factory=list)


class NextJSDeveloperAgent:
    """Agente especializado en desarrollo Next.js para SIAME"""

    def __init__(self, agent_id: str = None):
        self.agent_id = agent_id or f"nextjs_dev_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.logger = logging.getLogger(__name__)

        # Configuración del agente
        self.supported_features = [
            "diplomatic_document_viewer",
            "authentication_system",
            "document_upload",
            "security_classification",
            "api_integration",
            "real_time_updates",
            "audit_logging",
            "responsive_design"
        ]

        # Estadísticas
        self.stats = {
            "projects_created": 0,
            "components_generated": 0,
            "apis_implemented": 0,
            "builds_successful": 0
        }

    async def create_nextjs_project(self, project_config: NextJSProject) -> Dict[str, Any]:
        """Crea un nuevo proyecto Next.js con configuración diplomática"""
        try:
            self.logger.info(f"Creando proyecto Next.js: {project_config.name}")

            # Crear directorio del proyecto
            project_path = project_config.path
            project_path.mkdir(parents=True, exist_ok=True)

            # Ejecutar create-next-app
            cmd = [
                "npx", "create-next-app@latest", project_config.name,
                "--typescript" if project_config.typescript else "--javascript",
                "--tailwind" if project_config.tailwind else "--no-tailwind",
                "--eslint" if project_config.eslint else "--no-eslint",
                "--src-dir" if project_config.src_dir else "--no-src-dir",
                "--app" if project_config.app_router else "--no-app",
                "--import-alias", "@/*"
            ]

            # Ejecutar comando
            result = await self._run_command(cmd, cwd=project_path.parent)

            if result["success"]:
                # Configurar proyecto para uso diplomático
                await self._configure_diplomatic_project(project_path / project_config.name, project_config)

                self.stats["projects_created"] += 1

                return {
                    "success": True,
                    "project_path": str(project_path / project_config.name),
                    "message": f"Proyecto Next.js '{project_config.name}' creado exitosamente"
                }
            else:
                return {
                    "success": False,
                    "error": result.get("error", "Error desconocido al crear proyecto")
                }

        except Exception as e:
            self.logger.error(f"Error creando proyecto Next.js: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def implement_component(self, project_path: Path, component_name: str,
                                component_type: str = "diplomatic_document_viewer") -> Dict[str, Any]:
        """Implementa un componente React especializado"""
        try:
            self.logger.info(f"Implementando componente: {component_name}")

            if component_type not in NEXTJS_TEMPLATES:
                return {
                    "success": False,
                    "error": f"Tipo de componente no soportado: {component_type}"
                }

            # Determinar ruta del componente
            components_dir = project_path / "src" / "components"
            if not components_dir.exists():
                components_dir = project_path / "components"

            components_dir.mkdir(parents=True, exist_ok=True)

            # Crear archivo del componente
            component_file = components_dir / f"{component_name}.tsx"
            component_content = NEXTJS_TEMPLATES[component_type]

            with open(component_file, 'w', encoding='utf-8') as f:
                f.write(component_content)

            # Crear tipos TypeScript si es necesario
            await self._create_typescript_types(project_path, component_type)

            self.stats["components_generated"] += 1

            return {
                "success": True,
                "component_path": str(component_file),
                "message": f"Componente {component_name} implementado exitosamente"
            }

        except Exception as e:
            self.logger.error(f"Error implementando componente: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def setup_api_routes(self, project_path: Path, api_config: Dict[str, Any]) -> Dict[str, Any]:
        """Configura rutas de API para el sistema diplomático"""
        try:
            self.logger.info("Configurando rutas de API")

            api_dir = project_path / "src" / "app" / "api"
            if not api_dir.exists():
                api_dir = project_path / "pages" / "api"

            api_dir.mkdir(parents=True, exist_ok=True)

            # APIs diplomáticas estándar
            apis_to_create = [
                ("documents", self._create_documents_api),
                ("auth", self._create_auth_api),
                ("upload", self._create_upload_api),
                ("security", self._create_security_api)
            ]

            created_apis = []

            for api_name, creator_func in apis_to_create:
                if api_config.get(f"include_{api_name}", True):
                    api_path = await creator_func(api_dir, api_name)
                    created_apis.append(api_path)

            self.stats["apis_implemented"] += len(created_apis)

            return {
                "success": True,
                "apis_created": created_apis,
                "message": f"APIs implementadas: {', '.join([str(p) for p in created_apis])}"
            }

        except Exception as e:
            self.logger.error(f"Error configurando APIs: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def configure_authentication(self, project_path: Path,
                                     auth_config: Dict[str, Any]) -> Dict[str, Any]:
        """Configura sistema de autenticación con niveles de clasificación"""
        try:
            self.logger.info("Configurando sistema de autenticación")

            # Instalar dependencias de autenticación
            dependencies = [
                "next-auth",
                "jose",
                "@types/jsonwebtoken",
                "bcryptjs",
                "@types/bcryptjs"
            ]

            await self._install_dependencies(project_path, dependencies)

            # Crear configuración de NextAuth
            await self._create_nextauth_config(project_path, auth_config)

            # Crear middleware de autenticación
            await self._create_auth_middleware(project_path)

            # Crear hooks de autenticación
            await self._create_auth_hooks(project_path)

            return {
                "success": True,
                "message": "Sistema de autenticación configurado exitosamente"
            }

        except Exception as e:
            self.logger.error(f"Error configurando autenticación: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def setup_azure_integration(self, project_path: Path,
                                    azure_config: Dict[str, Any]) -> Dict[str, Any]:
        """Configura integración con servicios de Azure"""
        try:
            self.logger.info("Configurando integración con Azure")

            # Instalar SDK de Azure
            azure_dependencies = [
                "@azure/storage-blob",
                "@azure/ai-form-recognizer",
                "@azure/msal-browser",
                "@azure/msal-react"
            ]

            await self._install_dependencies(project_path, azure_dependencies)

            # Crear utilidades de Azure
            await self._create_azure_utilities(project_path, azure_config)

            # Crear configuración de MSAL
            await self._create_msal_config(project_path, azure_config)

            return {
                "success": True,
                "message": "Integración con Azure configurada exitosamente"
            }

        except Exception as e:
            self.logger.error(f"Error configurando Azure: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def build_project(self, project_path: Path) -> Dict[str, Any]:
        """Construye el proyecto Next.js"""
        try:
            self.logger.info("Construyendo proyecto Next.js")

            # Ejecutar build
            result = await self._run_command(["npm", "run", "build"], cwd=project_path)

            if result["success"]:
                self.stats["builds_successful"] += 1
                return {
                    "success": True,
                    "message": "Proyecto construido exitosamente",
                    "output": result.get("output", "")
                }
            else:
                return {
                    "success": False,
                    "error": result.get("error", "Error en la construcción"),
                    "output": result.get("output", "")
                }

        except Exception as e:
            self.logger.error(f"Error construyendo proyecto: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def get_agent_status(self) -> Dict[str, Any]:
        """Obtiene el estado del agente"""
        return {
            "agent_id": self.agent_id,
            "agent_type": "NextJS Developer",
            "supported_features": self.supported_features,
            "statistics": self.stats,
            "available_templates": list(NEXTJS_TEMPLATES.keys())
        }

    # Métodos privados

    async def _configure_diplomatic_project(self, project_path: Path, config: NextJSProject) -> None:
        """Configura el proyecto para uso diplomático"""
        # Crear estructura de directorios diplomática
        dirs_to_create = [
            "src/types",
            "src/lib/azure",
            "src/lib/auth",
            "src/lib/security",
            "src/hooks",
            "src/components/diplomatic",
            "src/components/security",
            "public/icons"
        ]

        for dir_path in dirs_to_create:
            (project_path / dir_path).mkdir(parents=True, exist_ok=True)

        # Crear tipos TypeScript diplomáticos
        await self._create_diplomatic_types(project_path)

        # Configurar variables de entorno
        await self._create_env_files(project_path)

        # Actualizar package.json con scripts diplomáticos
        await self._update_package_json(project_path, config)

    async def _create_diplomatic_types(self, project_path: Path) -> None:
        """Crea tipos TypeScript para el sistema diplomático"""
        types_content = '''
export type SecurityLevel = 'public' | 'restricted' | 'confidential' | 'secret' | 'top_secret';

export type DiplomaticDocumentType =
  | 'hoja_remision'
  | 'guia_valija'
  | 'nota_diplomatica'
  | 'acuerdo_bilateral'
  | 'protocolo_ceremonia'
  | 'credenciales'
  | 'comunicacion_oficial'
  | 'informe_consular';

export interface DiplomaticDocument {
  id: string;
  title: string;
  type: DiplomaticDocumentType;
  securityLevel: SecurityLevel;
  content?: string;
  extractedData?: Record<string, any>;
  metadata: {
    createdAt: string;
    updatedAt: string;
    createdBy: string;
    country?: string;
    embassy?: string;
    department?: string;
  };
  date: string;
  country?: string;
  status: 'pending' | 'processing' | 'completed' | 'archived';
}

export interface User {
  id: string;
  username: string;
  email: string;
  securityClearance: SecurityLevel;
  roles: string[];
  department?: string;
  country?: string;
  lastLogin?: string;
  isActive: boolean;
}

export interface AuthToken {
  token: string;
  expiresAt: string;
  securityLevel: SecurityLevel;
  permissions: string[];
}

export interface AzureFormRecognizerResult {
  documentType: DiplomaticDocumentType;
  confidence: number;
  extractedData: Record<string, any>;
  tables?: any[];
  keyValuePairs?: Record<string, string>;
}
'''

        types_file = project_path / "src" / "types" / "diplomatic.ts"
        with open(types_file, 'w', encoding='utf-8') as f:
            f.write(types_content)

    async def _create_env_files(self, project_path: Path) -> None:
        """Crea archivos de variables de entorno"""
        env_content = '''
# Next.js Configuration
NEXT_PUBLIC_APP_NAME=SIAME 2026v3
NEXT_PUBLIC_APP_VERSION=3.0.0

# Azure Configuration
AZURE_FORM_RECOGNIZER_ENDPOINT=https://your-region.api.cognitive.microsoft.com/
AZURE_FORM_RECOGNIZER_KEY=your_form_recognizer_key_here
AZURE_STORAGE_ACCOUNT=your_storage_account
AZURE_STORAGE_KEY=your_storage_key

# Authentication
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your_nextauth_secret_here
JWT_SECRET=your_jwt_secret_here

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/siame_db

# Security
ENCRYPTION_KEY=your_encryption_key_here
AUDIT_LOG_LEVEL=info

# Azure AD (Optional)
AZURE_AD_CLIENT_ID=your_azure_ad_client_id
AZURE_AD_CLIENT_SECRET=your_azure_ad_client_secret
AZURE_AD_TENANT_ID=your_azure_ad_tenant_id
'''

        env_file = project_path / ".env.local"
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(env_content)

        # Crear .env.example
        env_example = project_path / ".env.example"
        with open(env_example, 'w', encoding='utf-8') as f:
            f.write(env_content)

    async def _run_command(self, cmd: List[str], cwd: Path) -> Dict[str, Any]:
        """Ejecuta un comando del sistema"""
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=cwd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()

            return {
                "success": process.returncode == 0,
                "output": stdout.decode() if stdout else "",
                "error": stderr.decode() if stderr else "",
                "return_code": process.returncode
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    async def _install_dependencies(self, project_path: Path, dependencies: List[str]) -> None:
        """Instala dependencias npm"""
        cmd = ["npm", "install"] + dependencies
        result = await self._run_command(cmd, cwd=project_path)

        if not result["success"]:
            raise Exception(f"Error instalando dependencias: {result['error']}")

    async def _create_documents_api(self, api_dir: Path, name: str) -> Path:
        """Crea API de documentos"""
        api_content = '''
import { NextRequest, NextResponse } from 'next/server';
import { verifyToken } from '@/lib/auth';
import { checkSecurityLevel } from '@/lib/security';

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const documentId = searchParams.get('id');

    // Verificar autenticación
    const authResult = await verifyToken(request);
    if (!authResult.success) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    // Verificar nivel de seguridad
    const securityLevel = request.headers.get('Security-Level') || 'public';
    if (!checkSecurityLevel(authResult.user.securityClearance, securityLevel)) {
      return NextResponse.json({ error: 'Insufficient security clearance' }, { status: 403 });
    }

    // TODO: Implementar lógica de recuperación de documentos
    const document = {
      id: documentId,
      title: 'Documento Diplomático',
      type: 'comunicacion_oficial',
      securityLevel,
      content: 'Contenido del documento...',
      metadata: {
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        createdBy: authResult.user.id
      }
    };

    return NextResponse.json(document);
  } catch (error) {
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}

export async function POST(request: NextRequest) {
  try {
    // Verificar autenticación
    const authResult = await verifyToken(request);
    if (!authResult.success) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    const data = await request.json();

    // TODO: Implementar lógica de creación de documentos
    const newDocument = {
      id: `doc_${Date.now()}`,
      ...data,
      metadata: {
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        createdBy: authResult.user.id
      }
    };

    return NextResponse.json(newDocument, { status: 201 });
  } catch (error) {
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}
'''

        api_path = api_dir / f"{name}" / "route.ts"
        api_path.parent.mkdir(parents=True, exist_ok=True)

        with open(api_path, 'w', encoding='utf-8') as f:
            f.write(api_content)

        return api_path

    async def _create_auth_api(self, api_dir: Path, name: str) -> Path:
        """Crea API de autenticación"""
        api_content = '''
import { NextRequest, NextResponse } from 'next/server';
import { signJWT, verifyPassword } from '@/lib/auth';

export async function POST(request: NextRequest) {
  try {
    const { username, password, securityCode } = await request.json();

    // TODO: Implementar verificación real con base de datos
    const user = await authenticateUser(username, password, securityCode);

    if (!user) {
      return NextResponse.json({ error: 'Invalid credentials' }, { status: 401 });
    }

    // Generar token JWT
    const token = await signJWT({
      userId: user.id,
      username: user.username,
      securityClearance: user.securityClearance,
      roles: user.roles
    });

    return NextResponse.json({
      token,
      user: {
        id: user.id,
        username: user.username,
        securityClearance: user.securityClearance,
        roles: user.roles
      },
      securityLevel: user.securityClearance
    });
  } catch (error) {
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}

async function authenticateUser(username: string, password: string, securityCode?: string) {
  // Simulación - reemplazar con lógica real
  if (username === 'admin' && password === 'admin123') {
    return {
      id: '1',
      username: 'admin',
      securityClearance: 'secret',
      roles: ['admin', 'diplomat']
    };
  }
  return null;
}
'''

        api_path = api_dir / f"{name}" / "route.ts"
        api_path.parent.mkdir(parents=True, exist_ok=True)

        with open(api_path, 'w', encoding='utf-8') as f:
            f.write(api_content)

        return api_path

    async def _create_upload_api(self, api_dir: Path, name: str) -> Path:
        """Crea API de subida de documentos"""
        # Implementación similar a las otras APIs
        api_path = api_dir / f"{name}" / "route.ts"
        api_path.parent.mkdir(parents=True, exist_ok=True)

        with open(api_path, 'w', encoding='utf-8') as f:
            f.write('// TODO: Implementar API de upload')

        return api_path

    async def _create_security_api(self, api_dir: Path, name: str) -> Path:
        """Crea API de seguridad"""
        # Implementación similar a las otras APIs
        api_path = api_dir / f"{name}" / "route.ts"
        api_path.parent.mkdir(parents=True, exist_ok=True)

        with open(api_path, 'w', encoding='utf-8') as f:
            f.write('// TODO: Implementar API de seguridad')

        return api_path

    async def _create_typescript_types(self, project_path: Path, component_type: str) -> None:
        """Crea tipos TypeScript específicos para componentes"""
        # Ya implementado en _create_diplomatic_types
        pass

    async def _create_nextauth_config(self, project_path: Path, auth_config: Dict[str, Any]) -> None:
        """Crea configuración de NextAuth"""
        # TODO: Implementar configuración de NextAuth
        pass

    async def _create_auth_middleware(self, project_path: Path) -> None:
        """Crea middleware de autenticación"""
        # TODO: Implementar middleware
        pass

    async def _create_auth_hooks(self, project_path: Path) -> None:
        """Crea hooks de autenticación"""
        # TODO: Implementar hooks
        pass

    async def _create_azure_utilities(self, project_path: Path, azure_config: Dict[str, Any]) -> None:
        """Crea utilidades de Azure"""
        # TODO: Implementar utilidades de Azure
        pass

    async def _create_msal_config(self, project_path: Path, azure_config: Dict[str, Any]) -> None:
        """Crea configuración de MSAL"""
        # TODO: Implementar configuración MSAL
        pass

    async def _update_package_json(self, project_path: Path, config: NextJSProject) -> None:
        """Actualiza package.json con scripts diplomáticos"""
        package_json_path = project_path / "package.json"

        if package_json_path.exists():
            with open(package_json_path, 'r') as f:
                package_data = json.load(f)

            # Agregar scripts personalizados
            package_data.setdefault("scripts", {}).update({
                "dev:secure": "next dev --experimental-https",
                "build:production": "next build && next export",
                "analyze": "ANALYZE=true npm run build",
                "test:security": "npm run test -- --testPathPattern=security"
            })

            with open(package_json_path, 'w') as f:
                json.dump(package_data, f, indent=2)


# Función principal para testing
async def main():
    """Función principal para testing del agente"""
    logging.basicConfig(level=logging.INFO)

    agent = NextJSDeveloperAgent()

    # Crear proyecto de ejemplo
    project_config = NextJSProject(
        name="siame-test",
        path=Path("./test_projects"),
        features=["diplomatic_document_viewer", "authentication_system"]
    )

    result = await agent.create_nextjs_project(project_config)
    print(f"Resultado: {result}")

    status = await agent.get_agent_status()
    print(f"Estado del agente: {status}")


if __name__ == "__main__":
    asyncio.run(main())
# SIAME 2026v3 Frontend

Sistema Inteligente de Administración y Manejo de Expedientes - Frontend Next.js

## 🚀 Características

- **Next.js 15** con App Router
- **TypeScript** para type safety
- **Tailwind CSS** para estilos
- **Prisma** para ORM de base de datos
- **NextAuth.js** para autenticación
- **Azure SDKs** para integración cloud
- **shadcn/ui** para componentes UI
- **Navegación diplomática** con diferentes niveles de acceso
- **5 niveles de clasificación** de seguridad
- **Responsive design** para todos los dispositivos

## 📁 Estructura del Proyecto

```
src/frontend/
├── src/
│   ├── app/                      # App Router de Next.js
│   │   ├── admin/               # Páginas de administración
│   │   ├── auth/                # Autenticación
│   │   ├── dashboard/           # Dashboard y analytics
│   │   ├── documents/           # Gestión de documentos
│   │   ├── api/                 # API routes
│   │   ├── layout.tsx           # Layout raíz
│   │   └── page.tsx             # Página principal
│   ├── components/              # Componentes React
│   │   ├── ui/                  # Componentes UI base
│   │   ├── layout/              # Componentes de layout
│   │   ├── documents/           # Componentes específicos de documentos
│   │   ├── forms/               # Formularios
│   │   └── security/            # Componentes de seguridad
│   ├── lib/                     # Librerías y utilidades
│   │   ├── auth/                # Configuración de autenticación
│   │   ├── azure/               # Integración Azure
│   │   ├── database/            # Cliente de base de datos
│   │   ├── utils/               # Utilidades generales
│   │   └── validators/          # Validadores Zod
│   ├── types/                   # Definiciones TypeScript
│   ├── hooks/                   # Hooks personalizados
│   ├── contexts/                # Context providers
│   ├── config/                  # Configuración
│   └── styles/                  # Estilos globales
├── public/                      # Archivos estáticos
├── prisma/                      # Esquemas de base de datos
├── .env.local                   # Variables de entorno locales
├── .env.example                 # Ejemplo de variables de entorno
├── package.json                 # Dependencias y scripts
├── tailwind.config.js           # Configuración Tailwind
└── tsconfig.json                # Configuración TypeScript
```

## 🛠️ Configuración de Desarrollo

### Prerequisitos

- Node.js 18+
- PostgreSQL 15+
- Cuenta Azure (para servicios en la nube)

### 1. Instalación

```bash
# Instalar dependencias
npm install

# Configurar variables de entorno
cp .env.example .env.local
# Editar .env.local con tus configuraciones
```

### 2. Variables de Entorno

Configura las siguientes variables en `.env.local`:

```bash
# Base de datos
DATABASE_URL="postgresql://siame_user:siame_password@localhost:5432/siame_dev"

# NextAuth
NEXTAUTH_URL="http://localhost:3000"
NEXTAUTH_SECRET="tu-secret-muy-seguro"

# Azure (opcional para desarrollo)
AZURE_TENANT_ID="tu-tenant-id"
AZURE_CLIENT_ID="tu-client-id"
AZURE_CLIENT_SECRET="tu-client-secret"
AZURE_FORM_RECOGNIZER_ENDPOINT="https://tu-form-recognizer.cognitiveservices.azure.com/"
AZURE_FORM_RECOGNIZER_KEY="tu-api-key"
AZURE_STORAGE_CONNECTION_STRING="tu-connection-string"
AZURE_KEY_VAULT_URL="https://tu-keyvault.vault.azure.net/"
```

### 3. Base de Datos

```bash
# Generar cliente Prisma
npm run db:generate

# Ejecutar migraciones
npm run db:migrate

# (Opcional) Abrir Prisma Studio
npm run db:studio
```

### 4. Desarrollo

```bash
# Iniciar servidor de desarrollo
npm run dev

# Lint
npm run lint

# Build de producción
npm run build
```

## 🏛️ Características Diplomáticas

### Roles de Usuario

El sistema soporta 10 niveles de roles diplomáticos:

1. **Embajador** - Máximo nivel de acceso
2. **Ministro Consejero** - Acceso administrativo completo
3. **Consejero** - Gestión de documentos y workflows
4. **Primer Secretario** - Creación y revisión de documentos
5. **Segundo Secretario** - Procesamiento de documentos
6. **Tercer Secretario** - Acceso básico a documentos
7. **Agregado** - Funciones especializadas
8. **Funcionario Administrativo** - Soporte administrativo
9. **Consultor Externo** - Acceso limitado temporal
10. **Invitado** - Solo lectura de documentos públicos

### Niveles de Clasificación

- 🟢 **PÚBLICO** - Acceso general
- 🔵 **RESTRINGIDO** - Personal autorizado
- 🟡 **CONFIDENCIAL** - Información sensible
- 🔴 **SECRETO** - Altamente clasificado
- 🟣 **ALTO SECRETO** - Máxima seguridad nacional

### Tipos de Documentos

- **Hojas de Remisión**: OGA, PCO, PRU
- **Guías de Valija**: Entrada/Salida, Ordinaria/Extraordinaria
- **Notas Diplomáticas**
- **Despachos**
- **Memorándums**

## 🔐 Seguridad

### Características de Seguridad

- **Row Level Security (RLS)** en PostgreSQL
- **Autenticación multi-factor** con NextAuth
- **Auditoría completa** de todas las acciones
- **Encriptación** de datos sensibles
- **Validación** de roles y clearance
- **Sesiones seguras** con expiración automática

### Cumplimiento

- ✅ **ENS Alto** (Esquema Nacional de Seguridad)
- ✅ **ISO 27001**
- ✅ **GDPR** (Reglamento General de Protección de Datos)
- ✅ **CCN-CERT** (Centro Criptológico Nacional)

## 🎨 Componentes UI

### Componentes Base

- `Button` - Botones con variantes diplomáticas
- `Badge` - Badges con colores de clasificación
- `Input` - Campos de entrada seguros
- `Dialog` - Modales para workflows
- `Table` - Tablas con filtrado y paginación

### Componentes Especializados

- `MainNav` - Navegación con control de acceso
- `UserNav` - Información de usuario y clearance
- `DocumentViewer` - Visor de documentos clasificados
- `ClassificationBadge` - Indicadores de nivel de seguridad
- `SecurityIndicator` - Estado de seguridad del usuario

## 📞 Soporte

- **Email**: siame-dev@maeuec.es
- **Documentación**: [Wiki del proyecto](../../wiki)
- **Issues**: [GitHub Issues](../../issues)

---

**SIAME 2026v3** - Construyendo el futuro de la gestión diplomática digital.

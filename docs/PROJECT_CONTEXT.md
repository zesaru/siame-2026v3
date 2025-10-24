# SIAME 2026v3 - Contexto del Proyecto

## Sistema Inteligente de Administración y Manejo de Expedientes
**Ministerio de Asuntos Exteriores, Unión Europea y Cooperación**

---

## 📋 DESCRIPCIÓN GENERAL

SIAME 2026v3 es un sistema de gestión documental diplomático de alta seguridad diseñado para procesar, almacenar y gestionar documentos clasificados del Ministerio de Asuntos Exteriores de España.

### Características Principales
- ✅ Procesamiento automático de documentos con OCR (Azure Form Recognizer)
- ✅ Clasificación de seguridad multi-nivel (PUBLICO → TOP_SECRET)
- ✅ Sistema de roles diplomáticos jerárquicos
- ✅ Gestión de Hojas de Remisión y Guías de Valija Diplomática
- ✅ Arquitectura multi-agente con orquestador Python
- ✅ Cumplimiento ENS Alto, ISO27001, GDPR
- ✅ Auditoría completa y trazabilidad de accesos

---

## 🏗️ ARQUITECTURA TECNOLÓGICA

### Frontend
- **Framework**: Next.js 14 con App Router
- **Lenguaje**: TypeScript
- **Estilos**: Tailwind CSS
- **UI Components**: shadcn/ui
- **Autenticación**: NextAuth.js

### Backend
- **API**: Next.js API Routes
- **Orquestador**: Python 3.11+ con FastAPI
- **Base de Datos**: PostgreSQL 15+
- **ORM**: Prisma
- **Cache**: Redis

### Cloud Services (Azure)
- **Form Recognizer**: OCR y extracción de datos
- **Blob Storage**: Almacenamiento de documentos
- **Key Vault**: Gestión de secretos
- **Cognitive Services**: Análisis avanzado

---

## 📄 TIPOS DE DOCUMENTOS

### 1. Hojas de Remisión
Documentos de 1-3 páginas para envío interno de correspondencia

**Variantes:**
- OGA (Oficina de Gestión Administrativa)
- PCO (Protocolo)
- PRU (Prensa)
- CON (Consular)
- ADM (Administrativa)

**Campos principales:**
- Número de documento
- Unidad remitente
- Fecha de emisión
- Asunto
- Destino
- Clasificación de seguridad

### 2. Guías de Valija Diplomática
Documentos para control de envíos en valijas diplomáticas

**Tipos:**
- Entrada Ordinaria
- Entrada Extraordinaria
- Salida Ordinaria
- Salida Extraordinaria

**Estructura jerárquica:**
```
Valija Principal (Número, Fecha, Origen/Destino)
  ├── Precintos (Tabla con números y estados)
  └── Valijas Internas
        ├── Valija Interna 1
        │     └── Items contenidos
        └── Valija Interna 2
              └── Items contenidos
```

**Campos principales:**
- Número de valija
- Fecha de despacho/recepción
- Origen/Destino
- Modalidad (Ordinaria/Extraordinaria)
- Tabla de precintos
- Contenido detallado

---

## 🔒 NIVELES DE SEGURIDAD

Sistema de clasificación basado en ENS (Esquema Nacional de Seguridad):

| Nivel | Descripción | Acceso |
|-------|-------------|--------|
| **PUBLICO** | Información de acceso público | Todos los usuarios |
| **INTERNO** | Uso interno del ministerio | Usuarios autorizados |
| **CONFIDENCIAL** | Información sensible | Supervisores y superiores |
| **SECRETO** | Información muy sensible | Administradores y directivos |
| **TOP_SECRET** | Máxima clasificación | Solo Super Administradores |

---

## 👥 ROLES DE USUARIO

Sistema jerárquico de roles con permisos heredados:

```
SUPER_ADMIN (Máximo control del sistema)
    ↓
ADMIN (Gestión completa de usuarios y documentos)
    ↓
SUPERVISOR (Supervisión de equipos y aprobaciones)
    ↓
ANALISTA (Procesamiento y análisis de documentos)
    ↓
OPERADOR (Operaciones básicas)
    ↓
CONSULTOR (Solo lectura de documentos autorizados)
```

### Roles Diplomáticos Adicionales
- Embajador
- Ministro Consejero
- Consejero
- Primer/Segundo/Tercer Secretario
- Agregado
- Funcionario Administrativo
- Consultor Externo
- Invitado

---

## 🤖 ARQUITECTURA DE AGENTES

### Orquestador Principal
Coordinador maestro que gestiona todos los subagentes y distribuye tareas.

### Subagentes Especializados

#### 1. **Analyst Agent**
- Análisis de documentos
- Clasificación automática
- Extracción de metadatos

#### 2. **Azure Specialist Agent**
- Integración con Azure Form Recognizer
- Gestión de Blob Storage
- Acceso a Key Vault

#### 3. **Database Specialist Agent**
- Diseño de esquemas con Prisma
- Operaciones CRUD
- Optimización de consultas

#### 4. **Security Specialist Agent**
- Control de accesos
- Validación de permisos
- Auditoría de seguridad

#### 5. **Frontend Developer Agent**
- UI/UX con Next.js y Tailwind
- Componentes React
- Integración con APIs

#### 6. **Backend Developer Agent**
- APIs REST y GraphQL
- Lógica de negocio
- Integración de servicios

#### 7. **Tester Agent**
- Pruebas unitarias
- Pruebas de integración
- QA y validación

---

## 📊 ESTRUCTURA DE BASE DE DATOS

### Tablas Principales

#### Users
- Información de usuario
- Roles y permisos
- Nivel de autorización de seguridad
- Información diplomática

#### Documents
- Metadatos del documento
- Clasificación de seguridad
- Contenido OCR
- Datos extraídos (JSON)
- Versionado

#### HojasRemision (Pendiente)
- Número de documento
- Unidad remitente
- Fecha y asunto
- Destino

#### GuiasValija (Pendiente)
- Número de guía
- Tipo y modalidad
- Fechas de despacho/recepción
- Relación jerárquica

#### ValijasInternas (Pendiente)
- Relación con guía principal
- Número de valija interna
- Precintos asociados

#### ItemsValija (Pendiente)
- Contenido de cada valija
- Descripción y cantidad

#### Precintos (Pendiente)
- Número de precinto
- Estado (intacto/roto)
- Relación con valijas

#### Workflows
- Flujos de aprobación
- Estados de proceso
- Pasos configurables

#### AuditLog
- Registro completo de acciones
- Trazabilidad total
- Cambios detallados

---

## 🚀 ESTADO ACTUAL DEL PROYECTO

### ✅ Completado

#### Fase 1: Estructura del Proyecto
- [x] 93 archivos creados
- [x] Carpetas organizadas (frontend, orchestrator, agents, config, docs)
- [x] Configuración de Docker
- [x] Estructura de agentes

#### Fase 2: Configuración del Entorno
- [x] requirements.txt para Python
- [x] .env.example con todas las variables
- [x] .env.local para desarrollo
- [x] Schema.prisma básico
- [x] Documentación de contexto

### ⏳ En Progreso

#### Fase 2: Configuración (Continuación)
- [ ] Completar schema.prisma con modelos específicos:
  - HojasRemision
  - GuiasValija (con estructura jerárquica)
  - ValijasInternas
  - ItemsValija
  - Precintos
  - Autorizaciones por documento

### 📋 Pendiente

#### Fase 3: Implementación del Orquestador
- [ ] Implementar agentes Python
- [ ] Sistema de comunicación entre agentes
- [ ] Coordinación de tareas
- [ ] Manejo de errores y reintentos

#### Fase 4: Integración con Azure
- [ ] Configurar Azure Form Recognizer
- [ ] Implementar Blob Storage
- [ ] Conectar Key Vault
- [ ] Servicios cognitivos

#### Fase 5: Frontend Next.js
- [ ] Sistema de autenticación
- [ ] Dashboard principal
- [ ] Módulos de carga de documentos
- [ ] Visualización de guías de valija
- [ ] Gestión de usuarios

#### Fase 6: APIs y Backend
- [ ] Endpoints REST
- [ ] Lógica de negocio
- [ ] Validaciones de seguridad
- [ ] Sistema de permisos

#### Fase 7: Testing y QA
- [ ] Pruebas unitarias
- [ ] Pruebas de integración
- [ ] Pruebas de seguridad
- [ ] Pruebas de rendimiento

#### Fase 8: Despliegue
- [ ] Configuración de producción
- [ ] CI/CD Pipeline
- [ ] Monitoreo
- [ ] Documentación final

---

## 🔧 COMANDOS ÚTILES

### Instalación
```bash
# Instalar dependencias Python
cd orchestrator && pip install -r requirements.txt

# Instalar dependencias Node.js
cd src/frontend && npm install

# Configurar base de datos
cd src/frontend && npx prisma generate && npx prisma migrate dev
```

### Desarrollo
```bash
# Iniciar todos los servicios
make dev

# Iniciar solo frontend
cd src/frontend && npm run dev

# Iniciar solo orchestrator
cd orchestrator && python main.py

# Iniciar base de datos
docker-compose up -d postgres redis
```

### Testing
```bash
# Tests frontend
cd src/frontend && npm test

# Tests backend
cd orchestrator && pytest

# Tests de integración
make test-integration
```

---

## 📚 REFERENCIAS IMPORTANTES

### Documentación
- [Next.js 14](https://nextjs.org/docs)
- [Prisma ORM](https://www.prisma.io/docs)
- [Azure Form Recognizer](https://learn.microsoft.com/azure/ai-services/document-intelligence/)
- [FastAPI](https://fastapi.tiangolo.com/)

### Normativas
- ENS (Esquema Nacional de Seguridad)
- ISO 27001
- GDPR
- CCN-CERT

### Contacto
- Repositorio: GitHub (siame-2026v3)
- Documentación: `/docs`
- Ejemplos: `/examples`

---

## 🔐 SEGURIDAD

### Consideraciones Importantes
1. **NUNCA** commitear archivos `.env` con credenciales reales
2. Usar Azure Key Vault para secretos en producción
3. Implementar autenticación de dos factores
4. Auditar todos los accesos a documentos clasificados
5. Encriptar documentos en reposo y en tránsito
6. Realizar backups cifrados diariamente
7. Mantener logs de auditoría durante 7 años

---

**Última actualización**: 2025-09-30
**Versión**: 3.0.0
**Estado**: En Desarrollo Activo
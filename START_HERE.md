# 🚀 SIAME 2026v3 - EMPIEZA AQUÍ

**Última actualización**: 2025-10-22
**Progreso**: 24% completado
**Estado**: ✅ Listo para instalación

---

## 🎯 INICIO ULTRA-RÁPIDO (3 COMANDOS)

```bash
# 1. Instalar servicios (PostgreSQL, Redis, pip)
./install-services.sh

# 2. Aplicar migraciones de base de datos
./run-migrations.sh

# 3. Iniciar desarrollo
./start-dev.sh
```

**¡Eso es todo!** 🎉

---

## 📋 ¿QUÉ ES SIAME 2026v3?

**Sistema Inteligente de Análisis Multiagente Especializado** para el procesamiento de documentos diplomáticos del Ministerio de Asuntos Exteriores.

### Características Principales

- 🤖 **7 Agentes Especializados** coordinados por un orchestrator
- 🔐 **5 Niveles de Seguridad** (Público → Alto Secreto)
- 📄 **Documentos Diplomáticos**: Hojas de Remisión, Guías de Valija, Notas
- ☁️ **Integración con Azure**: Form Recognizer, Blob Storage, Key Vault
- 📊 **Auditoría Completa** de todas las operaciones
- 🎨 **Frontend Moderno**: Next.js 15 + TypeScript + Tailwind CSS

---

## 🛠️ SCRIPTS DISPONIBLES

### 1️⃣ `./install-services.sh` - Instalación Automática

**¿Qué hace?**
- ✅ Instala PostgreSQL 15
- ✅ Instala Redis 7
- ✅ Instala Python pip
- ✅ Configura la base de datos
- ✅ Configura inicio automático de servicios
- ✅ Instala dependencias Python

**Cuándo usarlo:** Primera vez que configuras el proyecto

```bash
./install-services.sh
```

**Duración:** ~5-10 minutos

---

### 2️⃣ `./verify-setup.sh` - Verificación del Sistema

**¿Qué hace?**
- 🔍 Verifica Node.js y npm
- 🔍 Verifica Python y pip
- 🔍 Verifica PostgreSQL
- 🔍 Verifica Redis
- 🔍 Verifica Prisma
- 🔍 Verifica dependencias

**Cuándo usarlo:** Para diagnosticar problemas o verificar el estado

```bash
./verify-setup.sh
```

**Duración:** ~10 segundos

---

### 3️⃣ `./run-migrations.sh` - Aplicar Migraciones

**¿Qué hace?**
- ✅ Valida el schema de Prisma
- ✅ Genera el cliente de Prisma
- ✅ Crea todas las tablas en PostgreSQL
- ✅ Aplica índices y relaciones
- ✅ Muestra estadísticas de la BD

**Cuándo usarlo:** Después de instalar servicios, o al actualizar el schema

```bash
./run-migrations.sh
```

**Duración:** ~30 segundos

---

### 4️⃣ `./start-dev.sh` - Inicio de Desarrollo

**¿Qué hace?**
- ✅ Verifica que los servicios estén corriendo
- ✅ Inicia servicios automáticamente si están parados
- ✅ Verifica que las migraciones estén aplicadas
- ✅ Ofrece menú interactivo para iniciar:
  - Frontend (Next.js)
  - Prisma Studio (explorador de BD)
  - Orchestrator (backend)

**Cuándo usarlo:** Cada vez que quieras trabajar en el proyecto

```bash
./start-dev.sh
```

**Duración:** ~5 segundos + tiempo de inicio del servicio elegido

---

## 📊 FLUJO DE TRABAJO COMPLETO

```
┌─────────────────────────────────────────────┐
│ PRIMERA VEZ (Configuración Inicial)         │
└─────────────────────────────────────────────┘
   1. ./install-services.sh      (5-10 min)
   2. ./run-migrations.sh         (30 seg)
   3. ./start-dev.sh              (elegir opción)

┌─────────────────────────────────────────────┐
│ DÍA A DÍA (Desarrollo Normal)               │
└─────────────────────────────────────────────┘
   1. ./start-dev.sh              (iniciar)
   2. Trabajar en el código
   3. Ctrl+C para detener

┌─────────────────────────────────────────────┐
│ SI HAY PROBLEMAS                            │
└─────────────────────────────────────────────┘
   1. ./verify-setup.sh           (diagnosticar)
   2. Seguir las recomendaciones que aparezcan
```

---

## 🗄️ ESTRUCTURA DE LA BASE DE DATOS

Una vez aplicadas las migraciones, tendrás **17 tablas**:

### Usuarios y Seguridad
- `users` - Usuarios del sistema con roles diplomáticos
- `accounts` - Cuentas de autenticación (NextAuth)
- `sessions` - Sesiones activas
- `verification_tokens` - Tokens de verificación

### Documentos Diplomáticos
- `documents` - Documentos base
- `hojas_remision` - Hojas de remisión (OGA, PCO, PRU)
- `guias_valija` - Guías de valija diplomática
- `valijas_internas` - Valijas internas jerárquicas
- `items_valija` - Items dentro de valijas
- `precintos` - Control de precintos
- `document_authorizations` - Permisos granulares

### Workflows y Procesos
- `workflows` - Definición de flujos de trabajo
- `workflow_steps` - Pasos de cada workflow
- `document_workflows` - Relación documentos-workflows

### Comunicación y Auditoría
- `notifications` - Notificaciones del sistema
- `audit_logs` - Registro completo de auditoría
- `file_uploads` - Archivos subidos
- `system_config` - Configuración del sistema

---

## 🎨 TECNOLOGÍAS UTILIZADAS

### Frontend
- **Next.js 15** - Framework React con App Router
- **TypeScript** - Tipado estático
- **Tailwind CSS** - Estilos utility-first
- **Prisma** - ORM para base de datos
- **NextAuth** - Autenticación

### Backend
- **Python 3.12** - Lenguaje principal del orchestrator
- **FastAPI** - Framework web moderno
- **PostgreSQL 15** - Base de datos relacional
- **Redis 7** - Cache y mensajería
- **Prisma** - ORM compartido con frontend

### Cloud
- **Azure Form Recognizer** - OCR y extracción de datos
- **Azure Blob Storage** - Almacenamiento de documentos
- **Azure Key Vault** - Gestión de secretos

---

## 📚 DOCUMENTACIÓN COMPLETA

| Archivo | Propósito | Leer |
|---------|-----------|------|
| **START_HERE.md** | Este archivo - Inicio rápido | ⭐ **PRIMERO** |
| **QUICK_START.md** | Guía rápida de 3 pasos | Si tienes prisa |
| **SETUP_GUIDE.md** | Instalación detallada | Si hay problemas |
| **NEXT_STEPS.md** | Próximos pasos y decisiones | Después de instalar |
| **STATUS.md** | Estado del proyecto | Ver progreso |
| **README.md** | Información completa | Referencia |

---

## 🔧 COMANDOS ÚTILES

### Servicios
```bash
# Iniciar PostgreSQL
sudo service postgresql start

# Iniciar Redis
sudo service redis-server start

# Ver estado de servicios
./verify-setup.sh
```

### Base de Datos
```bash
# Conectar a PostgreSQL
PGPASSWORD=siame_password psql -U siame_user -d siame_dev -h localhost

# Explorar con Prisma Studio
cd src/frontend && npx prisma studio

# Resetear base de datos (¡CUIDADO! Borra todos los datos)
cd src/frontend && npx prisma migrate reset
```

### Desarrollo
```bash
# Frontend
cd src/frontend && npm run dev

# Prisma Studio
cd src/frontend && npx prisma studio

# Orchestrator
cd orchestrator && source venv/bin/activate && python main.py
```

---

## 🚨 SOLUCIÓN RÁPIDA DE PROBLEMAS

### "PostgreSQL no está disponible"
```bash
sudo service postgresql start
./verify-setup.sh
```

### "Redis no responde"
```bash
sudo service redis-server start
./verify-setup.sh
```

### "Error en migraciones"
```bash
cd src/frontend
npx prisma migrate reset
npx prisma migrate dev --name initial_setup
```

### "No module named pip"
```bash
./install-services.sh
```

---

## 🎯 OBJETIVOS DEL PROYECTO

### Fase Actual: Fase 3 (20% → 100%)
- [x] Scripts de instalación creados
- [ ] Servicios instalados y configurados
- [ ] Migraciones aplicadas
- [ ] Frontend funcionando

### Próximas Fases
- **Fase 4**: Implementación del Orchestrator
- **Fase 5**: Integración con Azure
- **Fase 6**: Frontend Next.js
- **Fase 7**: APIs y Backend
- **Fase 8**: Testing y QA
- **Fase 9**: Despliegue

---

## 🌟 CARACTERÍSTICAS DESTACADAS

### 1. Sistema Multi-Agente
7 agentes especializados trabajando en conjunto:
- Document Processor
- Database Manager
- Azure Specialist
- Security Guardian
- Workflow Manager
- Communication Hub
- Quality Assurance

### 2. Seguridad Diplomática
5 niveles de clasificación:
- **Público** - Acceso general
- **Restringido** - Personal autorizado
- **Confidencial** - Información sensible
- **Secreto** - Altamente clasificado
- **Alto Secreto** - Máxima seguridad

### 3. Documentos Específicos
- **Hojas de Remisión** (OGA, PCO, PRU)
- **Guías de Valija** (Entrada/Salida, Ordinaria/Extraordinaria)
- **Valijas Internas** (Sistema jerárquico con items y precintos)
- **Notas Diplomáticas**
- **Despachos y Memorándums**

---

## 💡 CONSEJOS PARA DESARROLLO

### 1. Usa Prisma Studio
Es la forma más rápida de ver y editar datos:
```bash
cd src/frontend && npx prisma studio
```

### 2. Variables de Entorno
Las actuales son para **desarrollo**. No uses en producción.

### 3. Git
Evita commitear archivos `.env` con credenciales reales.

### 4. Servicios
Los servicios se detienen al cerrar WSL. Usa `start-dev.sh` para reiniciarlos.

---

## ✅ CHECKLIST DE INICIO

Marca cuando completes cada paso:

- [ ] Ejecuté `./install-services.sh`
- [ ] Ejecuté `./run-migrations.sh`
- [ ] Ejecuté `./verify-setup.sh` y todo está ✅
- [ ] Puedo ver la BD en Prisma Studio
- [ ] El frontend inicia con `npm run dev`
- [ ] Entiendo la estructura del proyecto
- [ ] Leí la documentación relevante

---

## 🎉 ¡LISTO PARA EMPEZAR!

```bash
# Tu primer comando debería ser:
./install-services.sh

# Luego:
./run-migrations.sh

# Y finalmente:
./start-dev.sh
```

**¿Preguntas?** Consulta los archivos de documentación o el README.md principal.

---

**SIAME 2026v3** - Construyendo el futuro del análisis diplomático con IA 🚀

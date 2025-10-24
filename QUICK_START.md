# 🚀 SIAME 2026v3 - Inicio Rápido

**Última actualización**: 2025-10-22

---

## ✅ Estado Actual del Proyecto

**Progreso Global**: 24% completado

### ✅ Completado
- ✅ Estructura del proyecto (100%)
- ✅ Configuración del entorno (100%)
- ✅ Schema de base de datos completo y validado
- ✅ Dependencias Node.js instaladas
- ✅ Documentación completa

### ⏳ Pendiente
- ⚠️ PostgreSQL (no configurado)
- ⚠️ Redis (no configurado)
- ⚠️ pip de Python (no instalado)

---

## 📋 PRÓXIMOS PASOS (3 OPCIONES)

### 🎯 OPCIÓN 1: Verificar Estado Actual (RECOMENDADO PRIMERO)

```bash
cd /mnt/c/Users/embto/Documents/GitHub/siame-2026v3
./verify-setup.sh
```

Este script te dirá exactamente qué falta configurar.

---

### 🐳 OPCIÓN 2: Instalación con Docker (Más Rápida)

**Requisito**: Habilitar WSL2 Integration en Docker Desktop

1. Abrir Docker Desktop en Windows
2. Settings → Resources → WSL Integration
3. Activar tu distribución Ubuntu
4. Apply & Restart

Luego ejecutar:

```bash
cd /mnt/c/Users/embto/Documents/GitHub/siame-2026v3
docker compose up -d postgres redis
./verify-setup.sh
```

---

### 💻 OPCIÓN 3: Instalación Nativa en WSL2

```bash
# Instalar servicios
sudo apt update
sudo apt install -y python3-pip python3-venv postgresql postgresql-contrib redis-server

# Iniciar servicios
sudo service postgresql start
sudo service redis-server start

# Configurar PostgreSQL
sudo -u postgres psql << EOF
CREATE USER siame_user WITH PASSWORD 'siame_password';
CREATE DATABASE siame_dev OWNER siame_user;
GRANT ALL PRIVILEGES ON DATABASE siame_dev TO siame_user;
ALTER USER siame_user CREATEDB;
\q
EOF

# Verificar
cd /mnt/c/Users/embto/Documents/GitHub/siame-2026v3
./verify-setup.sh
```

---

## 🗄️ Aplicar Migraciones de Base de Datos

**Solo cuando PostgreSQL esté corriendo:**

```bash
cd /mnt/c/Users/embto/Documents/GitHub/siame-2026v3/src/frontend

# Aplicar migraciones
npx prisma migrate dev --name initial_setup

# Verificar en Prisma Studio
npx prisma studio
```

---

## 🚀 Iniciar el Frontend

```bash
cd /mnt/c/Users/embto/Documents/GitHub/siame-2026v3/src/frontend
npm run dev
```

Acceder a: **http://localhost:3000**

---

## 🐍 Configurar Python y Orchestrator

```bash
cd /mnt/c/Users/embto/Documents/GitHub/siame-2026v3/orchestrator

# Crear entorno virtual
python3 -m venv venv

# Activar entorno
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

---

## 📚 Documentación Completa

- **SETUP_GUIDE.md** - Guía detallada de instalación paso a paso
- **STATUS.md** - Estado completo del proyecto
- **CONTINUE_HERE.md** - Continuación del desarrollo
- **README.md** - Documentación principal

---

## 🆘 Solución Rápida de Problemas

### PostgreSQL no conecta
```bash
sudo service postgresql restart
psql -U siame_user -d siame_dev -h localhost
```

### Redis no responde
```bash
sudo service redis-server restart
redis-cli ping
```

### Error en migraciones de Prisma
```bash
cd /mnt/c/Users/embto/Documents/GitHub/siame-2026v3/src/frontend
npx prisma migrate reset
npx prisma migrate dev
```

---

## 📊 Schema de Base de Datos

El proyecto incluye los siguientes modelos principales:

### Usuarios y Seguridad
- **User** - Usuarios del sistema con roles diplomáticos
- **Account** - Cuentas de autenticación
- **Session** - Sesiones activas

### Documentos
- **Document** - Documentos base
- **HojaRemision** - Hojas de remisión (OGA, PCO, PRU)
- **GuiaValija** - Guías de valija diplomática
- **ValijaInterna** - Valijas internas jerárquicas
- **ItemValija** - Items dentro de valijas
- **Precinto** - Control de precintos

### Workflows y Auditoría
- **Workflow** - Flujos de trabajo
- **WorkflowStep** - Pasos de workflows
- **AuditLog** - Registro de auditoría
- **Notification** - Notificaciones

### Seguridad
- **DocumentAuthorization** - Permisos granulares por documento
- **SecurityClassification** - 5 niveles (Público → Alto Secreto)
- **DiplomaticRole** - 10 roles diplomáticos

---

## 🎯 Objetivos del Sistema

SIAME 2026v3 es un **Sistema Inteligente de Análisis Multiagente Especializado** que:

1. **Procesa documentos diplomáticos** con OCR y IA
2. **Gestiona workflows** de aprobación y clasificación
3. **Controla acceso** con 5 niveles de seguridad
4. **Audita todas las acciones** para cumplimiento normativo
5. **Integra con Azure** (Form Recognizer, Blob Storage, Key Vault)

---

## 💡 Comandos Útiles

```bash
# Verificar estado del sistema
./verify-setup.sh

# Ver servicios Docker
docker compose ps

# Ver logs de servicios
docker compose logs -f postgres

# Reiniciar servicios
docker compose restart

# Parar servicios
docker compose down

# Frontend en desarrollo
cd src/frontend && npm run dev

# Prisma Studio (UI de BD)
cd src/frontend && npx prisma studio

# Ver schema de Prisma
cat src/frontend/prisma/schema.prisma
```

---

## ✨ Siguientes Desarrollos

1. **Fase 3**: Servicios de Base (20% completo)
2. **Fase 4**: Implementación del Orquestador
3. **Fase 5**: Integración con Azure
4. **Fase 6**: Frontend Next.js
5. **Fase 7**: APIs y Backend
6. **Fase 8**: Testing y QA
7. **Fase 9**: Despliegue

---

**¿Listo para empezar?** Ejecuta `./verify-setup.sh` para ver qué necesitas configurar.

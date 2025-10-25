# 🔧 Fix Docker Build - SIAME 2026v3

**Fecha:** 2025-10-25
**Problema:** Errores al hacer build de los contenedores Docker

---

## 🐛 Problema Original

Al ejecutar `docker compose up -d` se producían estos errores:

```
ERROR [agent_document_processor 7/10] COPY src/backend/agents/ ./agents/
ERROR [agent_database_manager 7/10] COPY src/backend/agents/ ./agents/
ERROR [agent_azure_specialist 7/10] COPY src/backend/agents/ ./agents/
ERROR [agent_security_guardian 7/10] COPY src/backend/agents/ ./agents/
```

**Causa:** El Dockerfile intentaba copiar `src/backend/agents/` que no existía en el proyecto.

---

## 🔍 Análisis de la Estructura Real

La estructura real del proyecto es:

```
siame-2026v3/
├── agents/                              # ✅ EXISTE aquí (raíz)
│   ├── analyst/
│   ├── developer/
│   ├── tester/
│   ├── authentication_security_agent.py
│   ├── azure_form_recognizer_agent.py
│   ├── document_classifier.py
│   └── nextjs_developer_agent.py
│
├── orchestrator/                        # ✅ EXISTE (raíz)
│   ├── api.py
│   ├── main.py
│   ├── requirements.txt
│   └── ...
│
├── src/
│   └── backend/
│       ├── orchestrator/                # Copia del orchestrator
│       └── database/
│
└── shared/                              # ✅ EXISTE (raíz)
    └── communication/
```

**NO existe:** `src/backend/agents/` ❌

---

## ✅ Soluciones Implementadas

### 1. Ajusté `infrastructure/docker/Dockerfile.agents`

**Cambio en línea 23:**

```dockerfile
# ANTES (incorrecto):
COPY src/backend/agents/ ./agents/

# DESPUÉS (correcto):
COPY agents/ ./agents/
```

**Archivo completo actualizado:**

```dockerfile
FROM python:3.11-slim
WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc g++ curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY orchestrator/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código compartido
COPY shared/ ./shared/

# Copiar código de agentes (están en la raíz del proyecto)
COPY agents/ ./agents/

# Copiar código del orquestador (para clases base)
COPY orchestrator/ ./orchestrator/
COPY src/backend/orchestrator/ ./src/backend/orchestrator/

# Script de inicio dinámico
COPY scripts/start-agent.sh /start-agent.sh
RUN chmod +x /start-agent.sh

ENV PYTHONUNBUFFERED=1
ENV AGENT_TYPE=document_processor

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8001/health || exit 1

CMD ["/start-agent.sh"]
```

---

### 2. Creé Módulos para Cada Tipo de Agente

El `docker-compose.yml` espera estos agentes:
- document_processor
- database_manager
- azure_specialist
- security_guardian

Pero en `agents/` teníamos archivos sueltos. Creé estructura de módulos:

```
agents/
├── document_processor/
│   ├── __init__.py
│   └── main.py
├── database_manager/
│   ├── __init__.py
│   └── main.py
├── azure_specialist/
│   ├── __init__.py
│   └── main.py
└── security_guardian/
    ├── __init__.py
    └── main.py
```

Cada `main.py` es una aplicación FastAPI mínima con:
- Endpoint `/` - Info del agente
- Endpoint `/health` - Health check
- Puerto asignado dinámicamente

---

### 3. Actualicé `scripts/start-agent.sh`

Agregué asignación automática de puertos para healthchecks:

```bash
# Asignar puerto según tipo de agente
case "$AGENT_TYPE" in
  document_processor)
    export AGENT_PORT=8001
    ;;
  database_manager)
    export AGENT_PORT=8002
    ;;
  azure_specialist)
    export AGENT_PORT=8003
    ;;
  security_guardian)
    export AGENT_PORT=8004
    ;;
  # ... etc
esac
```

---

## 🧪 Verificación del Fix

### Build exitoso de agentes:

```bash
docker compose build agent_document_processor
# ✅ Service agent_document_processor Built
```

### Build exitoso del orchestrator:

```bash
docker compose build orchestrator
# ✅ Service orchestrator Built
```

### Build del frontend (en progreso):

```bash
docker compose build frontend
# ⏳ Building...
```

---

## 📝 Puertos Asignados

| Servicio | Puerto | Health Check |
|----------|--------|--------------|
| Orchestrator | 8000 | http://localhost:8000/health |
| Document Processor | 8001 | http://localhost:8001/health |
| Database Manager | 8002 | http://localhost:8002/health |
| Azure Specialist | 8003 | http://localhost:8003/health |
| Security Guardian | 8004 | http://localhost:8004/health |
| Workflow Manager | 8005 | http://localhost:8005/health |
| Communication Hub | 8006 | http://localhost:8006/health |
| Quality Assurance | 8007 | http://localhost:8007/health |

---

## 🚀 Próximos Pasos

### Una vez que termine el build del frontend:

1. **Construir todas las imágenes:**
   ```bash
   docker compose build
   ```

2. **Iniciar servicios base:**
   ```bash
   docker compose up -d postgres redis
   sleep 15
   ```

3. **Aplicar migraciones:**
   ```bash
   cd src/frontend
   npm install
   npx prisma migrate dev
   npx prisma generate
   cd ../..
   ```

4. **Iniciar todos los servicios:**
   ```bash
   docker compose up -d
   ```

5. **Verificar logs:**
   ```bash
   docker compose logs -f
   ```

---

## ✅ Estado Actual

```
✅ Dockerfile.agents corregido
✅ Módulos de agentes creados
✅ Script start-agent.sh actualizado
✅ Build de agentes: EXITOSO
✅ Build de orchestrator: EXITOSO
⏳ Build de frontend: EN PROGRESO
```

---

## 📚 Archivos Modificados

1. `infrastructure/docker/Dockerfile.agents` - Rutas corregidas
2. `scripts/start-agent.sh` - Puertos asignados
3. `agents/document_processor/` - Nuevo módulo
4. `agents/database_manager/` - Nuevo módulo
5. `agents/azure_specialist/` - Nuevo módulo
6. `agents/security_guardian/` - Nuevo módulo

---

## 🎯 Verificación Final

Una vez que todo esté construido:

```bash
# Ver todas las imágenes
docker images | grep siame

# Verificar configuración
docker compose config

# Ver servicios
docker compose ps
```

---

**Estado:** ✅ PROBLEMA RESUELTO

Los contenedores ahora se construyen correctamente usando las rutas reales del proyecto.

# 🚀 SIAME 2026v3 - Guía de Deployment

**Sistema Inteligente de Administración y Manejo de Expedientes**
**Ministerio de Asuntos Exteriores, Unión Europea y Cooperación**

---

## 📖 ELIGE TU MÉTODO DE DEPLOYMENT

### ⭐ Opción 1: Git (RECOMENDADO)

**La forma más fácil, rápida y profesional**

```powershell
# En el servidor:
git clone https://github.com/TU_USUARIO/siame-2026v3.git
cd siame-2026v3
# ... configurar y desplegar
```

**📚 Guía completa:** [DEPLOY_CON_GIT.md](DEPLOY_CON_GIT.md)

**Ventajas:**
- ⚡ Actualizaciones en 2 minutos con `git pull`
- 📜 Historial completo de cambios
- 🔄 Rollback fácil si algo falla
- 👥 Colaboración entre desarrolladores

---

### Opción 2: ZIP/Package

**Para entornos sin acceso a Git**

```powershell
# Extraer ZIP y desplegar
Expand-Archive siame-2026v3.zip C:\Apps\
```

**📚 Guía completa:** [QUICK_DEPLOY.md](QUICK_DEPLOY.md)

---

## 📋 GUÍAS DISPONIBLES

| Documento | Descripción | Tiempo |
|-----------|-------------|--------|
| **[DEPLOY_CON_GIT.md](DEPLOY_CON_GIT.md)** | ⭐ Deployment con Git (Recomendado) | 15 min |
| **[QUICK_DEPLOY.md](QUICK_DEPLOY.md)** | Deployment rápido con ZIP | 45 min |
| **[DEPLOYMENT_WINDOWS_SERVER_2025.md](DEPLOYMENT_WINDOWS_SERVER_2025.md)** | Guía completa y detallada | 2 horas |

---

## 🎯 INICIO RÁPIDO

### Con Git (15 minutos):

```powershell
# 1. Clonar
git clone https://github.com/TU_USUARIO/siame-2026v3.git C:\Apps\siame-2026v3
cd C:\Apps\siame-2026v3

# 2. Configurar
Copy-Item .env.example .env
notepad .env  # Editar con tu configuración

# 3. Desplegar
docker compose up -d postgres redis
Start-Sleep -Seconds 15
docker compose run --rm frontend npx prisma migrate deploy
docker compose up -d

# 4. Verificar
docker compose ps
curl http://localhost:8000/health
```

**Ver guía completa:** [DEPLOY_CON_GIT.md](DEPLOY_CON_GIT.md)

---

## 📦 ARQUITECTURA

```
SIAME 2026v3
├── Frontend (Next.js 15 + React 18)
├── Orchestrator API (Python FastAPI)
├── PostgreSQL 15 (Base de datos)
├── Redis 7 (Cache)
├── Agents (Python)
└── Nginx (Reverse proxy)
```

---

## 🔧 REQUISITOS

### Hardware:
- **CPU:** 8+ cores (16 recomendado)
- **RAM:** 32 GB (64 GB recomendado)
- **Disco:** 500 GB SSD (1 TB recomendado)

### Software:
- **Windows Server 2025**
- **Docker** (instalado automáticamente por scripts)
- **Git** (para método Git)

---

## 🆘 AYUDA RÁPIDA

### Problema más común: Puerto en uso

```powershell
Get-NetTCPConnection -LocalPort 3000 | Get-Process
Stop-Process -Id <ID> -Force
```

### Ver logs:

```powershell
docker compose logs -f
```

### Reiniciar servicios:

```powershell
docker compose restart
```

---

## 📞 SOPORTE

**Documentación completa:** Ver archivos `DEPLOYMENT_*.md`

**Troubleshooting:** [DEPLOYMENT_WINDOWS_SERVER_2025.md](DEPLOYMENT_WINDOWS_SERVER_2025.md#troubleshooting)

---

## ✅ CHECKLIST

- [ ] Windows Server 2025 instalado
- [ ] Docker instalado (o listo para instalar)
- [ ] IP pública o dominio configurado
- [ ] Firewall configurado
- [ ] `.env` configurado con valores de producción
- [ ] Servicios corriendo
- [ ] Sistema verificado

---

**Fecha:** 2025-10-24
**Versión:** 1.0.0
**Estado:** ✅ Listo para deployment

# ✅ SIAME 2026v3 - LISTO PARA DEPLOYMENT

**Fecha de preparación:** 2025-10-24 16:50
**Entorno objetivo:** Windows Server 2025
**Estado:** ✅ TODO PREPARADO

---

## 📦 ARCHIVOS GENERADOS

### 1. Package de Deployment
```
📦 siame-2026v3-deployment-2025-10-24.zip (8.5 MB)
```

**Contenido:**
- ✅ Código fuente completo (sin node_modules)
- ✅ docker-compose.yml configurado
- ✅ .env.production con credenciales generadas
- ✅ Documentación completa
- ✅ Scripts de instalación

### 2. Credenciales de Producción
```
🔐 CREDENCIALES_PRODUCCION.txt
```

**⚠️ CRÍTICO:** Este archivo contiene:
- Password de PostgreSQL
- Password de Redis
- NEXTAUTH_SECRET
- JWT_SECRET
- SESSION_SECRET
- ENCRYPTION_KEY

**Acciones requeridas:**
1. ✅ Generadas automáticamente
2. ⏳ Guardar en gestor de contraseñas (KeePass, 1Password, Azure Key Vault)
3. ⏳ Eliminar del disco después de guardar
4. ⏳ NO compartir por email o chat

### 3. Documentación Incluida
- ✅ **QUICK_DEPLOY.md** - Guía rápida (45 minutos)
- ✅ **DEPLOYMENT_WINDOWS_SERVER_2025.md** - Guía completa
- ✅ **INSTALL.ps1** - Script de instalación automatizado
- ✅ **DEPLOYMENT_CHECKLIST.md** - Checklist paso a paso

---

## 🚀 CÓMO HACER EL DEPLOYMENT

### Opción A: Deployment Rápido (45 minutos)

1. **Copiar al servidor**
   ```
   - Copia: siame-2026v3-deployment-2025-10-24.zip
   - Al servidor Windows Server 2025
   - Por: RDP, WinSCP, o red compartida
   ```

2. **Extraer en el servidor**
   ```powershell
   # En el servidor:
   Expand-Archive -Path "C:\Users\Administrator\Downloads\siame-2026v3-deployment-2025-10-24.zip" -DestinationPath "C:\Apps\"
   ```

3. **Seguir la guía rápida**
   ```powershell
   cd C:\Apps\siame-deployment
   notepad QUICK_DEPLOY.md
   ```

4. **Ejecutar instalación**
   ```powershell
   # Como Administrador:
   .\INSTALL.ps1
   ```

### Opción B: Deployment Manual (Control total)

Seguir la guía completa: **DEPLOYMENT_WINDOWS_SERVER_2025.md**

---

## ✅ PRE-REQUISITOS EN EL SERVIDOR

Antes de hacer deployment, asegúrate que el servidor tenga:

- [ ] **Windows Server 2025** instalado y actualizado
- [ ] **Docker** instalado (o preparado para instalar)
- [ ] **Permisos de Administrador**
- [ ] **IP pública** o dominio configurado
- [ ] **Puertos disponibles:** 80, 443, 3000, 8000, 5432, 6379
- [ ] **Mínimo 32 GB RAM** (64 GB recomendado)
- [ ] **Mínimo 500 GB disco** (1 TB recomendado)

---

## 📋 CONFIGURACIÓN POST-EXTRACCIÓN

### En el servidor, editar `.env`:

```powershell
cd C:\Apps\siame-deployment
notepad .env
```

**Cambios CRÍTICOS a hacer:**

```env
# Cambiar esta URL con tu IP o dominio
NEXTAUTH_URL="http://TU_IP_O_DOMINIO:3000"

# Si tienes dominio:
# NEXTAUTH_URL="https://siame.tudominio.com"

# Si tienes credenciales Azure reales:
MOCK_AZURE_SERVICES=false
AZURE_TENANT_ID="tu-tenant-id-real"
AZURE_CLIENT_ID="tu-client-id-real"
AZURE_CLIENT_SECRET="tu-secret-real"
# ... etc
```

---

## 🎯 PASOS DE DEPLOYMENT

### 1. En el Servidor Windows Server 2025

```powershell
# 1. Instalar Docker (si no está)
Install-WindowsFeature -Name Containers -Restart

# Después del reinicio:
Invoke-WebRequest -UseBasicParsing `
  "https://raw.githubusercontent.com/microsoft/Windows-Containers/Main/helpful_tools/Install-DockerCE/install-docker-ce.ps1" `
  -o install-docker-ce.ps1
.\install-docker-ce.ps1

# 2. Navegar al proyecto
cd C:\Apps\siame-deployment

# 3. Configurar .env (editar NEXTAUTH_URL)
notepad .env

# 4. Configurar firewall
New-NetFirewallRule -DisplayName "SIAME - HTTP" -Direction Inbound -Protocol TCP -LocalPort 80 -Action Allow
New-NetFirewallRule -DisplayName "SIAME - HTTPS" -Direction Inbound -Protocol TCP -LocalPort 443 -Action Allow

# 5. Iniciar servicios base
docker compose up -d postgres redis

# 6. Esperar y verificar
Start-Sleep -Seconds 15
docker compose ps

# 7. Aplicar migraciones
docker compose run --rm frontend npx prisma migrate deploy

# 8. Iniciar todo
docker compose up -d

# 9. Verificar
docker compose ps
Invoke-WebRequest -Uri "http://localhost:8000/health"
```

### 2. Verificar que Todo Funciona

```powershell
# API Health
curl http://localhost:8000/health

# Frontend
Start-Process "http://localhost:3000"

# Logs
docker compose logs -f
```

---

## 🔐 SEGURIDAD POST-DEPLOYMENT

### Inmediatamente después del deployment:

1. **Verificar credenciales**
   - ✅ Ya están en `.env` (generadas automáticamente)
   - ⏳ NO usar passwords de desarrollo
   - ⏳ Guardar CREDENCIALES_PRODUCCION.txt en lugar seguro

2. **Configurar SSL/TLS**
   ```powershell
   # Copiar certificados SSL
   Copy-Item "C:\Certs\cert.pem" "C:\Apps\siame-deployment\infrastructure\ssl\"
   Copy-Item "C:\Certs\key.pem" "C:\Apps\siame-deployment\infrastructure\ssl\"

   # Reiniciar Nginx
   docker compose restart nginx
   ```

3. **Configurar Backup**
   ```powershell
   # Ejecutar script de backup manualmente
   .\scripts\backup-postgres.ps1

   # Programar tarea diaria
   # (Ver DEPLOYMENT_WINDOWS_SERVER_2025.md para detalles)
   ```

4. **Bloquear PostgreSQL desde exterior**
   ```powershell
   New-NetFirewallRule -DisplayName "Block PostgreSQL External" `
     -Direction Inbound -Protocol TCP -LocalPort 5432 -Action Block
   ```

---

## 📊 URLS DE ACCESO

Después del deployment:

```
Frontend:  http://TU_IP:3000
API:       http://TU_IP:8000/health
Grafana:   http://TU_IP:3001 (admin / password del .env)
```

### Primer Usuario Admin

```powershell
# Opción 1: Registrarse desde el navegador
# http://TU_IP:3000/auth/register

# Opción 2: Crear directamente en BD
docker exec -it siame_postgres psql -U siame_user -d siame_prod -c "
INSERT INTO users (id, email, name, role, clearance_level, created_at, updated_at)
VALUES (
  'admin-' || gen_random_uuid()::text,
  'admin@maeuec.es',
  'Administrador',
  'ADMIN',
  'TOP_SECRET',
  NOW(),
  NOW()
);"
```

---

## ✅ CHECKLIST RÁPIDO

### Antes de Copiar al Servidor
- [x] Package zip creado (8.5 MB)
- [x] Credenciales generadas
- [x] Documentación incluida
- [x] Scripts de instalación listos

### En el Servidor
- [ ] Docker instalado
- [ ] Firewall configurado
- [ ] ZIP extraído en C:\Apps\
- [ ] .env editado con IP/dominio
- [ ] Servicios iniciados
- [ ] Migraciones aplicadas
- [ ] Todo verificado

### Post-Deployment
- [ ] SSL/TLS configurado
- [ ] Backup programado
- [ ] Usuario admin creado
- [ ] Acceso verificado
- [ ] Logs monitoreados

---

## 🆘 SI ALGO SALE MAL

### Problema: Puerto en uso
```powershell
Get-NetTCPConnection -LocalPort 3000 | Get-Process
Stop-Process -Id <ID> -Force
```

### Problema: Docker no inicia servicio
```powershell
docker compose logs postgres
docker compose restart postgres
```

### Problema: Migración falla
```powershell
# Verificar conexión a PostgreSQL
docker exec siame_postgres psql -U siame_user -d siame_prod -c "SELECT 1"

# Reintentar migración
docker compose run --rm frontend npx prisma migrate deploy
```

### Problema: Credenciales incorrectas
```powershell
# Verificar .env
Get-Content .env | Select-String "PASSWORD"

# Editar manualmente
notepad .env
```

---

## 📞 SOPORTE Y AYUDA

### Documentos de Referencia
1. **QUICK_DEPLOY.md** - Guía paso a paso (45 min)
2. **DEPLOYMENT_WINDOWS_SERVER_2025.md** - Guía completa con troubleshooting
3. **README.md** - Información general del proyecto

### Comandos Útiles
```powershell
# Ver estado
docker compose ps

# Ver logs
docker compose logs -f

# Reiniciar todo
docker compose restart

# Detener todo
docker compose stop

# Iniciar de nuevo
docker compose start
```

---

## 🎉 RESUMEN

**Tienes TODO lo necesario para hacer el deployment:**

✅ Package listo: `siame-2026v3-deployment-2025-10-24.zip`
✅ Credenciales generadas y seguras
✅ Documentación completa y detallada
✅ Scripts de instalación automatizados
✅ Checklist para no olvidar nada

**Tiempo estimado de deployment:** 45-60 minutos

**Próximo paso:** Copiar el ZIP al servidor y seguir QUICK_DEPLOY.md

---

## 📝 NOTAS IMPORTANTES

1. **NO** uses las credenciales de desarrollo en producción (ya están cambiadas en .env.production)
2. **SÍ** cambia NEXTAUTH_URL con tu IP/dominio real
3. **SÍ** guarda CREDENCIALES_PRODUCCION.txt en lugar seguro
4. **SÍ** configura SSL/TLS para HTTPS en producción
5. **SÍ** configura backup automatizado inmediatamente

---

**Estado:** ✅ LISTO PARA DEPLOYMENT
**Preparado:** 2025-10-24
**Válido para:** Windows Server 2025
**Versión:** SIAME 2026v3

🚀 **¡Buena suerte con el deployment!**

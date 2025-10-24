# 🚀 QUICK DEPLOY - SIAME 2026v3 a Windows Server 2025

**Tiempo estimado:** 30-45 minutos
**Nivel:** Intermedio

---

## 📋 PRE-REQUISITOS

Antes de empezar, asegúrate de tener:

- [ ] **Acceso RDP** a Windows Server 2025
- [ ] **Permisos de Administrador** en el servidor
- [ ] **IP pública** o dominio configurado
- [ ] **Credenciales de Azure** (tenant, client ID, secrets)
- [ ] **Certificado SSL** (opcional: se puede generar auto-firmado)
- [ ] Este proyecto en un archivo ZIP o acceso al repositorio

---

## 🎯 PASOS RÁPIDOS

### PASO 1: Preparar el Servidor (15 minutos)

#### 1.1. Conectar al Servidor

```powershell
# Desde tu Windows 11
mstsc /v:IP_DEL_SERVIDOR
```

#### 1.2. Instalar Docker

```powershell
# Abrir PowerShell como Administrador

# Habilitar Containers feature
Install-WindowsFeature -Name Containers -Restart

# Después del reinicio, instalar Docker
Invoke-WebRequest -UseBasicParsing `
  "https://raw.githubusercontent.com/microsoft/Windows-Containers/Main/helpful_tools/Install-DockerCE/install-docker-ce.ps1" `
  -o install-docker-ce.ps1
.\install-docker-ce.ps1

# Instalar Docker Compose
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
Invoke-WebRequest `
  "https://github.com/docker/compose/releases/latest/download/docker-compose-Windows-x86_64.exe" `
  -OutFile "$Env:ProgramFiles\Docker\docker-compose.exe"

# Verificar
docker --version
docker compose version
```

---

### PASO 2: Copiar el Proyecto (5 minutos)

#### Opción A: Desde archivo ZIP

```powershell
# Copiar el ZIP al servidor (usa Remote Desktop, WinSCP o similar)
# Luego extraer:

cd C:\
Expand-Archive -Path "C:\Users\Administrator\Downloads\siame-2026v3.zip" -DestinationPath "C:\Apps\"
cd C:\Apps\siame-2026v3
```

#### Opción B: Desde Git

```powershell
cd C:\Apps
git clone https://github.com/tu-org/siame-2026v3.git
cd siame-2026v3
```

---

### PASO 3: Configurar Variables de Entorno (10 minutos)

```powershell
# Copiar template
Copy-Item .env.example .env

# Generar secrets seguros
function New-SecureSecret {
    $bytes = New-Object byte[] 32
    [System.Security.Cryptography.RandomNumberGenerator]::Fill($bytes)
    return [Convert]::ToBase64String($bytes)
}

Write-Host "NEXTAUTH_SECRET=$(New-SecureSecret)"
Write-Host "JWT_SECRET=$(New-SecureSecret)"
Write-Host "SESSION_SECRET=$(New-SecureSecret)"
```

**Editar `.env` con estos valores:**

```powershell
notepad .env
```

**Configuración MÍNIMA requerida:**

```env
# GENERAL
NODE_ENV=production

# BASE DE DATOS
DATABASE_URL="postgresql://siame_user:CAMBIAR_PASSWORD@postgres:5432/siame_prod"
POSTGRES_DB=siame_prod
POSTGRES_USER=siame_user
POSTGRES_PASSWORD=CAMBIAR_PASSWORD_AQUI

# NEXTAUTH (Pegar el generado arriba)
NEXTAUTH_URL="http://TU_IP_O_DOMINIO"
NEXTAUTH_SECRET="PEGAR_SECRET_GENERADO"

# REDIS
REDIS_URL="redis://:CAMBIAR_PASSWORD@redis:6379"
REDIS_PASSWORD=CAMBIAR_PASSWORD_AQUI

# AZURE (Si tienes credenciales, sino dejar mock)
MOCK_AZURE_SERVICES=true
# Si tienes Azure:
# MOCK_AZURE_SERVICES=false
# AZURE_TENANT_ID="tu-tenant-id"
# AZURE_CLIENT_ID="tu-client-id"
# AZURE_CLIENT_SECRET="tu-secret"
```

---

### PASO 4: Configurar Firewall (2 minutos)

```powershell
# Permitir puertos necesarios
New-NetFirewallRule -DisplayName "SIAME - HTTP" -Direction Inbound -Protocol TCP -LocalPort 80 -Action Allow
New-NetFirewallRule -DisplayName "SIAME - HTTPS" -Direction Inbound -Protocol TCP -LocalPort 443 -Action Allow
New-NetFirewallRule -DisplayName "SIAME - Frontend" -Direction Inbound -Protocol TCP -LocalPort 3000 -Action Allow
New-NetFirewallRule -DisplayName "SIAME - API" -Direction Inbound -Protocol TCP -LocalPort 8000 -Action Allow

# Verificar
Get-NetFirewallRule -DisplayName "SIAME*"
```

---

### PASO 5: Iniciar Servicios (5 minutos)

```powershell
cd C:\Apps\siame-2026v3

# 1. Iniciar PostgreSQL y Redis
docker compose up -d postgres redis

# 2. Esperar 15 segundos
Start-Sleep -Seconds 15

# 3. Verificar que estén healthy
docker compose ps

# Deberías ver:
# siame_postgres    Up (healthy)
# siame_redis       Up (healthy)
```

---

### PASO 6: Aplicar Migraciones (3 minutos)

```powershell
# Verificar que las migraciones se aplicaron
docker compose logs postgres | Select-String -Pattern "database system is ready"

# Aplicar migraciones (si tienes Node instalado localmente)
cd src\frontend
npm install
npx prisma migrate deploy

# O desde contenedor
docker compose run --rm frontend npx prisma migrate deploy
```

---

### PASO 7: Iniciar Todos los Servicios (5 minutos)

```powershell
cd C:\Apps\siame-2026v3

# Iniciar todo
docker compose up -d

# Ver logs
docker compose logs -f

# Verificar estado (en otra terminal)
docker compose ps
```

**Todos deben mostrar "Up" o "healthy"**

---

### PASO 8: Verificar Deployment (5 minutos)

#### 8.1. Verificar API Backend

```powershell
# Test health endpoint
Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing

# Deberías ver: {"status":"healthy",...}
```

#### 8.2. Verificar Frontend

```powershell
# Abrir navegador
Start-Process "http://localhost:3000"

# O desde otro PC en la red:
# http://IP_DEL_SERVIDOR:3000
```

#### 8.3. Verificar Base de Datos

```powershell
# Conectar a PostgreSQL
docker exec -it siame_postgres psql -U siame_user -d siame_prod

# Dentro de psql:
# \dt               -- Ver tablas (deben ser 19)
# SELECT COUNT(*) FROM users;
# \q                -- Salir
```

---

## ✅ CHECKLIST FINAL

Marca cada item cuando esté completado:

### Servidor
- [ ] Docker instalado y funcionando
- [ ] Firewall configurado
- [ ] Proyecto copiado a `C:\Apps\siame-2026v3`

### Configuración
- [ ] Archivo `.env` creado y configurado
- [ ] Passwords cambiados (no usar los de ejemplo)
- [ ] NEXTAUTH_SECRET generado
- [ ] URL/IP configurada correctamente

### Servicios
- [ ] PostgreSQL: Up (healthy)
- [ ] Redis: Up (healthy)
- [ ] Orchestrator: Up
- [ ] Frontend: Up (si está en docker-compose)

### Verificación
- [ ] API responde en `/health`
- [ ] Frontend carga en navegador
- [ ] Base de datos tiene 19 tablas
- [ ] No hay errores críticos en logs

---

## 🌐 ACCESO AL SISTEMA

Después del deployment, accede a:

```
Frontend: http://TU_IP_O_DOMINIO:3000
API:      http://TU_IP_O_DOMINIO:8000/health
Grafana:  http://TU_IP_O_DOMINIO:3001 (admin / password del .env)
```

### Primer Usuario Administrador

```powershell
# Opción 1: Desde el navegador
# Ir a: http://TU_IP:3000/auth/register
# Registrar con email: admin@maeuec.es

# Opción 2: Directamente en base de datos
docker exec -it siame_postgres psql -U siame_user -d siame_prod

# En psql:
INSERT INTO users (id, email, name, role, clearance_level, created_at, updated_at)
VALUES (
  'admin-' || gen_random_uuid()::text,
  'admin@maeuec.es',
  'Administrador',
  'ADMIN',
  'TOP_SECRET',
  NOW(),
  NOW()
);
```

---

## 🔧 COMANDOS ÚTILES POST-DEPLOYMENT

### Ver Logs
```powershell
docker compose logs -f
docker compose logs -f postgres
docker compose logs -f orchestrator
```

### Reiniciar Servicios
```powershell
docker compose restart
docker compose restart postgres
```

### Ver Recursos
```powershell
docker stats
```

### Detener Todo
```powershell
docker compose stop
```

### Iniciar de Nuevo
```powershell
docker compose start
```

---

## ⚠️ TROUBLESHOOTING RÁPIDO

### Problema: "Puerto ya en uso"
```powershell
# Ver qué usa el puerto 3000
Get-NetTCPConnection -LocalPort 3000 | Get-Process
# Matar el proceso o cambiar puerto en docker-compose.yml
```

### Problema: "Docker no encuentra imagen"
```powershell
# Pull manual de imágenes
docker pull postgres:15-alpine
docker pull redis:7-alpine
docker compose up -d --build
```

### Problema: "No conecta a PostgreSQL"
```powershell
# Ver logs
docker compose logs postgres
# Reiniciar
docker compose restart postgres
# Verificar .env tiene DATABASE_URL correcto
```

### Problema: "Migración falla"
```powershell
# Entrar al contenedor y migrar manualmente
docker exec -it siame_frontend sh
cd /app
npx prisma migrate deploy
```

---

## 🔒 SEGURIDAD POST-DEPLOYMENT

### CRÍTICO - Hacer INMEDIATAMENTE:

1. **Cambiar TODAS las contraseñas** del `.env`
2. **Bloquear acceso externo a PostgreSQL** (puerto 5432)
3. **Configurar SSL/TLS** para producción
4. **Configurar backup automatizado**

Ver guía completa: `DEPLOYMENT_WINDOWS_SERVER_2025.md`

---

## 📞 SOPORTE

Si algo sale mal:

1. **Ver logs:** `docker compose logs -f`
2. **Verificar .env:** Revisar que no hay typos
3. **Reiniciar:** `docker compose restart`
4. **Consultar guía completa:** `DEPLOYMENT_WINDOWS_SERVER_2025.md`

---

## 🎉 ¡DEPLOYMENT EXITOSO!

Si completaste todos los pasos, tu sistema SIAME 2026v3 ahora está corriendo en Windows Server 2025.

**Próximos pasos:**
1. Configurar certificado SSL
2. Configurar backup automatizado
3. Configurar monitoreo
4. Capacitar usuarios

---

**Versión:** 1.0.0
**Fecha:** 2025-10-24
**Tiempo total:** ~45 minutos

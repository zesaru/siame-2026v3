# 🚀 Guía Completa de Deployment - Windows Server 2025

**SIAME 2026v3** - Sistema Inteligente de Administración y Manejo de Expedientes
**Ministerio de Asuntos Exteriores, Unión Europea y Cooperación**

---

## 📋 Tabla de Contenidos

1. [Requisitos del Sistema](#requisitos-del-sistema)
2. [Instalación de Docker](#instalación-de-docker-en-windows-server-2025)
3. [Configuración del Entorno](#configuración-del-entorno)
4. [Deployment con Docker Compose](#deployment-con-docker-compose)
5. [Configuración de Seguridad](#configuración-de-seguridad)
6. [Backup y Recuperación](#backup-y-recuperación)
7. [Monitoreo](#monitoreo-y-logs)
8. [Troubleshooting](#troubleshooting)

---

## 📦 Requisitos del Sistema

### Hardware Mínimo Recomendado

| Componente | Mínimo | Recomendado |
|------------|--------|-------------|
| CPU | 8 cores | 16 cores (32 threads) |
| RAM | 32 GB | 64 GB |
| Disco | 500 GB SSD | 1 TB NVMe SSD |
| Red | 1 Gbps | 10 Gbps |

### Software Requerido

- ✅ **Windows Server 2025** (Build 26100+)
- ✅ **Docker Desktop** o **Mirantis Container Runtime**
- ✅ **Git para Windows** (opcional)
- ✅ **OpenSSL** (para certificados SSL)
- ✅ **PowerShell 7+** (recomendado)

---

## 🐳 Instalación de Docker en Windows Server 2025

### Opción 1: Docker Desktop (Desarrollo/Testing)

```powershell
# Descargar instalador
Invoke-WebRequest -Uri "https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe" `
  -OutFile "$env:TEMP\DockerDesktopInstaller.exe"

# Instalar
Start-Process -FilePath "$env:TEMP\DockerDesktopInstaller.exe" `
  -ArgumentList "install --quiet" -Wait

# Iniciar servicio
Start-Service com.docker.service

# Verificar
docker --version
docker compose version
```

### Opción 2: Mirantis Container Runtime (Producción - RECOMENDADO)

```powershell
# 1. Habilitar feature de Containers
Install-WindowsFeature -Name Containers -Restart

# 2. Después del reinicio, instalar Docker Engine
Invoke-WebRequest -UseBasicParsing `
  "https://raw.githubusercontent.com/microsoft/Windows-Containers/Main/helpful_tools/Install-DockerCE/install-docker-ce.ps1" `
  -o install-docker-ce.ps1

.\install-docker-ce.ps1

# 3. Instalar Docker Compose
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
Invoke-WebRequest `
  "https://github.com/docker/compose/releases/latest/download/docker-compose-Windows-x86_64.exe" `
  -OutFile "$Env:ProgramFiles\Docker\docker-compose.exe"

# Verificar instalación
docker --version
docker compose version
```

### Configurar Docker para Producción

```powershell
# Crear directorio de configuración
New-Item -ItemType Directory -Path "C:\ProgramData\Docker\config" -Force

# Crear daemon.json optimizado
$daemonConfig = @"
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "5"
  },
  "storage-driver": "windowsfilter",
  "dns": ["8.8.8.8", "8.8.4.4"],
  "experimental": false,
  "metrics-addr": "0.0.0.0:9323",
  "max-concurrent-downloads": 10,
  "max-concurrent-uploads": 5
}
"@

$daemonConfig | Out-File -FilePath "C:\ProgramData\Docker\config\daemon.json" -Encoding utf8

# Reiniciar Docker
Restart-Service docker
```

---

## ⚙️ Configuración del Entorno

### 1. Preparar Directorio del Proyecto

```powershell
# Crear directorio principal
New-Item -ItemType Directory -Path "C:\Apps\siame-2026v3" -Force
cd C:\Apps\siame-2026v3

# Clonar repositorio (si aplica)
git clone https://github.com/tu-org/siame-2026v3.git .

# O copiar archivos desde backup/zip
```

### 2. Configurar Variables de Entorno (.env)

```powershell
# Copiar template
Copy-Item .env.example .env

# Editar con valores de producción
notepad .env
```

**Configuración CRÍTICA en `.env`:**

```env
#============================================
# CONFIGURACIÓN DE PRODUCCIÓN
#============================================
NODE_ENV=production
LOG_LEVEL=info
PORT=3000

#============================================
# BASE DE DATOS
#============================================
DATABASE_URL="postgresql://siame_user:TU_PASSWORD_SEGURO@postgres:5432/siame_prod"
POSTGRES_DB=siame_prod
POSTGRES_USER=siame_user
POSTGRES_PASSWORD=TU_PASSWORD_SEGURO_AQUI

#============================================
# NEXTAUTH (GENERAR NUEVO SECRET)
#============================================
NEXTAUTH_URL="https://siame.maeuec.es"
NEXTAUTH_SECRET="GENERAR_CON_OPENSSL_ABAJO"

#============================================
# REDIS
#============================================
REDIS_URL="redis://:TU_REDIS_PASSWORD@redis:6379"
REDIS_PASSWORD=TU_REDIS_PASSWORD_AQUI

#============================================
# AZURE SERVICIOS (Credenciales reales)
#============================================
AZURE_TENANT_ID="tu-tenant-id-real"
AZURE_CLIENT_ID="tu-client-id-real"
AZURE_CLIENT_SECRET="tu-client-secret-real"
AZURE_FORM_RECOGNIZER_ENDPOINT="https://tu-form-recognizer.cognitiveservices.azure.com/"
AZURE_FORM_RECOGNIZER_KEY="tu-api-key-real"
AZURE_STORAGE_CONNECTION_STRING="DefaultEndpointsProtocol=https;AccountName=..."
AZURE_KEY_VAULT_URL="https://tu-keyvault.vault.azure.net/"

#============================================
# SEGURIDAD
#============================================
SECURITY_LEVEL=ENS_ALTO
ENABLE_AUDIT_LOGGING=true
ENABLE_ENCRYPTION=true
MOCK_AZURE_SERVICES=false
ENABLE_WATERMARKING=true

#============================================
# CORS Y DOMINIOS
#============================================
CORS_ORIGINS="https://siame.maeuec.es"
ALLOWED_DOMAINS="siame.maeuec.es,*.maeuec.es"
```

### 3. Generar Secrets Seguros

```powershell
# Función helper para generar secrets
function New-SecureSecret {
    param([int]$Length = 32)
    $bytes = New-Object byte[] $Length
    [System.Security.Cryptography.RandomNumberGenerator]::Fill($bytes)
    return [Convert]::ToBase64String($bytes)
}

# Generar y mostrar secrets
Write-Host "`n=== GENERAR ESTOS SECRETS Y AGREGARLOS AL .env ===" -ForegroundColor Green
Write-Host "`nNEXTAUTH_SECRET=" -NoNewline
New-SecureSecret
Write-Host "`nJWT_SECRET=" -NoNewline
New-SecureSecret
Write-Host "`nENCRYPTION_KEY=" -NoNewline
-join ((48..57) + (65..90) + (97..122) | Get-Random -Count 32 | % {[char]$_})
Write-Host "`n"
```

---

## 🚀 Deployment con Docker Compose

### 1. Validar Configuración

```powershell
# Verificar sintaxis de docker-compose.yml
docker compose config

# Si hay errores, revisar archivo
```

### 2. Iniciar Servicios Base (PostgreSQL + Redis)

```powershell
# Levantar solo base de datos y caché
docker compose up -d postgres redis

# Esperar a que estén saludables (10-15 segundos)
Start-Sleep -Seconds 15

# Verificar estado
docker compose ps
```

**Salida esperada:**
```
NAME              STATUS          PORTS
siame_postgres    Up (healthy)    0.0.0.0:5432->5432/tcp
siame_redis       Up (healthy)    0.0.0.0:6379->6379/tcp
```

### 3. Aplicar Migraciones de Base de Datos

```powershell
# Opción A: Desde contenedor frontend (si ya está built)
docker compose run --rm frontend npx prisma migrate deploy

# Opción B: Localmente (requiere Node.js)
cd src\frontend
npm install
npx prisma migrate deploy
cd ..\..
```

### 4. Verificar Tablas Creadas

```powershell
docker exec siame_postgres psql -U siame_user -d siame_prod -c "\dt"
```

**Debe mostrar 19 tablas:**
- users, accounts, sessions, verification_tokens
- documents, file_uploads, document_authorizations, document_workflows
- hojas_remision, guias_valija, valijas_internas, items_valija, precintos
- workflows, workflow_steps
- notifications, audit_logs, system_config
- _prisma_migrations

### 5. Levantar Todos los Servicios

```powershell
# Iniciar stack completo
docker compose up -d

# Ver logs en tiempo real
docker compose logs -f

# Verificar todos los servicios
docker compose ps
```

### 6. Verificar Health de Servicios

```powershell
# PostgreSQL
docker exec siame_postgres pg_isready -U siame_user

# Redis
docker exec siame_redis redis-cli -a $env:REDIS_PASSWORD ping

# Orchestrator API
Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing

# Frontend
Invoke-WebRequest -Uri "http://localhost:3000" -UseBasicParsing
```

---

## 🔒 Configuración de Seguridad

### 1. Firewall de Windows Server

```powershell
# Crear reglas de firewall
New-NetFirewallRule -DisplayName "SIAME - HTTP" `
  -Direction Inbound -Protocol TCP -LocalPort 80 -Action Allow

New-NetFirewallRule -DisplayName "SIAME - HTTPS" `
  -Direction Inbound -Protocol TCP -LocalPort 443 -Action Allow

# Bloquear PostgreSQL desde exterior
New-NetFirewallRule -DisplayName "SIAME - Block PostgreSQL External" `
  -Direction Inbound -Protocol TCP -LocalPort 5432 `
  -Action Block -RemoteAddress Any

# Permitir PostgreSQL solo localhost
New-NetFirewallRule -DisplayName "SIAME - Allow PostgreSQL Local" `
  -Direction Inbound -Protocol TCP -LocalPort 5432 `
  -Action Allow -RemoteAddress 127.0.0.1,::1

# Verificar reglas
Get-NetFirewallRule -DisplayName "SIAME*"
```

### 2. Certificados SSL/TLS

#### Generar Certificado Auto-Firmado (Testing)

```powershell
# Crear directorio SSL
New-Item -ItemType Directory -Path ".\infrastructure\ssl" -Force

# Generar certificado auto-firmado
$cert = New-SelfSignedCertificate `
  -DnsName "siame.maeuec.es", "*.maeuec.es" `
  -CertStoreLocation "cert:\LocalMachine\My" `
  -NotAfter (Get-Date).AddYears(3) `
  -KeyExportPolicy Exportable

# Exportar
$certPassword = ConvertTo-SecureString -String "TuPassword123!" -Force -AsPlainText
Export-PfxCertificate -Cert $cert `
  -FilePath ".\infrastructure\ssl\siame.pfx" `
  -Password $certPassword

# Convertir a PEM (requiere OpenSSL)
openssl pkcs12 -in .\infrastructure\ssl\siame.pfx `
  -out .\infrastructure\ssl\cert.pem -nodes
openssl pkcs12 -in .\infrastructure\ssl\siame.pfx `
  -out .\infrastructure\ssl\key.pem -nodes -nocerts
```

#### Usar Certificado Real (Producción)

```powershell
# Copiar certificados reales del proveedor
Copy-Item "C:\Certs\siame.crt" ".\infrastructure\ssl\cert.pem"
Copy-Item "C:\Certs\siame.key" ".\infrastructure\ssl\key.pem"
Copy-Item "C:\Certs\ca-bundle.crt" ".\infrastructure\ssl\ca-bundle.pem"

# Establecer permisos restrictivos
$acl = Get-Acl ".\infrastructure\ssl\key.pem"
$acl.SetAccessRuleProtection($true, $false)
$acl.Access | ForEach-Object { $acl.RemoveAccessRule($_) }
$rule = New-Object System.Security.AccessControl.FileSystemAccessRule(
    "Administrators", "FullControl", "Allow"
)
$acl.AddAccessRule($rule)
Set-Acl ".\infrastructure\ssl\key.pem" $acl
```

### 3. Configurar Nginx para HTTPS

Crear `infrastructure/nginx/conf.d/siame.conf`:

```nginx
# Redirigir HTTP a HTTPS
server {
    listen 80;
    server_name siame.maeuec.es;
    return 301 https://$server_name$request_uri;
}

# Servidor HTTPS principal
server {
    listen 443 ssl http2;
    server_name siame.maeuec.es;

    # Certificados SSL
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;

    # Configuración SSL moderna
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256';
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;

    # Frontend Next.js
    location / {
        proxy_pass http://frontend:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300;
        proxy_connect_timeout 300;
    }

    # API Backend
    location /api/ {
        proxy_pass http://orchestrator:8000/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300;
    }

    # Logs
    access_log /var/log/nginx/siame_access.log;
    error_log /var/log/nginx/siame_error.log warn;
}
```

Reiniciar Nginx:

```powershell
docker compose restart nginx
```

---

## 💾 Backup y Recuperación

### Script de Backup Automatizado

Crear `scripts/backup-postgres.ps1`:

```powershell
#Requires -RunAsAdministrator

# Configuración
$BACKUP_DIR = "D:\Backups\SIAME\PostgreSQL"
$DATE = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$RETENTION_DAYS = 30
$DB_NAME = "siame_prod"
$DB_USER = "siame_user"

# Crear directorio
New-Item -ItemType Directory -Path $BACKUP_DIR -Force | Out-Null

Write-Host "=== Backup PostgreSQL SIAME ===" -ForegroundColor Green
Write-Host "Fecha: $(Get-Date)" -ForegroundColor Cyan
Write-Host "Base de datos: $DB_NAME" -ForegroundColor Cyan

# Realizar backup
Write-Host "`nCreando backup..." -ForegroundColor Yellow
docker exec siame_postgres pg_dump -U $DB_USER $DB_NAME > "$BACKUP_DIR\${DB_NAME}_$DATE.sql"

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Backup SQL creado" -ForegroundColor Green

    # Comprimir
    Write-Host "Comprimiendo backup..." -ForegroundColor Yellow
    Compress-Archive -Path "$BACKUP_DIR\${DB_NAME}_$DATE.sql" `
      -DestinationPath "$BACKUP_DIR\${DB_NAME}_$DATE.zip" -Force
    Remove-Item "$BACKUP_DIR\${DB_NAME}_$DATE.sql"

    $backupSize = (Get-Item "$BACKUP_DIR\${DB_NAME}_$DATE.zip").Length / 1MB
    Write-Host "✓ Backup comprimido: $([math]::Round($backupSize, 2)) MB" -ForegroundColor Green

    # Limpiar backups antiguos
    Write-Host "`nLimpiando backups antiguos..." -ForegroundColor Yellow
    $deleted = Get-ChildItem -Path $BACKUP_DIR -Filter "*.zip" |
        Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-$RETENTION_DAYS) } |
        Remove-Item -Force -PassThru

    Write-Host "✓ Eliminados $($deleted.Count) backups antiguos" -ForegroundColor Green
    Write-Host "`n=== Backup completado exitosamente ===" -ForegroundColor Green
} else {
    Write-Host "✗ Error al crear backup" -ForegroundColor Red
    exit 1
}
```

### Programar Backup Diario

```powershell
# Crear tarea programada para backup diario a las 2:00 AM
$action = New-ScheduledTaskAction `
  -Execute "PowerShell.exe" `
  -Argument "-NoProfile -ExecutionPolicy Bypass -File C:\Apps\siame-2026v3\scripts\backup-postgres.ps1"

$trigger = New-ScheduledTaskTrigger -Daily -At 2am

$principal = New-ScheduledTaskPrincipal `
  -UserId "SYSTEM" `
  -LogonType ServiceAccount `
  -RunLevel Highest

Register-ScheduledTask `
  -Action $action `
  -Trigger $trigger `
  -Principal $principal `
  -TaskName "SIAME PostgreSQL Backup Diario" `
  -Description "Backup automático diario de la base de datos SIAME" `
  -Force

# Verificar tarea creada
Get-ScheduledTask -TaskName "SIAME PostgreSQL Backup Diario"
```

### Restaurar desde Backup

```powershell
# Restaurar backup específico
$BACKUP_FILE = "D:\Backups\SIAME\PostgreSQL\siame_prod_2025-10-24_02-00-00.zip"

# Descomprimir
Expand-Archive -Path $BACKUP_FILE -DestinationPath "$env:TEMP\siame_restore" -Force

# Restaurar
$sqlFile = Get-ChildItem "$env:TEMP\siame_restore\*.sql" | Select-Object -First 1
Get-Content $sqlFile.FullName | docker exec -i siame_postgres psql -U siame_user -d siame_prod

# Limpiar
Remove-Item "$env:TEMP\siame_restore" -Recurse -Force
```

---

## 📊 Monitoreo y Logs

### Acceso a Servicios de Monitoreo

**Grafana** (Dashboard de métricas):
```
URL: https://siame.maeuec.es:3001
Usuario: admin
Password: (configurado en .env)
```

**Prometheus** (Recolector de métricas):
```
URL: http://localhost:9090
```

### Ver Logs de Contenedores

```powershell
# Todos los servicios
docker compose logs -f

# Servicio específico
docker compose logs -f frontend
docker compose logs -f orchestrator
docker compose logs -f postgres

# Últimas N líneas
docker compose logs --tail=100 postgres

# Desde una fecha específica
docker compose logs --since="2025-10-24T00:00:00" frontend
```

### Exportar Logs de Auditoría

```powershell
# Exportar logs de los últimos 7 días a CSV
$outputFile = "audit_logs_$(Get-Date -Format 'yyyy-MM-dd').csv"
docker exec siame_postgres psql -U siame_user -d siame_prod -c `
  "COPY (SELECT * FROM audit_logs WHERE created_at >= NOW() - INTERVAL '7 days' ORDER BY created_at DESC) TO STDOUT WITH CSV HEADER" `
  > $outputFile

Write-Host "Logs exportados a: $outputFile"
```

---

## 🔧 Troubleshooting

### Problema: Contenedor no inicia

```powershell
# Ver logs detallados del contenedor
docker compose logs frontend

# Ver último error
docker compose logs --tail=50 frontend

# Reiniciar contenedor específico
docker compose restart frontend

# Recrear contenedor
docker compose up -d --force-recreate frontend
```

### Problema: No conecta a PostgreSQL

```powershell
# Verificar que PostgreSQL esté corriendo
docker compose ps postgres

# Probar conexión
docker exec siame_postgres psql -U siame_user -d siame_prod -c "SELECT version();"

# Ver logs de PostgreSQL
docker compose logs postgres

# Verificar red
docker network inspect siame-2026v3_siame_network
```

### Problema: Puerto ya en uso

```powershell
# Ver qué proceso usa el puerto
Get-NetTCPConnection -LocalPort 3000 |
  Select-Object -Property OwningProcess |
  Get-Process

# Matar proceso
Stop-Process -Id <PROCESS_ID> -Force
```

### Resetear Sistema Completo (⚠️ BORRA TODOS LOS DATOS)

```powershell
# Detener todos los servicios
docker compose down -v

# Limpiar imágenes y volúmenes
docker system prune -a --volumes -f

# Volver a iniciar
docker compose up -d
```

---

## ✅ Checklist de Deployment

### Pre-Deployment

- [ ] Windows Server 2025 actualizado
- [ ] Docker instalado y funcionando (`docker --version`)
- [ ] Archivo `.env` configurado con valores de producción
- [ ] Secrets generados (NEXTAUTH_SECRET, JWT_SECRET, etc.)
- [ ] Certificados SSL copiados a `infrastructure/ssl/`
- [ ] Firewall configurado
- [ ] Credenciales de Azure verificadas
- [ ] DNS apuntando al servidor

### Durante Deployment

- [ ] `docker compose up -d postgres redis`
- [ ] Verificar: `docker compose ps` (ambos "healthy")
- [ ] Aplicar migraciones: `npx prisma migrate deploy`
- [ ] Verificar tablas: 19 tablas creadas
- [ ] `docker compose up -d` (todos los servicios)
- [ ] Verificar: todos los contenedores "Up" o "healthy"
- [ ] Test frontend: `Invoke-WebRequest http://localhost:3000`
- [ ] Test API: `Invoke-WebRequest http://localhost:8000/health`

### Post-Deployment

- [ ] Crear usuario administrador inicial
- [ ] Configurar backup automatizado
- [ ] Configurar monitoreo (Grafana)
- [ ] Verificar logs de auditoría
- [ ] Documentar credenciales en KeePass/Vault
- [ ] Pruebas de carga básicas
- [ ] Plan de rollback documentado

---

## 📞 Comandos Rápidos de Referencia

```powershell
# ===== GESTIÓN DE SERVICIOS =====
docker compose up -d                    # Iniciar todos
docker compose stop                     # Detener todos
docker compose restart                  # Reiniciar todos
docker compose down                     # Eliminar (mantiene datos)
docker compose down -v                  # Eliminar TODO (⚠️ borra datos)
docker compose ps                       # Ver estado
docker stats                            # Ver recursos

# ===== LOGS =====
docker compose logs -f                  # Todos en tiempo real
docker compose logs -f frontend         # Uno específico
docker compose logs --tail=100 postgres # Últimas 100 líneas

# ===== BASE DE DATOS =====
docker exec -it siame_postgres psql -U siame_user -d siame_prod
docker exec siame_postgres pg_dump -U siame_user siame_prod > backup.sql

# ===== REDIS =====
docker exec -it siame_redis redis-cli -a TU_PASSWORD

# ===== ACTUALIZACIÓN =====
docker compose pull                     # Descargar nuevas imágenes
docker compose up -d --build           # Rebuild y restart
```

---

## 📖 Recursos Adicionales

- **Documentación Docker:** https://docs.docker.com/
- **Prisma Docs:** https://www.prisma.io/docs
- **Next.js Deployment:** https://nextjs.org/docs/deployment
- **Windows Server Containers:** https://learn.microsoft.com/en-us/virtualization/windowscontainers/

---

**Versión:** 1.0.0
**Fecha:** 2025-10-24
**Autor:** Equipo SIAME
**Sistema:** SIAME 2026v3 para Windows Server 2025

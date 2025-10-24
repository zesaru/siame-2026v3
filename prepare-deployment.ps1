# SIAME 2026v3 - Script de Preparación para Deployment
# Este script prepara el proyecto para ser desplegado en Windows Server 2025

param(
    [switch]$SkipTests,
    [switch]$IncludeNodeModules,
    [string]$OutputPath = ".\siame-deployment"
)

Write-Host @"
╔════════════════════════════════════════════════════════╗
║   SIAME 2026v3 - Preparación para Deployment         ║
║   Windows Server 2025                                  ║
╚════════════════════════════════════════════════════════╝
"@ -ForegroundColor Cyan

$ErrorActionPreference = "Stop"

# Funciones auxiliares
function Write-Step {
    param([string]$Message)
    Write-Host "`n► $Message" -ForegroundColor Yellow
}

function Write-Success {
    param([string]$Message)
    Write-Host "  ✓ $Message" -ForegroundColor Green
}

function Write-Info {
    param([string]$Message)
    Write-Host "  ℹ $Message" -ForegroundColor Cyan
}

function Write-Warning {
    param([string]$Message)
    Write-Host "  ⚠ $Message" -ForegroundColor Yellow
}

# ===== PASO 1: Validación =====
Write-Step "Validando entorno..."

# Verificar que estamos en el directorio correcto
if (-not (Test-Path "docker-compose.yml")) {
    Write-Error "No se encontró docker-compose.yml. Ejecuta este script desde la raíz del proyecto."
}
Write-Success "Directorio del proyecto validado"

# Verificar Docker
try {
    docker --version | Out-Null
    Write-Success "Docker instalado"
} catch {
    Write-Warning "Docker no encontrado. Necesitarás instalarlo en el servidor."
}

# ===== PASO 2: Limpiar archivos innecesarios =====
Write-Step "Limpiando archivos de desarrollo..."

$filesToRemove = @(
    ".git",
    ".vscode",
    "node_modules",
    ".next",
    "__pycache__",
    "*.log",
    ".env.local",
    ".env.development",
    "tmp",
    "temp",
    "coverage"
)

$itemsRemoved = 0
foreach ($pattern in $filesToRemove) {
    if (-not $IncludeNodeModules -and $pattern -eq "node_modules") {
        $found = Get-ChildItem -Path . -Filter $pattern -Recurse -Directory -ErrorAction SilentlyContinue
        foreach ($item in $found) {
            Remove-Item $item.FullName -Recurse -Force -ErrorAction SilentlyContinue
            $itemsRemoved++
        }
    }
}
Write-Success "Archivos de desarrollo limpiados ($itemsRemoved items)"

# ===== PASO 3: Validar archivos esenciales =====
Write-Step "Validando archivos esenciales..."

$essentialFiles = @(
    "docker-compose.yml",
    ".env.example",
    "src/frontend/prisma/schema.prisma",
    "orchestrator/requirements.txt"
)

$missingFiles = @()
foreach ($file in $essentialFiles) {
    if (Test-Path $file) {
        Write-Success $file
    } else {
        $missingFiles += $file
        Write-Warning "Falta: $file"
    }
}

if ($missingFiles.Count -gt 0) {
    Write-Error "Faltan archivos esenciales. Revisa el proyecto."
}

# ===== PASO 4: Generar credenciales de producción =====
Write-Step "Generando credenciales de producción..."

function New-SecurePassword {
    param([int]$Length = 16)
    $chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*"
    -join ((1..$Length) | ForEach-Object { $chars[(Get-Random -Maximum $chars.Length)] })
}

function New-SecureSecret {
    param([int]$Length = 32)
    $bytes = New-Object byte[] $Length
    [System.Security.Cryptography.RandomNumberGenerator]::Fill($bytes)
    return [Convert]::ToBase64String($bytes)
}

$credentials = @{
    "POSTGRES_PASSWORD" = New-SecurePassword -Length 20
    "REDIS_PASSWORD" = New-SecurePassword -Length 20
    "NEXTAUTH_SECRET" = New-SecureSecret
    "JWT_SECRET" = New-SecureSecret
    "SESSION_SECRET" = New-SecureSecret
    "ENCRYPTION_KEY" = -join ((48..57) + (65..90) + (97..122) | Get-Random -Count 32 | ForEach-Object {[char]$_})
}

Write-Success "Credenciales generadas"

# ===== PASO 5: Crear archivo .env.production =====
Write-Step "Creando .env.production..."

if (Test-Path ".env.example") {
    $envContent = Get-Content ".env.example" -Raw

    # Reemplazar valores
    $envContent = $envContent -replace 'NODE_ENV=development', 'NODE_ENV=production'
    $envContent = $envContent -replace 'siame_password', $credentials["POSTGRES_PASSWORD"]
    $envContent = $envContent -replace 'siame_redis_password', $credentials["REDIS_PASSWORD"]
    $envContent = $envContent -replace 'tu-secret-muy-seguro-cambiame-en-produccion', $credentials["NEXTAUTH_SECRET"]
    $envContent = $envContent -replace 'tu-jwt-secret-muy-seguro', $credentials["JWT_SECRET"]
    $envContent = $envContent -replace 'tu-session-secret', $credentials["SESSION_SECRET"]
    $envContent = $envContent -replace 'tu-encryption-key-32-caracteres', $credentials["ENCRYPTION_KEY"]
    $envContent = $envContent -replace 'siame_dev', 'siame_prod'
    $envContent = $envContent -replace 'MOCK_AZURE_SERVICES=false', 'MOCK_AZURE_SERVICES=true'

    $envContent | Out-File -FilePath ".env.production" -Encoding utf8
    Write-Success ".env.production creado"

    # Guardar credenciales en archivo seguro
    $credentialsFile = "CREDENCIALES_PRODUCCION.txt"
    @"
╔════════════════════════════════════════════════════════╗
║   SIAME 2026v3 - CREDENCIALES DE PRODUCCIÓN          ║
║   GUARDAR EN LUGAR SEGURO - NO COMPARTIR             ║
╚════════════════════════════════════════════════════════╝

Generadas: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")

IMPORTANTE: Estas credenciales deben ser guardadas en un
gestor de contraseñas (KeePass, Azure Key Vault, etc.)

═══════════════════════════════════════════════════════════

POSTGRES_PASSWORD:
$($credentials["POSTGRES_PASSWORD"])

REDIS_PASSWORD:
$($credentials["REDIS_PASSWORD"])

NEXTAUTH_SECRET:
$($credentials["NEXTAUTH_SECRET"])

JWT_SECRET:
$($credentials["JWT_SECRET"])

SESSION_SECRET:
$($credentials["SESSION_SECRET"])

ENCRYPTION_KEY:
$($credentials["ENCRYPTION_KEY"])

═══════════════════════════════════════════════════════════

NOTA: Estas credenciales YA están en .env.production
Solo guarda este archivo en lugar seguro como respaldo.

═══════════════════════════════════════════════════════════
"@ | Out-File -FilePath $credentialsFile -Encoding utf8

    Write-Success "Credenciales guardadas en: $credentialsFile"
    Write-Warning "¡IMPORTANTE! Guarda $credentialsFile en un lugar seguro"
} else {
    Write-Error "No se encontró .env.example"
}

# ===== PASO 6: Crear estructura de deployment =====
Write-Step "Creando estructura de deployment..."

# Crear directorio temporal
if (Test-Path $OutputPath) {
    Remove-Item $OutputPath -Recurse -Force
}
New-Item -ItemType Directory -Path $OutputPath -Force | Out-Null

# Copiar archivos esenciales
$filesToCopy = @(
    "docker-compose.yml",
    ".env.production",
    ".env.example",
    "package.json",
    "Makefile",
    "README.md",
    "DEPLOYMENT_WINDOWS_SERVER_2025.md",
    "QUICK_DEPLOY.md"
)

foreach ($file in $filesToCopy) {
    if (Test-Path $file) {
        Copy-Item $file -Destination $OutputPath
        Write-Success "Copiado: $file"
    }
}

# Copiar directorios
$directoriesToCopy = @(
    "src",
    "orchestrator",
    "agents",
    "config",
    "infrastructure",
    "shared",
    "scripts",
    "docs"
)

foreach ($dir in $directoriesToCopy) {
    if (Test-Path $dir) {
        Copy-Item $dir -Destination $OutputPath -Recurse -Force
        Write-Success "Copiado: $dir"
    }
}

Write-Success "Estructura de deployment creada en: $OutputPath"

# ===== PASO 7: Crear script de instalación para el servidor =====
Write-Step "Creando script de instalación automática..."

$installScript = @"
# SIAME 2026v3 - Script de Instalación Automática
# Windows Server 2025
# Ejecutar como Administrador

Write-Host "╔════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   SIAME 2026v3 - Instalación Automática              ║" -ForegroundColor Cyan
Write-Host "║   Windows Server 2025                                 ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════╝" -ForegroundColor Cyan

`$ErrorActionPreference = "Stop"

# Paso 1: Verificar permisos
if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Error "Este script debe ejecutarse como Administrador"
}

# Paso 2: Verificar Docker
Write-Host "`n► Verificando Docker..." -ForegroundColor Yellow
try {
    docker --version | Out-Null
    docker compose version | Out-Null
    Write-Host "  ✓ Docker instalado" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Docker no encontrado" -ForegroundColor Red
    Write-Host "`nPara instalar Docker, ejecuta:" -ForegroundColor Yellow
    Write-Host "  Install-WindowsFeature -Name Containers -Restart" -ForegroundColor Cyan
    Write-Host "  # Después del reinicio:" -ForegroundColor Cyan
    Write-Host "  Invoke-WebRequest 'https://raw.githubusercontent.com/microsoft/Windows-Containers/Main/helpful_tools/Install-DockerCE/install-docker-ce.ps1' -o install-docker-ce.ps1" -ForegroundColor Cyan
    Write-Host "  .\install-docker-ce.ps1" -ForegroundColor Cyan
    exit 1
}

# Paso 3: Crear directorio de aplicación
Write-Host "`n► Creando directorio de aplicación..." -ForegroundColor Yellow
`$appDir = "C:\Apps\siame-2026v3"
if (-not (Test-Path `$appDir)) {
    New-Item -ItemType Directory -Path `$appDir -Force | Out-Null
}
Write-Host "  ✓ Directorio: `$appDir" -ForegroundColor Green

# Paso 4: Copiar archivos
Write-Host "`n► Copiando archivos..." -ForegroundColor Yellow
Copy-Item -Path ".\*" -Destination `$appDir -Recurse -Force
Write-Host "  ✓ Archivos copiados" -ForegroundColor Green

# Paso 5: Configurar .env
Write-Host "`n► Configurando variables de entorno..." -ForegroundColor Yellow
Set-Location `$appDir
if (Test-Path ".env.production") {
    Copy-Item ".env.production" ".env" -Force
    Write-Host "  ✓ .env configurado" -ForegroundColor Green
} else {
    Write-Warning "No se encontró .env.production. Copia .env.example manualmente."
}

# Paso 6: Configurar firewall
Write-Host "`n► Configurando firewall..." -ForegroundColor Yellow
New-NetFirewallRule -DisplayName "SIAME - HTTP" -Direction Inbound -Protocol TCP -LocalPort 80 -Action Allow -ErrorAction SilentlyContinue
New-NetFirewallRule -DisplayName "SIAME - HTTPS" -Direction Inbound -Protocol TCP -LocalPort 443 -Action Allow -ErrorAction SilentlyContinue
New-NetFirewallRule -DisplayName "SIAME - Frontend" -Direction Inbound -Protocol TCP -LocalPort 3000 -Action Allow -ErrorAction SilentlyContinue
New-NetFirewallRule -DisplayName "SIAME - API" -Direction Inbound -Protocol TCP -LocalPort 8000 -Action Allow -ErrorAction SilentlyContinue
Write-Host "  ✓ Firewall configurado" -ForegroundColor Green

# Paso 7: Iniciar servicios
Write-Host "`n► Iniciando servicios..." -ForegroundColor Yellow
docker compose up -d postgres redis
Write-Host "  ✓ PostgreSQL y Redis iniciados" -ForegroundColor Green

Start-Sleep -Seconds 15

# Paso 8: Verificar servicios
Write-Host "`n► Verificando servicios..." -ForegroundColor Yellow
docker compose ps

Write-Host "`n╔════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║   Instalación base completada                         ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════╝" -ForegroundColor Green

Write-Host "`nPróximos pasos:" -ForegroundColor Cyan
Write-Host "1. Editar C:\Apps\siame-2026v3\.env con tu IP/dominio" -ForegroundColor White
Write-Host "2. Ejecutar: docker compose up -d" -ForegroundColor White
Write-Host "3. Aplicar migraciones: docker compose run --rm frontend npx prisma migrate deploy" -ForegroundColor White
Write-Host "4. Acceder a: http://localhost:3000" -ForegroundColor White
"@

$installScript | Out-File -FilePath "$OutputPath\INSTALL.ps1" -Encoding utf8
Write-Success "Script de instalación creado: INSTALL.ps1"

# ===== PASO 8: Crear checklist =====
Write-Step "Creando checklist de deployment..."

$checklistContent = @"
# ✅ CHECKLIST DE DEPLOYMENT - SIAME 2026v3

## PRE-DEPLOYMENT

### Servidor
- [ ] Windows Server 2025 instalado y actualizado
- [ ] Acceso RDP funcionando
- [ ] Permisos de Administrador
- [ ] IP pública o dominio configurado
- [ ] Puertos 80, 443, 3000, 8000 disponibles

### Credenciales y Certificados
- [ ] Credenciales de producción generadas
- [ ] Archivo CREDENCIALES_PRODUCCION.txt guardado en lugar seguro
- [ ] Certificado SSL obtenido (o preparado para generar auto-firmado)
- [ ] Credenciales de Azure (si aplica)

### Archivos
- [ ] Package de deployment preparado
- [ ] .env.production configurado con IP/dominio real
- [ ] QUICK_DEPLOY.md revisado

## DEPLOYMENT

### Instalación Base
- [ ] Docker instalado en el servidor
- [ ] Docker Compose instalado
- [ ] Proyecto copiado a C:\Apps\siame-2026v3
- [ ] Firewall configurado

### Configuración
- [ ] .env.production copiado a .env
- [ ] NEXTAUTH_URL configurado con dominio real
- [ ] Passwords cambiados (no usar los de desarrollo)
- [ ] MOCK_AZURE_SERVICES=true (o credenciales Azure reales)

### Servicios
- [ ] PostgreSQL iniciado y healthy
- [ ] Redis iniciado y healthy
- [ ] Migraciones aplicadas (19 tablas creadas)
- [ ] Orchestrator iniciado
- [ ] Frontend iniciado (si aplica)

### Verificación
- [ ] API responde: http://IP:8000/health
- [ ] Frontend carga: http://IP:3000
- [ ] PostgreSQL responde
- [ ] Redis responde
- [ ] No hay errores en logs

## POST-DEPLOYMENT

### Seguridad
- [ ] Certificado SSL configurado
- [ ] HTTPS funcionando
- [ ] Firewall bloqueando PostgreSQL desde exterior
- [ ] Acceso SSH/RDP limitado por IP
- [ ] Credenciales guardadas en gestor de contraseñas

### Datos
- [ ] Usuario administrador creado
- [ ] Backup automatizado configurado
- [ ] Script de backup probado
- [ ] Restauración de backup probada

### Monitoreo
- [ ] Grafana accesible
- [ ] Prometheus recolectando métricas
- [ ] Logs funcionando
- [ ] Alertas configuradas (opcional)

### Documentación
- [ ] Credenciales documentadas
- [ ] IPs y dominios documentados
- [ ] Procedimientos de backup documentados
- [ ] Plan de rollback documentado
- [ ] Contactos de soporte documentados

## TESTING POST-DEPLOYMENT

### Funcionalidad
- [ ] Login funciona
- [ ] Registro de usuarios funciona
- [ ] Creación de documentos funciona
- [ ] Upload de archivos funciona
- [ ] Navegación completa probada

### Performance
- [ ] Tiempo de carga < 3 segundos
- [ ] Sin errores de timeout
- [ ] Base de datos responde rápido

### Seguridad
- [ ] HTTPS obligatorio
- [ ] Headers de seguridad presentes
- [ ] Acceso no autorizado bloqueado
- [ ] Logs de auditoría funcionando

## ROLLBACK (Si algo falla)

- [ ] Backup de datos disponible
- [ ] docker compose down
- [ ] Restaurar backup si es necesario
- [ ] Investigar logs: docker compose logs
- [ ] Consultar DEPLOYMENT_WINDOWS_SERVER_2025.md

---

**Completado por:** _______________
**Fecha:** _______________
**Firma:** _______________
"@

$checklistContent | Out-File -FilePath "$OutputPath\DEPLOYMENT_CHECKLIST.md" -Encoding utf8
Write-Success "Checklist creado: DEPLOYMENT_CHECKLIST.md"

# ===== PASO 9: Crear archivo comprimido =====
Write-Step "Creando archivo comprimido..."

$zipFile = "siame-2026v3-deployment-$(Get-Date -Format 'yyyy-MM-dd').zip"
Compress-Archive -Path "$OutputPath\*" -DestinationPath $zipFile -Force

$zipSize = (Get-Item $zipFile).Length / 1MB
Write-Success "Archivo creado: $zipFile ($([math]::Round($zipSize, 2)) MB)"

# ===== RESUMEN FINAL =====
Write-Host "`n" -NoNewline
Write-Host "╔════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║   PREPARACIÓN COMPLETADA                              ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════╝" -ForegroundColor Green

Write-Host "`nArchivos generados:" -ForegroundColor Cyan
Write-Host "  📦 $zipFile" -ForegroundColor White
Write-Host "  📁 $OutputPath\" -ForegroundColor White
Write-Host "  🔐 CREDENCIALES_PRODUCCION.txt" -ForegroundColor Yellow

Write-Host "`nPróximos pasos:" -ForegroundColor Cyan
Write-Host "  1. Copia $zipFile al servidor Windows Server 2025" -ForegroundColor White
Write-Host "  2. Extrae el archivo en C:\Apps\" -ForegroundColor White
Write-Host "  3. Lee QUICK_DEPLOY.md" -ForegroundColor White
Write-Host "  4. Ejecuta INSTALL.ps1 como Administrador" -ForegroundColor White

Write-Host "`n⚠️  IMPORTANTE:" -ForegroundColor Yellow
Write-Host "  - Guarda CREDENCIALES_PRODUCCION.txt en un lugar seguro" -ForegroundColor White
Write-Host "  - NO compartas las credenciales" -ForegroundColor White
Write-Host "  - Configura NEXTAUTH_URL con tu IP/dominio real" -ForegroundColor White

Write-Host "`n✅ Todo listo para deployment!" -ForegroundColor Green

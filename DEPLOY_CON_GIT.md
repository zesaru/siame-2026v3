# 🚀 Deployment con Git - SIAME 2026v3

**La forma MÁS FÁCIL y profesional de hacer deployment**

---

## ✅ POR QUÉ GIT ES MEJOR

| Característica | Con Git | Con ZIP |
|----------------|---------|---------|
| Velocidad | ⚡ Rápido (solo cambios) | 🐌 Lento (todo el archivo) |
| Actualizaciones | `git pull` | Copiar ZIP completo |
| Historial | ✅ Completo | ❌ No existe |
| Rollback | `git checkout` | Restaurar backup |
| Tamaño | 📦 Pequeño (incremental) | 📦 Grande (siempre 8+ MB) |
| Colaboración | ✅ Múltiples devs | ❌ Manual |

---

## 🎯 DEPLOYMENT CON GIT (15 MINUTOS)

### PREPARACIÓN (Una sola vez)

#### 1. En tu máquina de desarrollo (Windows 11 + WSL2)

```bash
cd /mnt/c/Users/embto/Documents/GitHub/siame-2026v3

# Verificar estado
git status

# Agregar todos los archivos (excepto los del .gitignore)
git add .

# Hacer commit inicial
git commit -m "Initial commit: SIAME 2026v3 ready for deployment"

# Subir a GitHub/GitLab/Azure DevOps
git remote add origin https://github.com/TU_USUARIO/siame-2026v3.git
git push -u origin main
```

#### 2. En el Servidor Windows Server 2025

```powershell
# Instalar Git para Windows (si no está)
winget install --id Git.Git -e --source winget

# O descargar desde: https://git-scm.com/download/win

# Verificar instalación
git --version
```

---

## 🚀 DEPLOYMENT INICIAL (Primera vez)

### En el Servidor Windows Server 2025:

```powershell
# 1. Clonar el repositorio
cd C:\Apps
git clone https://github.com/TU_USUARIO/siame-2026v3.git
cd siame-2026v3

# 2. Copiar .env.example a .env
Copy-Item .env.example .env

# 3. Editar .env con valores de producción
notepad .env
```

**En el `.env`, configurar:**

```env
# IMPORTANTE: Cambiar estos valores
NODE_ENV=production

# Tu dominio o IP
NEXTAUTH_URL="http://TU_IP_O_DOMINIO:3000"

# Generar secrets seguros (ver abajo cómo)
NEXTAUTH_SECRET="GENERAR_CON_COMANDO_ABAJO"
POSTGRES_PASSWORD="GENERAR_PASSWORD_SEGURO"
REDIS_PASSWORD="GENERAR_PASSWORD_SEGURO"

# Azure (si tienes credenciales)
MOCK_AZURE_SERVICES=true  # o false si tienes Azure
```

**Generar secrets seguros:**

```powershell
# Generar NEXTAUTH_SECRET
[Convert]::ToBase64String([System.Security.Cryptography.RandomNumberGenerator]::GetBytes(32))

# Generar passwords
-join ((48..57) + (65..90) + (97..122) | Get-Random -Count 20 | % {[char]$_})
```

```powershell
# 4. Instalar Docker (si no está)
Install-WindowsFeature -Name Containers -Restart

# Después del reinicio:
Invoke-WebRequest -UseBasicParsing `
  "https://raw.githubusercontent.com/microsoft/Windows-Containers/Main/helpful_tools/Install-DockerCE/install-docker-ce.ps1" `
  -o install-docker-ce.ps1
.\install-docker-ce.ps1

# 5. Configurar firewall
New-NetFirewallRule -DisplayName "SIAME - HTTP" -Direction Inbound -Protocol TCP -LocalPort 80 -Action Allow
New-NetFirewallRule -DisplayName "SIAME - HTTPS" -Direction Inbound -Protocol TCP -LocalPort 443 -Action Allow
New-NetFirewallRule -DisplayName "SIAME - Frontend" -Direction Inbound -Protocol TCP -LocalPort 3000 -Action Allow
New-NetFirewallRule -DisplayName "SIAME - API" -Direction Inbound -Protocol TCP -LocalPort 8000 -Action Allow

# 6. Iniciar servicios
docker compose up -d postgres redis

# Esperar 15 segundos
Start-Sleep -Seconds 15

# 7. Verificar servicios
docker compose ps

# 8. Aplicar migraciones
docker compose run --rm frontend npx prisma migrate deploy

# 9. Iniciar todos los servicios
docker compose up -d

# 10. Verificar
docker compose ps
Invoke-WebRequest http://localhost:8000/health
Start-Process http://localhost:3000
```

---

## 🔄 ACTUALIZACIONES (Después de la primera vez)

**¡ESTO ES LO MÁS FÁCIL!**

### En tu máquina de desarrollo:

```bash
# 1. Hacer cambios en el código
# 2. Commit
git add .
git commit -m "feat: nueva funcionalidad"

# 3. Push
git push origin main
```

### En el Servidor:

```powershell
cd C:\Apps\siame-2026v3

# 1. Pull de cambios (¡Solo esto!)
git pull origin main

# 2. Si hay cambios en dependencias, reinstalar
docker compose build

# 3. Si hay cambios en BD, aplicar migraciones
docker compose run --rm frontend npx prisma migrate deploy

# 4. Reiniciar servicios
docker compose restart

# ¡Listo! Actualización completa
```

---

## 📋 CHECKLIST RÁPIDO

### Primera Vez (Setup)
- [ ] Git instalado en el servidor
- [ ] Repositorio clonado a `C:\Apps\siame-2026v3`
- [ ] `.env` creado y configurado
- [ ] Docker instalado
- [ ] Firewall configurado
- [ ] Servicios iniciados
- [ ] Migraciones aplicadas
- [ ] Todo funcionando

### Actualizaciones (Siempre)
- [ ] `git pull` en el servidor
- [ ] `docker compose restart`
- [ ] Verificar que todo funciona

---

## 🔐 SEGURIDAD CON GIT

### ⚠️ NUNCA Subir al Repositorio:

- ❌ `.env` (solo `.env.example`)
- ❌ `CREDENCIALES_PRODUCCION.txt`
- ❌ Certificados SSL (`.pem`, `.key`)
- ❌ Datos de usuarios
- ❌ Passwords reales

### ✅ SÍ Subir:

- ✅ Código fuente
- ✅ `docker-compose.yml`
- ✅ `.env.example` (con valores de ejemplo)
- ✅ Documentación
- ✅ Scripts de instalación

**Ya está configurado en `.gitignore`** ✅

---

## 🎯 COMANDOS ÚTILES DE GIT

### En Desarrollo:

```bash
# Ver estado
git status

# Ver cambios
git diff

# Agregar cambios
git add .

# Commit
git commit -m "descripción"

# Push
git push origin main

# Ver historial
git log --oneline
```

### En Servidor:

```powershell
# Pull cambios
git pull origin main

# Ver versión actual
git log -1

# Ver cambios que se van a aplicar (antes de pull)
git fetch
git log HEAD..origin/main --oneline

# Rollback a versión anterior (si algo falla)
git log --oneline  # Ver commits
git checkout <commit-hash>
docker compose restart
```

---

## 🌟 WORKFLOWS RECOMENDADOS

### Desarrollo → Producción Simple

```
Desarrollo (Windows 11 WSL2)
    ↓ git push
GitHub/GitLab/Azure DevOps
    ↓ git pull
Producción (Windows Server 2025)
```

### Desarrollo → Staging → Producción (Avanzado)

```
Desarrollo (branch: develop)
    ↓ git push
Staging Server (branch: develop)
    ↓ git merge → main
Producción (branch: main)
```

---

## 🆘 TROUBLESHOOTING

### Problema: Conflictos al hacer pull

```powershell
# Ver qué archivos tienen conflicto
git status

# Opción 1: Mantener cambios del servidor
git stash
git pull
git stash pop

# Opción 2: Sobrescribir con cambios del repositorio
git reset --hard origin/main
git pull
```

### Problema: Olvidé configurar .env y ya hice pull

```powershell
# El .env NO se sobrescribe porque está en .gitignore
# Está seguro, solo verifica:
cat .env
```

### Problema: Quiero volver a versión anterior

```powershell
# Ver historial
git log --oneline

# Volver a commit específico
git checkout <commit-hash>

# O crear branch desde ese punto
git checkout -b rollback-<fecha> <commit-hash>

# Reiniciar servicios
docker compose restart
```

---

## 📊 COMPARACIÓN: Git vs ZIP

### Primer Deployment:

| Método | Tiempo | Comandos |
|--------|--------|----------|
| ZIP | 15 min | Copiar ZIP, extraer, configurar |
| Git | 10 min | git clone, configurar .env |

### Actualización:

| Método | Tiempo | Comandos |
|--------|--------|----------|
| ZIP | 15 min | Copiar ZIP, extraer, sobrescribir |
| **Git** | **2 min** | **git pull, docker compose restart** |

**¡Git es 7x más rápido en actualizaciones!**

---

## 🎓 EJEMPLO COMPLETO PASO A PASO

### 1. Primera vez (Setup inicial)

**En desarrollo:**
```bash
cd /mnt/c/Users/embto/Documents/GitHub/siame-2026v3
git add .
git commit -m "Initial deployment"
git remote add origin https://github.com/maeuec/siame-2026v3.git
git push -u origin main
```

**En servidor:**
```powershell
cd C:\Apps
git clone https://github.com/maeuec/siame-2026v3.git
cd siame-2026v3
Copy-Item .env.example .env
notepad .env  # Configurar
docker compose up -d postgres redis
Start-Sleep -Seconds 15
docker compose run --rm frontend npx prisma migrate deploy
docker compose up -d
```

### 2. Actualización (después de hacer cambios)

**En desarrollo:**
```bash
# Hiciste cambios en el código
git add .
git commit -m "feat: nuevo módulo de reportes"
git push
```

**En servidor:**
```powershell
cd C:\Apps\siame-2026v3
git pull
docker compose restart
# ¡Listo!
```

---

## ✅ VENTAJAS ADICIONALES DE GIT

1. **Historial completo** - Puedes ver quién cambió qué y cuándo
2. **Rollback fácil** - Vuelve a cualquier versión anterior
3. **Branches** - Prueba features sin afectar producción
4. **Colaboración** - Múltiples desarrolladores trabajando
5. **CI/CD** - Automatiza deployment con GitHub Actions
6. **Auditoría** - Cumplimiento ENS Alto
7. **Backup** - El repositorio es un backup automático

---

## 🚀 PRÓXIMOS PASOS

### Ahora:

1. **Hacer commit inicial** del proyecto
2. **Subir a GitHub/GitLab/Azure DevOps**
3. **Clonar en el servidor**
4. **Configurar y desplegar**

### Después:

1. Configurar **branch protegidos** (main)
2. Implementar **Pull Requests** para code review
3. Configurar **GitHub Actions** para CI/CD
4. Automatizar **tests** antes de deployment

---

## 📞 COMANDOS RÁPIDOS DE REFERENCIA

```powershell
# DESARROLLO
git add .
git commit -m "mensaje"
git push

# SERVIDOR (Primera vez)
git clone https://github.com/TU_REPO/siame-2026v3.git
Copy-Item .env.example .env
docker compose up -d

# SERVIDOR (Actualizaciones)
git pull
docker compose restart
```

---

## 🎉 RESUMEN

**Git hace el deployment:**
- ✅ **Más rápido** (2 min vs 15 min)
- ✅ **Más seguro** (historial y rollback)
- ✅ **Más profesional** (industria estándar)
- ✅ **Más fácil** (un solo comando: `git pull`)

**Próximo paso:**
```bash
git add .
git commit -m "Initial commit"
git push
```

---

**Versión:** 1.0.0
**Fecha:** 2025-10-24
**Método:** Git (Recomendado ⭐)

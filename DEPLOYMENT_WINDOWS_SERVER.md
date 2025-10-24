# 🚀 Despliegue en Windows Server 2019 - SIAME 2026v3

## 📋 SITUACIÓN ACTUAL

### Entorno de Desarrollo (Ahora)
- **Sistema**: Windows 11 con WSL2
- **Propósito**: Desarrollo y pruebas
- **Instalación**: PostgreSQL, Redis en WSL2

### Entorno de Producción (Objetivo)
- **Sistema**: Windows Server 2019
- **Propósito**: Aplicación en producción
- **Instalación**: Diferente estrategia

---

## 🎯 OPCIONES DE DESPLIEGUE EN WINDOWS SERVER 2019

### OPCIÓN 1: Docker en Windows Server (RECOMENDADA) ⭐

**Ventajas:**
- ✅ Mismo entorno dev → prod
- ✅ Fácil actualización
- ✅ Aislamiento de servicios
- ✅ Escalabilidad
- ✅ Ya tienes `docker-compose.yml` listo

**Requisitos:**
- Windows Server 2019 con Containers feature
- Docker Desktop para Windows Server
- O Docker Engine directamente

**Instalación:**
```powershell
# En Windows Server 2019
# Habilitar containers
Install-WindowsFeature -Name Containers

# Instalar Docker
Install-Module -Name DockerMsftProvider -Force
Install-Package -Name docker -ProviderName DockerMsftProvider -Force

# Reiniciar
Restart-Computer
```

**Despliegue:**
```powershell
cd C:\siame-2026v3
docker-compose -f docker-compose.yml up -d
```

---

### OPCIÓN 2: Servicios Nativos en Windows Server

**Ventajas:**
- ✅ Sin dependencia de Docker
- ✅ Integración nativa con Windows
- ✅ Rendimiento directo

**Componentes a instalar:**
1. PostgreSQL 15 para Windows
2. Redis para Windows
3. Python 3.12 para Windows
4. Node.js 20 LTS para Windows
5. IIS como reverse proxy (opcional)

**Instalación:**

#### 1. PostgreSQL
```powershell
# Descargar desde:
# https://www.postgresql.org/download/windows/

# Instalar con:
# - Puerto: 5432
# - Usuario: postgres
# - Password: [tu_password_seguro]
```

#### 2. Redis
```powershell
# Opción A: Redis para Windows (Memurai)
# https://www.memurai.com/

# Opción B: Redis en WSL2 (no recomendado para producción)
```

#### 3. Python
```powershell
# Descargar Python 3.12 desde:
# https://www.python.org/downloads/windows/

# Instalar con "Add to PATH"
```

#### 4. Node.js
```powershell
# Descargar Node.js 20 LTS desde:
# https://nodejs.org/

# Instalar versión LTS
```

---

### OPCIÓN 3: Híbrido (Docker + Servicios Nativos)

**Configuración:**
- Frontend Next.js → IIS o como servicio Windows
- Orchestrator Python → Servicio Windows
- PostgreSQL → Nativo Windows
- Redis → Docker o Memurai

---

## 🔧 CONFIGURACIÓN RECOMENDADA

### Para Desarrollo (Tu Windows 11 actual)
```
WSL2 Ubuntu
├── PostgreSQL (desarrollo)
├── Redis (desarrollo)
├── Python venv
└── Next.js dev server
```

**Ejecutar:**
```bash
# En WSL2
./INSTALL_ONE_COMMAND.sh  # Instala en WSL2
./run-migrations.sh
./start-dev.sh
```

### Para Producción (Windows Server 2019)
```
Windows Server 2019
├── Docker Containers
│   ├── PostgreSQL 15
│   ├── Redis 7
│   ├── Orchestrator
│   ├── Frontend Next.js
│   └── Nginx
└── Configuración
    ├── Firewall rules
    ├── SSL certificates
    └── Backups automáticos
```

**Ejecutar:**
```powershell
# En PowerShell (Windows Server)
docker-compose -f docker-compose.prod.yml up -d
```

---

## 📊 COMPARACIÓN DE OPCIONES

| Característica | Docker | Nativo | Híbrido |
|----------------|--------|--------|---------|
| Facilidad setup | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| Rendimiento | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Mantenimiento | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| Escalabilidad | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| Costo | Gratis | Gratis | Gratis |

---

## 🎯 MI RECOMENDACIÓN

### Ahora (Desarrollo en Windows 11)
```bash
# Usar WSL2 para desarrollo
./INSTALL_ONE_COMMAND.sh
```

**Beneficios:**
- Desarrollo rápido
- Mismo entorno que Linux
- Fácil de probar

### Luego (Producción en Windows Server 2019)
```powershell
# Usar Docker en Windows Server
docker-compose up -d
```

**Beneficios:**
- Fácil migración desde dev
- Mismos contenedores
- Configuración ya lista en `docker-compose.yml`

---

## 📝 PASOS SUGERIDOS

### Fase 1: Desarrollo (Ahora - Windows 11 WSL2)
1. ✅ Instalar en WSL2
2. ✅ Desarrollar features
3. ✅ Probar todo localmente
4. ✅ Preparar para producción

### Fase 2: Pre-Producción (Preparar)
1. Configurar Windows Server 2019
2. Instalar Docker
3. Transferir código
4. Ajustar variables de entorno

### Fase 3: Producción (Desplegar)
1. Copiar proyecto a Windows Server
2. Ajustar `docker-compose.prod.yml`
3. Ejecutar `docker-compose up -d`
4. Configurar SSL, firewall, backups

---

## 🔐 CONSIDERACIONES DE SEGURIDAD

### Desarrollo (WSL2)
- Credenciales simples OK
- Sin SSL necesario
- Firewall local

### Producción (Windows Server)
- ⚠️ Cambiar TODAS las credenciales
- ✅ Usar SSL/TLS
- ✅ Configurar firewall
- ✅ Backups automáticos
- ✅ Logs de auditoría
- ✅ Monitoreo

---

## 📂 ARCHIVOS DE CONFIGURACIÓN

### Desarrollo (`.env.local`)
```env
DATABASE_URL=postgresql://siame_user:siame_password@localhost:5432/siame_dev
REDIS_URL=redis://localhost:6379
NODE_ENV=development
```

### Producción (`.env.production`)
```env
DATABASE_URL=postgresql://siame_prod:STRONG_PASSWORD@db-server:5432/siame_prod
REDIS_URL=redis://:STRONG_PASSWORD@redis-server:6379
NODE_ENV=production
NEXTAUTH_URL=https://siame.tu-dominio.es
```

---

## 🚀 INSTALACIÓN EN WINDOWS SERVER 2019

### Opción A: Con Docker (Paso a paso)

#### 1. Preparar Windows Server
```powershell
# Habilitar Hyper-V
Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V -All

# Habilitar Containers
Install-WindowsFeature -Name Containers

# Reiniciar
Restart-Computer
```

#### 2. Instalar Docker
```powershell
# Descargar Docker Desktop para Windows Server
# O usar Docker Engine directamente

# Verificar
docker --version
docker-compose --version
```

#### 3. Copiar Proyecto
```powershell
# Copiar desde repositorio o transferir archivos
git clone https://github.com/tu-org/siame-2026v3.git C:\siame-2026v3
cd C:\siame-2026v3
```

#### 4. Configurar Producción
```powershell
# Copiar y editar .env
copy .env.example .env.production
notepad .env.production
```

#### 5. Desplegar
```powershell
docker-compose -f docker-compose.yml up -d
```

### Opción B: Sin Docker (Servicios nativos)

Ver documentación detallada en: `WINDOWS_SERVER_NATIVE.md` (a crear)

---

## 💡 RESPUESTA A TU PREGUNTA

### ¿Dónde instalar ahora?

**Respuesta:** En WSL2 (tu Windows 11)

**Razones:**
1. Es para **desarrollo**
2. Más rápido y fácil
3. Mejor experiencia de desarrollo
4. No afecta tu Windows Server 2019

### ¿Cómo llevar a Windows Server 2019?

**Respuesta:** Usar Docker

**Razones:**
1. Ya tienes `docker-compose.yml` listo
2. Mismo entorno dev → prod
3. Fácil de mantener
4. Escalable

---

## 📞 PRÓXIMOS PASOS

### Ahora (Desarrollo)
```bash
# En WSL2 (tu Windows 11)
./INSTALL_ONE_COMMAND.sh
```

### Después (cuando estés listo para producción)
Te ayudaré a:
1. Configurar Docker en Windows Server 2019
2. Migrar la aplicación
3. Configurar seguridad
4. Hacer el despliegue

---

## ❓ FAQ

**P: ¿Puedo desarrollar en WSL2 y desplegar en Windows Server?**
R: ¡Sí! Es lo más común y recomendado.

**P: ¿El código funcionará igual en WSL2 que en Windows Server?**
R: Sí, si usas Docker en ambos. El código es el mismo.

**P: ¿Necesito instalar nada en Windows Server ahora?**
R: No, primero desarrolla en WSL2. Luego configuramos Windows Server.

**P: ¿WSL2 en Windows Server 2019?**
R: Windows Server 2019 no tiene WSL2. Usarás Docker o servicios nativos.

---

**Conclusión:** Desarrolla en WSL2 ahora, despliega en Docker en Windows Server después.

---

_¿Más preguntas sobre el despliegue?_

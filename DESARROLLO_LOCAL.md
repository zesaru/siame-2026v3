# 🚀 Guía de Desarrollo Local - SIAME 2026v3

Esta guía te ayudará a configurar y ejecutar SIAME 2026v3 en tu Mac (o cualquier sistema con Docker).

---

## ✅ Prerrequisitos

- **Docker Desktop** instalado y funcionando
- **Git** instalado
- **Node.js 18+** (opcional, solo si quieres desarrollo sin Docker)
- **Python 3.11+** (opcional, solo si quieres desarrollo sin Docker)

---

## 🎯 Inicio Rápido (5 minutos)

### 1. Verificar Docker

```bash
docker --version
docker compose version
```

### 2. Configurar Variables de Entorno

El archivo `.env` ya está creado. Edítalo si necesitas cambiar algo:

```bash
# Editar variables de entorno
nano .env

# O con VS Code
code .env
```

**IMPORTANTE para desarrollo local:** Por defecto está configurado con:
- PostgreSQL en puerto 5432
- Redis en puerto 6379
- Backend en puerto 8000
- Frontend en puerto 3000
- Nginx en puerto 80

### 3. Iniciar Servicios

```bash
# Iniciar solo base de datos y cache (para desarrollo rápido)
docker compose up -d postgres redis

# Esperar 10 segundos a que estén saludables
sleep 10

# Verificar que están corriendo
docker compose ps
```

### 4. Aplicar Migraciones de Base de Datos

```bash
# Desde el directorio del frontend
cd src/frontend

# Instalar dependencias (primera vez)
npm install

# Aplicar migraciones
npx prisma migrate dev

# Volver al directorio raíz
cd ../..
```

### 5. Iniciar Todos los Servicios

```bash
# Iniciar todo el stack
docker compose up -d

# Ver logs en tiempo real
docker compose logs -f
```

### 6. Acceder a la Aplicación

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **Documentación API:** http://localhost:8000/docs
- **Grafana:** http://localhost:3001 (usuario: `admin`, password: `siame_grafana_password`)
- **Prometheus:** http://localhost:9090

---

## 🛠️ Comandos Útiles

### Gestión de Servicios

```bash
# Ver estado de todos los servicios
docker compose ps

# Ver logs de un servicio específico
docker compose logs -f frontend
docker compose logs -f orchestrator
docker compose logs -f postgres

# Reiniciar un servicio
docker compose restart frontend

# Detener todos los servicios
docker compose stop

# Detener y eliminar contenedores (mantiene datos)
docker compose down

# Detener y eliminar TODO (⚠️ borra la base de datos)
docker compose down -v
```

### Base de Datos

```bash
# Conectar a PostgreSQL
docker exec -it siame_postgres psql -U siame_user -d siame_dev

# Ver tablas
docker exec siame_postgres psql -U siame_user -d siame_dev -c "\dt"

# Hacer backup
docker exec siame_postgres pg_dump -U siame_user siame_dev > backup_$(date +%Y%m%d).sql

# Restaurar backup
cat backup_20251025.sql | docker exec -i siame_postgres psql -U siame_user -d siame_dev
```

### Redis

```bash
# Conectar a Redis
docker exec -it siame_redis redis-cli -a siame_redis_password

# Ver todas las keys
KEYS *

# Limpiar cache
FLUSHALL
```

### Desarrollo del Frontend

```bash
cd src/frontend

# Instalar dependencias
npm install

# Desarrollo local (sin Docker, conecta a DB en Docker)
npm run dev

# Build de producción
npm run build

# Regenerar cliente Prisma
npx prisma generate

# Ver base de datos en Prisma Studio
npx prisma studio
```

### Desarrollo del Backend

```bash
cd orchestrator

# Crear virtual environment
python -m venv venv
source venv/bin/activate  # En Mac/Linux

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar orchestrator localmente
uvicorn api:app --reload --port 8000
```

---

## 🔧 Desarrollo Sin Docker (Opcional)

Si prefieres desarrollar sin Docker:

### 1. Instalar PostgreSQL localmente

```bash
# En Mac con Homebrew
brew install postgresql@15
brew services start postgresql@15

# Crear base de datos
createdb siame_dev
```

### 2. Instalar Redis localmente

```bash
# En Mac con Homebrew
brew install redis
brew services start redis
```

### 3. Actualizar .env

```env
DATABASE_URL="postgresql://tu_usuario@localhost:5432/siame_dev"
REDIS_URL="redis://localhost:6379"
```

### 4. Ejecutar servicios

```bash
# Terminal 1 - Backend
cd orchestrator
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn api:app --reload

# Terminal 2 - Frontend
cd src/frontend
npm install
npm run dev
```

---

## 🐛 Troubleshooting

### Puerto ya en uso

```bash
# Ver qué proceso usa el puerto 3000
lsof -i :3000

# Matar el proceso
kill -9 <PID>
```

### Contenedor no inicia

```bash
# Ver logs detallados
docker compose logs --tail=100 frontend

# Recrear contenedor
docker compose up -d --force-recreate frontend

# Rebuild de imagen
docker compose build --no-cache frontend
docker compose up -d frontend
```

### Error de permisos en volúmenes

```bash
# Dar permisos a directorios
chmod -R 755 src/
chmod -R 755 config/
```

### Base de datos no conecta

```bash
# Verificar que PostgreSQL esté corriendo
docker compose ps postgres

# Ver logs de PostgreSQL
docker compose logs postgres

# Reiniciar PostgreSQL
docker compose restart postgres

# Verificar conexión
docker exec siame_postgres pg_isready -U siame_user
```

### Frontend no compila

```bash
cd src/frontend

# Limpiar y reinstalar
rm -rf node_modules .next
npm install
npm run build
```

### Reset completo (⚠️ BORRA TODO)

```bash
# Detener y eliminar todo
docker compose down -v

# Limpiar sistema Docker
docker system prune -a --volumes -f

# Volver a iniciar desde cero
docker compose up -d postgres redis
# ... seguir pasos de inicio rápido
```

---

## 📝 Variables de Entorno Importantes

Para desarrollo local, estas son las variables críticas en `.env`:

```env
# Modo de desarrollo
NODE_ENV=development
DEBUG_MODE=true

# Base de datos (dentro de Docker)
DATABASE_URL="postgresql://siame_user:siame_password@localhost:5432/siame_dev"

# Redis (dentro de Docker)
REDIS_URL="redis://:siame_redis_password@localhost:6379"

# NextAuth (genera un secret nuevo con: openssl rand -base64 32)
NEXTAUTH_URL="http://localhost:3000"
NEXTAUTH_SECRET="tu-secret-generado"

# Azure (para desarrollo puedes usar MOCK)
MOCK_AZURE_SERVICES=true
MOCK_EMAIL_SERVICE=true
```

---

## 🧪 Testing

```bash
# Tests del frontend
cd src/frontend
npm test

# Tests del backend
cd orchestrator
pytest

# Tests de integración
docker compose -f docker-compose.test.yml up
```

---

## 📚 Recursos Adicionales

- **Documentación del Proyecto:** Ver `README.md`
- **Deployment a Producción:** Ver `DEPLOYMENT_WINDOWS_SERVER_2025.md`
- **Arquitectura:** Ver `docs/PROJECT_CONTEXT.md`
- **Estado Actual:** Ver `ESTADO_ACTUAL.md`

---

## 🆘 Ayuda

Si tienes problemas:

1. Revisa los logs: `docker compose logs -f`
2. Verifica que Docker esté corriendo
3. Asegúrate de que los puertos no estén ocupados
4. Revisa que `.env` esté configurado correctamente
5. Intenta un reset limpio (ver sección Troubleshooting)

---

**¡Feliz desarrollo!** 🎉

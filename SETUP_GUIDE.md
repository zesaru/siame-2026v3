# 🚀 Guía de Instalación de Servicios - SIAME 2026v3

**Fecha**: 2025-10-22
**Estado del Schema**: ✅ Validado correctamente

---

## ✅ ESTADO ACTUAL

- ✅ Schema de Prisma completado y validado
- ✅ Dependencias Node.js instaladas (423 paquetes)
- ✅ Python 3.12.3 disponible
- ⚠️ **PENDIENTE**: PostgreSQL, Redis, pip

---

## 📋 OPCIÓN 1: Instalación Rápida con Docker Desktop (RECOMENDADO)

### Paso 1: Habilitar WSL2 Integration en Docker Desktop

1. Abrir Docker Desktop en Windows
2. Ir a **Settings** → **Resources** → **WSL Integration**
3. Habilitar **Enable integration with my default WSL distro**
4. Activar el toggle para tu distribución Ubuntu
5. Hacer clic en **Apply & Restart**

### Paso 2: Verificar Docker en WSL

```bash
# Abrir tu terminal WSL y ejecutar:
docker --version
docker compose version
```

### Paso 3: Levantar Servicios

```bash
cd /mnt/c/Users/embto/Documents/GitHub/siame-2026v3
docker compose up -d postgres redis
```

### Paso 4: Verificar Servicios

```bash
# Ver estado
docker compose ps

# Ver logs
docker compose logs postgres
docker compose logs redis

# Verificar conexión a PostgreSQL
docker compose exec postgres psql -U siame_user -d siame_dev -c "SELECT version();"
```

---

## 📋 OPCIÓN 2: Instalación Nativa en WSL2

### Paso 1: Actualizar Sistema

```bash
sudo apt update
sudo apt upgrade -y
```

### Paso 2: Instalar pip

```bash
sudo apt install python3-pip python3-venv -y

# Verificar instalación
python3 --version
pip3 --version
```

### Paso 3: Instalar PostgreSQL

```bash
# Instalar PostgreSQL
sudo apt install postgresql postgresql-contrib -y

# Iniciar servicio
sudo service postgresql start

# Configurar PostgreSQL
sudo -u postgres psql << EOF
CREATE USER siame_user WITH PASSWORD 'siame_password';
CREATE DATABASE siame_dev OWNER siame_user;
GRANT ALL PRIVILEGES ON DATABASE siame_dev TO siame_user;
ALTER USER siame_user CREATEDB;
\q
EOF

# Verificar conexión
psql -U siame_user -d siame_dev -h localhost -c "SELECT version();"
```

### Paso 4: Instalar Redis

```bash
# Instalar Redis
sudo apt install redis-server -y

# Iniciar servicio
sudo service redis-server start

# Verificar
redis-cli ping
# Debería responder: PONG
```

### Paso 5: Configurar Inicio Automático (Opcional)

```bash
# Agregar al final de tu .bashrc o .zshrc
cat >> ~/.bashrc << 'EOF'

# Auto-iniciar servicios PostgreSQL y Redis
if service postgresql status 2>&1 | grep -q "is not running"; then
    sudo service postgresql start > /dev/null 2>&1
fi

if service redis-server status 2>&1 | grep -q "is not running"; then
    sudo service redis-server start > /dev/null 2>&1
fi
EOF

source ~/.bashrc
```

---

## 🐍 CONFIGURACIÓN DE PYTHON

### Paso 1: Crear Entorno Virtual

```bash
cd /mnt/c/Users/embto/Documents/GitHub/siame-2026v3/orchestrator
python3 -m venv venv
```

### Paso 2: Activar Entorno Virtual

```bash
source venv/bin/activate
# Tu prompt debería cambiar a mostrar (venv)
```

### Paso 3: Instalar Dependencias

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Paso 4: Verificar Instalación

```bash
pip list
```

---

## 🗄️ CONFIGURACIÓN DE BASE DE DATOS

### Paso 1: Verificar Variables de Entorno

```bash
cd /mnt/c/Users/embto/Documents/GitHub/siame-2026v3/src/frontend

# Verificar que existe .env
cat .env
```

Si no existe, copiar desde ejemplo:
```bash
cp .env.example .env
# Editar según tu configuración
nano .env
```

### Paso 2: Verificar Conexión

```bash
cd /mnt/c/Users/embto/Documents/GitHub/siame-2026v3/src/frontend
npx prisma db pull --force
```

### Paso 3: Aplicar Migraciones

```bash
npx prisma migrate dev --name initial_setup
```

### Paso 4: Generar Cliente Prisma

```bash
npx prisma generate
```

### Paso 5: Abrir Prisma Studio (Opcional)

```bash
npx prisma studio
# Se abrirá en http://localhost:5555
```

---

## ✅ VERIFICACIÓN FINAL

### Script de Verificación Completa

```bash
#!/bin/bash

echo "🔍 Verificando instalación de SIAME 2026v3..."
echo ""

# Python
echo "✓ Python:"
python3 --version

# pip
echo "✓ pip:"
pip3 --version

# Node.js
echo "✓ Node.js:"
node --version

# npm
echo "✓ npm:"
npm --version

# PostgreSQL
echo "✓ PostgreSQL:"
if command -v psql &> /dev/null; then
    psql -U siame_user -d siame_dev -h localhost -c "SELECT 'Conectado correctamente' as status;" 2>&1 | grep -q "Conectado" && echo "PostgreSQL: ✅ Funcionando" || echo "PostgreSQL: ❌ Error de conexión"
else
    docker compose exec postgres psql -U siame_user -d siame_dev -c "SELECT 'Conectado correctamente' as status;" 2>&1 | grep -q "Conectado" && echo "PostgreSQL (Docker): ✅ Funcionando" || echo "PostgreSQL: ❌ No disponible"
fi

# Redis
echo "✓ Redis:"
if command -v redis-cli &> /dev/null; then
    redis-cli ping 2>&1 | grep -q "PONG" && echo "Redis: ✅ Funcionando" || echo "Redis: ❌ Error"
else
    docker compose exec redis redis-cli ping 2>&1 | grep -q "PONG" && echo "Redis (Docker): ✅ Funcionando" || echo "Redis: ❌ No disponible"
fi

# Prisma
echo "✓ Prisma:"
cd /mnt/c/Users/embto/Documents/GitHub/siame-2026v3/src/frontend && npx prisma validate 2>&1 | grep -q "valid" && echo "Prisma Schema: ✅ Válido" || echo "Prisma: ❌ Error"

echo ""
echo "✅ Verificación completada!"
```

Guardar este script como `verify-setup.sh` y ejecutar:

```bash
chmod +x verify-setup.sh
./verify-setup.sh
```

---

## 🚀 PRÓXIMOS PASOS

Una vez completada la instalación:

### 1. Iniciar Frontend en Modo Desarrollo

```bash
cd /mnt/c/Users/embto/Documents/GitHub/siame-2026v3/src/frontend
npm run dev
```

Acceder a: http://localhost:3000

### 2. Iniciar Orchestrator (Cuando esté listo)

```bash
cd /mnt/c/Users/embto/Documents/GitHub/siame-2026v3/orchestrator
source venv/bin/activate
python main.py
```

### 3. Poblar Base de Datos con Datos de Ejemplo

```bash
cd /mnt/c/Users/embto/Documents/GitHub/siame-2026v3/src/frontend
npx prisma db seed
```

---

## 🔧 SOLUCIÓN DE PROBLEMAS

### PostgreSQL no inicia

```bash
# Ver logs
sudo cat /var/log/postgresql/postgresql-*.log

# Reiniciar servicio
sudo service postgresql restart

# Verificar estado
sudo service postgresql status
```

### Redis no inicia

```bash
# Ver logs
sudo tail -f /var/log/redis/redis-server.log

# Reiniciar servicio
sudo service redis-server restart
```

### Error de conexión a base de datos

```bash
# Verificar que DATABASE_URL está correcto
cd /mnt/c/Users/embto/Documents/GitHub/siame-2026v3/src/frontend
cat .env | grep DATABASE_URL

# Probar conexión directa
psql -U siame_user -d siame_dev -h localhost
```

### Migraciones fallan

```bash
# Resetear base de datos (¡CUIDADO! Esto borra todos los datos)
cd /mnt/c/Users/embto/Documents/GitHub/siame-2026v3/src/frontend
npx prisma migrate reset

# Aplicar de nuevo
npx prisma migrate dev
```

---

## 📚 REFERENCIAS

- **Prisma Docs**: https://www.prisma.io/docs
- **Next.js Docs**: https://nextjs.org/docs
- **PostgreSQL Docs**: https://www.postgresql.org/docs/
- **Redis Docs**: https://redis.io/docs/

---

## 📝 NOTAS IMPORTANTES

1. **Seguridad**: Las credenciales actuales son para DESARROLLO solamente
2. **Producción**: Cambiar todas las credenciales en `.env` antes de desplegar
3. **Backup**: Hacer backup de la base de datos regularmente
4. **WSL2**: Si cierras la terminal WSL, los servicios se detienen (usar Docker o configurar inicio automático)

---

**Estado**: Listo para instalación
**Última actualización**: 2025-10-22
**Versión del Schema**: v1.0 (validado ✅)

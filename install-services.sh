#!/bin/bash

# SIAME 2026v3 - Script de Instalación Automática de Servicios
# Instala PostgreSQL, Redis y pip en WSL2 sin Docker

set -e  # Salir si hay errores

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 SIAME 2026v3 - Instalación de Servicios"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Este script instalará:"
echo "  • PostgreSQL 15"
echo "  • Redis 7"
echo "  • Python pip"
echo "  • Configurará la base de datos"
echo "  • Configurará inicio automático"
echo ""
echo "⚠️  Se necesitará tu contraseña para usar sudo"
echo ""
read -p "¿Continuar? (s/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Ss]$ ]]; then
    echo "Instalación cancelada."
    exit 1
fi

echo ""
echo "━━━ Paso 1: Actualizando sistema ━━━"
sudo apt update
echo "✅ Sistema actualizado"

echo ""
echo "━━━ Paso 2: Instalando PostgreSQL ━━━"
if command -v psql &> /dev/null; then
    echo "⚠️  PostgreSQL ya está instalado, omitiendo..."
else
    sudo apt install -y postgresql postgresql-contrib
    echo "✅ PostgreSQL instalado"
fi

echo ""
echo "━━━ Paso 3: Instalando Redis ━━━"
if command -v redis-cli &> /dev/null; then
    echo "⚠️  Redis ya está instalado, omitiendo..."
else
    sudo apt install -y redis-server
    echo "✅ Redis instalado"
fi

echo ""
echo "━━━ Paso 4: Instalando pip ━━━"
if python3 -m pip --version &> /dev/null; then
    echo "⚠️  pip ya está instalado, omitiendo..."
else
    sudo apt install -y python3-pip python3-venv
    echo "✅ pip instalado"
fi

echo ""
echo "━━━ Paso 5: Iniciando servicios ━━━"
sudo service postgresql start
sudo service redis-server start
echo "✅ Servicios iniciados"

echo ""
echo "━━━ Paso 6: Configurando PostgreSQL ━━━"

# Verificar si la base de datos ya existe
if sudo -u postgres psql -lqt | cut -d \| -f 1 | grep -qw siame_dev; then
    echo "⚠️  Base de datos 'siame_dev' ya existe"
    read -p "¿Deseas recrearla? (Esto borrará todos los datos) (s/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Ss]$ ]]; then
        sudo -u postgres psql << EOF
DROP DATABASE IF EXISTS siame_dev;
DROP USER IF EXISTS siame_user;
EOF
        echo "Base de datos eliminada"
    else
        echo "Manteniendo base de datos existente"
    fi
fi

# Crear usuario y base de datos si no existen
sudo -u postgres psql << 'EOF'
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_user WHERE usename = 'siame_user') THEN
        CREATE USER siame_user WITH PASSWORD 'siame_password';
        RAISE NOTICE 'Usuario siame_user creado';
    ELSE
        RAISE NOTICE 'Usuario siame_user ya existe';
    END IF;
END
$$;

DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_database WHERE datname = 'siame_dev') THEN
        CREATE DATABASE siame_dev OWNER siame_user;
        RAISE NOTICE 'Base de datos siame_dev creada';
    ELSE
        RAISE NOTICE 'Base de datos siame_dev ya existe';
    END IF;
END
$$;
EOF

sudo -u postgres psql << 'EOF'
GRANT ALL PRIVILEGES ON DATABASE siame_dev TO siame_user;
ALTER USER siame_user CREATEDB;
EOF

echo "✅ PostgreSQL configurado"

echo ""
echo "━━━ Paso 7: Verificando conexiones ━━━"

# Verificar PostgreSQL
if PGPASSWORD=siame_password psql -U siame_user -d siame_dev -h localhost -c "SELECT 'PostgreSQL OK' as status;" &> /dev/null; then
    echo "✅ PostgreSQL: Conectado correctamente"
else
    echo "❌ PostgreSQL: Error de conexión"
    exit 1
fi

# Verificar Redis
if redis-cli ping &> /dev/null; then
    echo "✅ Redis: Respondiendo correctamente"
else
    echo "❌ Redis: Error de conexión"
    exit 1
fi

echo ""
echo "━━━ Paso 8: Configurando inicio automático ━━━"

# Agregar al .bashrc si no existe
BASHRC_FILE="$HOME/.bashrc"
STARTUP_SCRIPT="
# SIAME 2026v3 - Auto-start services
if ! pgrep -x postgres > /dev/null 2>&1; then
    sudo service postgresql start > /dev/null 2>&1
fi
if ! pgrep -x redis-server > /dev/null 2>&1; then
    sudo service redis-server start > /dev/null 2>&1
fi"

if ! grep -q "SIAME 2026v3 - Auto-start services" "$BASHRC_FILE"; then
    echo "$STARTUP_SCRIPT" >> "$BASHRC_FILE"
    echo "✅ Inicio automático configurado en $BASHRC_FILE"
else
    echo "⚠️  Inicio automático ya estaba configurado"
fi

echo ""
echo "━━━ Paso 9: Instalando dependencias Python ━━━"
cd /mnt/c/Users/embto/Documents/GitHub/siame-2026v3/orchestrator

if [ ! -d "venv" ]; then
    echo "Creando entorno virtual..."
    python3 -m venv venv
    echo "✅ Entorno virtual creado"
else
    echo "⚠️  Entorno virtual ya existe"
fi

echo "Activando entorno virtual e instalando dependencias..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
deactivate
echo "✅ Dependencias Python instaladas"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ INSTALACIÓN COMPLETADA"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 Resumen de servicios instalados:"
echo ""
echo "  PostgreSQL:"
echo "    • Usuario: siame_user"
echo "    • Password: siame_password"
echo "    • Base de datos: siame_dev"
echo "    • Puerto: 5432"
echo ""
echo "  Redis:"
echo "    • Puerto: 6379"
echo "    • Sin contraseña (desarrollo)"
echo ""
echo "  Python:"
echo "    • pip instalado"
echo "    • Entorno virtual: orchestrator/venv"
echo "    • Dependencias instaladas"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎯 PRÓXIMOS PASOS:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "1. Verificar instalación:"
echo "   ./verify-setup.sh"
echo ""
echo "2. Aplicar migraciones de Prisma:"
echo "   cd src/frontend"
echo "   npx prisma migrate dev --name initial_setup"
echo ""
echo "3. Iniciar frontend:"
echo "   npm run dev"
echo ""
echo "4. Abrir en navegador:"
echo "   http://localhost:3000"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📚 Documentación:"
echo "  • QUICK_START.md - Inicio rápido"
echo "  • SETUP_GUIDE.md - Guía detallada"
echo "  • STATUS.md - Estado del proyecto"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

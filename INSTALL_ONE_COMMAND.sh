#!/bin/bash

# SIAME 2026v3 - Instalación en UN SOLO COMANDO
# Este script instala y configura todo automáticamente

set -e

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 SIAME 2026v3 - Instalación Completa"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Este script instalará y configurará automáticamente:"
echo "  • PostgreSQL 15"
echo "  • Redis 7"
echo "  • Python pip + dependencias"
echo "  • Base de datos configurada"
echo "  • Todo listo para desarrollo"
echo ""
echo "Tiempo estimado: 5-10 minutos"
echo ""
read -p "¿Continuar? (s/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Ss]$ ]]; then
    echo "Instalación cancelada."
    exit 1
fi

echo ""
echo "━━━ 1/7: Actualizando sistema ━━━"
sudo apt update

echo ""
echo "━━━ 2/7: Instalando servicios ━━━"
sudo apt install -y postgresql postgresql-contrib redis-server python3-pip python3-venv

echo ""
echo "━━━ 3/7: Iniciando servicios ━━━"
sudo service postgresql start
sudo service redis-server start

echo ""
echo "━━━ 4/7: Configurando PostgreSQL ━━━"
sudo -u postgres psql << 'EOF' || true
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_user WHERE usename = 'siame_user') THEN
        CREATE USER siame_user WITH PASSWORD 'siame_password';
    END IF;
END $$;

DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_database WHERE datname = 'siame_dev') THEN
        CREATE DATABASE siame_dev OWNER siame_user;
    END IF;
END $$;

GRANT ALL PRIVILEGES ON DATABASE siame_dev TO siame_user;
ALTER USER siame_user CREATEDB;
EOF

echo ""
echo "━━━ 5/7: Verificando conexiones ━━━"
if PGPASSWORD=siame_password psql -U siame_user -d siame_dev -h localhost -c "SELECT 'OK' as status;" &> /dev/null; then
    echo "✅ PostgreSQL OK"
else
    echo "❌ PostgreSQL falló"
    exit 1
fi

if redis-cli ping &> /dev/null; then
    echo "✅ Redis OK"
else
    echo "❌ Redis falló"
    exit 1
fi

echo ""
echo "━━━ 6/7: Instalando dependencias Python ━━━"
cd /mnt/c/Users/embto/Documents/GitHub/siame-2026v3/orchestrator
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip -q
pip install -r requirements.txt -q
deactivate

echo ""
echo "━━━ 7/7: Verificación final ━━━"
cd /mnt/c/Users/embto/Documents/GitHub/siame-2026v3
./verify-setup.sh

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ INSTALACIÓN COMPLETADA"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🎯 PRÓXIMO PASO:"
echo ""
echo "   ./run-migrations.sh"
echo ""
echo "Esto creará las 17 tablas en PostgreSQL (30 segundos)"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

#!/bin/bash

# SIAME 2026v3 - Script para Arreglar PostgreSQL
# Si hubo error en la instalación, este script lo soluciona

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔧 Arreglando PostgreSQL - SIAME 2026v3"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "Paso 1: Verificando estado de PostgreSQL..."
sudo service postgresql status

echo ""
echo "Paso 2: Iniciando PostgreSQL..."
sudo service postgresql start

echo ""
echo "Paso 3: Esperando que PostgreSQL inicie completamente..."
sleep 3

echo ""
echo "Paso 4: Verificando que esté corriendo..."
sudo service postgresql status

echo ""
echo "Paso 5: Configurando usuario y base de datos..."
sudo -u postgres psql << 'EOF'
-- Eliminar si existe (por si hubo error anterior)
DROP DATABASE IF EXISTS siame_dev;
DROP USER IF EXISTS siame_user;

-- Crear usuario
CREATE USER siame_user WITH PASSWORD 'siame_password';

-- Crear base de datos
CREATE DATABASE siame_dev OWNER siame_user;

-- Otorgar permisos
GRANT ALL PRIVILEGES ON DATABASE siame_dev TO siame_user;
ALTER USER siame_user CREATEDB;

-- Verificar
\du
\l

EOF

echo ""
echo "Paso 6: Probando conexión..."
PGPASSWORD=siame_password psql -U siame_user -d siame_dev -h localhost -c "SELECT 'PostgreSQL funcionando correctamente!' as status;"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ PostgreSQL debería estar funcionando ahora"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Siguiente paso:"
echo "  ./verify-setup.sh"
echo ""

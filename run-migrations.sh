#!/bin/bash

# SIAME 2026v3 - Script para aplicar migraciones de Prisma
# Fecha: 2025-10-22

set -e

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🗄️  SIAME 2026v3 - Migraciones de Base de Datos"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Verificar que estamos en el directorio correcto
if [ ! -f "docker-compose.yml" ]; then
    echo -e "${RED}❌ Error: Debes ejecutar este script desde la raíz del proyecto${NC}"
    exit 1
fi

# Verificar PostgreSQL
echo "━━━ Verificando PostgreSQL ━━━"
if PGPASSWORD=siame_password psql -U siame_user -d siame_dev -h localhost -c "SELECT 1;" &> /dev/null; then
    echo -e "${GREEN}✅ PostgreSQL conectado${NC}"
else
    echo -e "${RED}❌ PostgreSQL no está disponible${NC}"
    echo ""
    echo "Ejecuta primero: ./install-services.sh"
    echo "O inicia el servicio: sudo service postgresql start"
    exit 1
fi

# Ir al directorio del frontend
cd src/frontend

echo ""
echo "━━━ Validando Schema de Prisma ━━━"
if npx prisma validate 2>&1 | grep -q "valid"; then
    echo -e "${GREEN}✅ Schema válido${NC}"
else
    echo -e "${RED}❌ Error en el schema${NC}"
    npx prisma validate
    exit 1
fi

echo ""
echo "━━━ Generando Cliente Prisma ━━━"
npx prisma generate
echo -e "${GREEN}✅ Cliente generado${NC}"

echo ""
echo "━━━ Aplicando Migraciones ━━━"
echo ""
echo "⚠️  Esto creará las siguientes tablas en la base de datos:"
echo "  • users (usuarios del sistema)"
echo "  • accounts (cuentas de autenticación)"
echo "  • sessions (sesiones activas)"
echo "  • documents (documentos base)"
echo "  • hojas_remision (documentos de remisión)"
echo "  • guias_valija (guías de valija diplomática)"
echo "  • valijas_internas (valijas internas)"
echo "  • items_valija (items de valijas)"
echo "  • precintos (control de precintos)"
echo "  • workflows (flujos de trabajo)"
echo "  • workflow_steps (pasos de workflows)"
echo "  • document_workflows (relación documentos-workflows)"
echo "  • notifications (notificaciones)"
echo "  • audit_logs (registros de auditoría)"
echo "  • system_config (configuración del sistema)"
echo "  • file_uploads (archivos subidos)"
echo "  • document_authorizations (permisos por documento)"
echo ""
read -p "¿Continuar con las migraciones? (s/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Ss]$ ]]; then
    echo "Migraciones canceladas."
    exit 1
fi

echo ""
npx prisma migrate dev --name initial_setup

echo ""
echo "━━━ Verificando Migraciones ━━━"
echo ""
echo "Tablas creadas en la base de datos:"
PGPASSWORD=siame_password psql -U siame_user -d siame_dev -h localhost -c "\dt" | grep -E "public \|" || echo "No se pudieron listar las tablas"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}✅ MIGRACIONES COMPLETADAS${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 Estadísticas de la base de datos:"
echo ""
PGPASSWORD=siame_password psql -U siame_user -d siame_dev -h localhost << 'EOF'
SELECT
    schemaname as schema,
    COUNT(*) as total_tablas
FROM pg_tables
WHERE schemaname = 'public'
GROUP BY schemaname;

SELECT
    'Total de enums' as descripcion,
    COUNT(*) as cantidad
FROM pg_type
WHERE typtype = 'e';
EOF

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎯 PRÓXIMOS PASOS:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "1. Explorar la base de datos con Prisma Studio:"
echo "   cd src/frontend"
echo "   npx prisma studio"
echo "   # Se abrirá en http://localhost:5555"
echo ""
echo "2. Iniciar el frontend en desarrollo:"
echo "   cd src/frontend"
echo "   npm run dev"
echo "   # Se abrirá en http://localhost:3000"
echo ""
echo "3. (Opcional) Poblar con datos de ejemplo:"
echo "   cd src/frontend"
echo "   npx prisma db seed"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📚 Información de la base de datos:"
echo "  • Host: localhost"
echo "  • Puerto: 5432"
echo "  • Base de datos: siame_dev"
echo "  • Usuario: siame_user"
echo "  • Password: siame_password"
echo ""
echo "  Conectar con psql:"
echo "  PGPASSWORD=siame_password psql -U siame_user -d siame_dev -h localhost"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

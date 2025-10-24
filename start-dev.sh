#!/bin/bash

# SIAME 2026v3 - Script de inicio rápido para desarrollo
# Fecha: 2025-10-22

set -e

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 SIAME 2026v3 - Inicio de Desarrollo"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para verificar servicio
check_service() {
    local service=$1
    local check_cmd=$2

    echo -n "Verificando $service... "
    if eval $check_cmd &> /dev/null; then
        echo -e "${GREEN}✅${NC}"
        return 0
    else
        echo -e "${RED}❌${NC}"
        return 1
    fi
}

# Función para iniciar servicio
start_service() {
    local service=$1
    echo "Iniciando $service..."
    sudo service $service start
}

echo "━━━ Verificando servicios ━━━"
echo ""

# Verificar y arrancar PostgreSQL
if ! check_service "PostgreSQL" "PGPASSWORD=siame_password psql -U siame_user -d siame_dev -h localhost -c 'SELECT 1'"; then
    echo -e "${YELLOW}PostgreSQL no está corriendo. Intentando iniciar...${NC}"
    if command -v psql &> /dev/null; then
        start_service postgresql
        sleep 2
        if check_service "PostgreSQL" "PGPASSWORD=siame_password psql -U siame_user -d siame_dev -h localhost -c 'SELECT 1'"; then
            echo -e "${GREEN}PostgreSQL iniciado correctamente${NC}"
        else
            echo -e "${RED}Error: PostgreSQL no se pudo iniciar${NC}"
            echo "Ejecuta: ./install-services.sh"
            exit 1
        fi
    else
        echo -e "${RED}PostgreSQL no está instalado${NC}"
        echo "Ejecuta: ./install-services.sh"
        exit 1
    fi
fi

# Verificar y arrancar Redis
if ! check_service "Redis" "redis-cli ping"; then
    echo -e "${YELLOW}Redis no está corriendo. Intentando iniciar...${NC}"
    if command -v redis-cli &> /dev/null; then
        start_service redis-server
        sleep 1
        if check_service "Redis" "redis-cli ping"; then
            echo -e "${GREEN}Redis iniciado correctamente${NC}"
        else
            echo -e "${RED}Error: Redis no se pudo iniciar${NC}"
            exit 1
        fi
    else
        echo -e "${RED}Redis no está instalado${NC}"
        echo "Ejecuta: ./install-services.sh"
        exit 1
    fi
fi

echo ""
echo "━━━ Verificando migraciones ━━━"
echo ""

# Verificar si hay tablas en la base de datos
TABLE_COUNT=$(PGPASSWORD=siame_password psql -U siame_user -d siame_dev -h localhost -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';" 2>/dev/null | tr -d ' ')

if [ "$TABLE_COUNT" = "0" ] || [ -z "$TABLE_COUNT" ]; then
    echo -e "${YELLOW}⚠️  No se encontraron tablas en la base de datos${NC}"
    echo ""
    echo "¿Deseas aplicar las migraciones ahora?"
    echo "Esto creará todas las tablas necesarias para el sistema."
    echo ""
    read -p "¿Aplicar migraciones? (s/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Ss]$ ]]; then
        ./run-migrations.sh
    else
        echo -e "${YELLOW}⚠️  El sistema necesita migraciones para funcionar${NC}"
        echo "Ejecuta manualmente: ./run-migrations.sh"
        exit 1
    fi
else
    echo -e "${GREEN}✅ Base de datos configurada ($TABLE_COUNT tablas)${NC}"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}✅ SISTEMA LISTO PARA DESARROLLO${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 Servicios activos:"
echo ""
echo "  ✅ PostgreSQL (localhost:5432)"
echo "  ✅ Redis (localhost:6379)"
echo "  ✅ Prisma ($TABLE_COUNT tablas)"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎯 INICIAR DESARROLLO:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "${BLUE}Opción 1: Frontend Next.js${NC}"
echo "  cd src/frontend"
echo "  npm run dev"
echo "  # Abrir: http://localhost:3000"
echo ""
echo -e "${BLUE}Opción 2: Prisma Studio (Explorar BD)${NC}"
echo "  cd src/frontend"
echo "  npx prisma studio"
echo "  # Abrir: http://localhost:5555"
echo ""
echo -e "${BLUE}Opción 3: Orchestrator (Backend)${NC}"
echo "  cd orchestrator"
echo "  source venv/bin/activate"
echo "  python main.py"
echo "  # API: http://localhost:8000"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "¿Qué deseas iniciar?"
echo ""
echo "  1) Frontend (Next.js)"
echo "  2) Prisma Studio"
echo "  3) Orchestrator"
echo "  4) Todo en terminales separadas"
echo "  5) Solo verificar (salir)"
echo ""
read -p "Selecciona una opción (1-5): " -n 1 -r
echo
echo ""

case $REPLY in
    1)
        echo "Iniciando Frontend..."
        cd src/frontend
        npm run dev
        ;;
    2)
        echo "Iniciando Prisma Studio..."
        cd src/frontend
        npx prisma studio
        ;;
    3)
        echo "Iniciando Orchestrator..."
        cd orchestrator
        if [ -d "venv" ]; then
            source venv/bin/activate
            python main.py
        else
            echo -e "${YELLOW}⚠️  Entorno virtual no encontrado${NC}"
            echo "Ejecuta: ./install-services.sh"
            exit 1
        fi
        ;;
    4)
        echo "Para iniciar múltiples servicios, abre varias terminales:"
        echo ""
        echo "Terminal 1: cd src/frontend && npm run dev"
        echo "Terminal 2: cd src/frontend && npx prisma studio"
        echo "Terminal 3: cd orchestrator && source venv/bin/activate && python main.py"
        ;;
    5)
        echo "Sistema listo. ¡Feliz desarrollo! 🚀"
        ;;
    *)
        echo "Opción no válida"
        exit 1
        ;;
esac

#!/bin/bash

# SIAME 2026v3 - Script de Verificación de Instalación
# Fecha: 2025-10-22

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔍 SIAME 2026v3 - Verificación de Instalación"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Función para verificar comando
check_command() {
    local cmd=$1
    local name=$2
    local version_flag=${3:---version}

    echo -n "Verificando $name... "
    if command -v $cmd &> /dev/null; then
        echo -e "${GREEN}✅ Instalado${NC}"
        $cmd $version_flag 2>&1 | head -1
    else
        echo -e "${RED}❌ No encontrado${NC}"
        return 1
    fi
    echo ""
}

# Verificar Node.js
echo "━━━ Node.js y npm ━━━"
check_command "node" "Node.js" "--version"
check_command "npm" "npm" "--version"

# Verificar Python
echo "━━━ Python ━━━"
check_command "python3" "Python" "--version"
echo -n "Verificando pip... "
if python3 -m pip --version &> /dev/null; then
    echo -e "${GREEN}✅ Instalado${NC}"
    python3 -m pip --version
else
    echo -e "${RED}❌ No encontrado${NC}"
    echo "Instalar con: sudo apt install python3-pip python3-venv"
fi
echo ""

# Verificar PostgreSQL
echo "━━━ PostgreSQL ━━━"
PG_AVAILABLE=false
echo -n "Verificando PostgreSQL nativo... "
if command -v psql &> /dev/null; then
    echo -e "${GREEN}✅ Instalado${NC}"
    psql --version
    echo -n "Probando conexión a BD... "
    if PGPASSWORD=siame_password psql -U siame_user -d siame_dev -h localhost -c "SELECT 'OK' as status;" &> /dev/null; then
        echo -e "${GREEN}✅ Conectado${NC}"
        PG_AVAILABLE=true
    else
        echo -e "${YELLOW}⚠️  No conectado (servicio parado?)${NC}"
        echo "Iniciar con: sudo service postgresql start"
    fi
else
    echo -e "${YELLOW}⚠️  No instalado${NC}"
    echo -n "Verificando PostgreSQL en Docker... "
    if docker compose ps postgres 2>&1 | grep -q "Up"; then
        echo -e "${GREEN}✅ Corriendo en Docker${NC}"
        PG_AVAILABLE=true
    else
        echo -e "${RED}❌ No disponible${NC}"
        echo "Ver SETUP_GUIDE.md para instrucciones de instalación"
    fi
fi
echo ""

# Verificar Redis
echo "━━━ Redis ━━━"
REDIS_AVAILABLE=false
echo -n "Verificando Redis nativo... "
if command -v redis-cli &> /dev/null; then
    echo -e "${GREEN}✅ Instalado${NC}"
    redis-cli --version
    echo -n "Probando conexión... "
    if redis-cli ping 2>&1 | grep -q "PONG"; then
        echo -e "${GREEN}✅ Conectado${NC}"
        REDIS_AVAILABLE=true
    else
        echo -e "${YELLOW}⚠️  No conectado (servicio parado?)${NC}"
        echo "Iniciar con: sudo service redis-server start"
    fi
else
    echo -e "${YELLOW}⚠️  No instalado${NC}"
    echo -n "Verificando Redis en Docker... "
    if docker compose ps redis 2>&1 | grep -q "Up"; then
        echo -e "${GREEN}✅ Corriendo en Docker${NC}"
        REDIS_AVAILABLE=true
    else
        echo -e "${RED}❌ No disponible${NC}"
        echo "Ver SETUP_GUIDE.md para instrucciones de instalación"
    fi
fi
echo ""

# Verificar Docker
echo "━━━ Docker ━━━"
check_command "docker" "Docker" "--version"
check_command "docker" "Docker Compose" "compose version"

# Verificar Prisma
echo "━━━ Prisma ━━━"
cd /mnt/c/Users/embto/Documents/GitHub/siame-2026v3/src/frontend 2>/dev/null
if [ -f "prisma/schema.prisma" ]; then
    echo -n "Verificando Schema de Prisma... "
    if npx prisma validate 2>&1 | grep -q "valid"; then
        echo -e "${GREEN}✅ Válido${NC}"
    else
        echo -e "${RED}❌ Error en schema${NC}"
    fi

    echo -n "Verificando Cliente Prisma... "
    if [ -d "node_modules/@prisma/client" ]; then
        echo -e "${GREEN}✅ Generado${NC}"
    else
        echo -e "${YELLOW}⚠️  No generado${NC}"
        echo "Generar con: npx prisma generate"
    fi
else
    echo -e "${RED}❌ Schema no encontrado${NC}"
fi
echo ""

# Verificar dependencias Node
echo "━━━ Dependencias Node.js ━━━"
cd /mnt/c/Users/embto/Documents/GitHub/siame-2026v3/src/frontend 2>/dev/null
if [ -d "node_modules" ]; then
    echo -e "${GREEN}✅ node_modules presente${NC}"
    PACKAGE_COUNT=$(ls -1 node_modules | wc -l)
    echo "   Paquetes instalados: $PACKAGE_COUNT"
else
    echo -e "${RED}❌ node_modules no encontrado${NC}"
    echo "Instalar con: npm install"
fi
echo ""

# Verificar variables de entorno
echo "━━━ Variables de Entorno ━━━"
cd /mnt/c/Users/embto/Documents/GitHub/siame-2026v3/src/frontend 2>/dev/null
if [ -f ".env" ]; then
    echo -e "${GREEN}✅ .env presente${NC}"
    if grep -q "DATABASE_URL" .env; then
        echo "   ✓ DATABASE_URL configurada"
    fi
    if grep -q "NEXTAUTH_SECRET" .env; then
        echo "   ✓ NEXTAUTH_SECRET configurada"
    fi
else
    echo -e "${YELLOW}⚠️  .env no encontrado${NC}"
    echo "Copiar desde: cp .env.example .env"
fi
echo ""

# Resumen
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 RESUMEN"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if [ "$PG_AVAILABLE" = true ] && [ "$REDIS_AVAILABLE" = true ]; then
    echo -e "${GREEN}✅ Sistema listo para desarrollo${NC}"
    echo ""
    echo "Próximos pasos:"
    echo "  1. cd /mnt/c/Users/embto/Documents/GitHub/siame-2026v3/src/frontend"
    echo "  2. npx prisma migrate dev --name initial_setup"
    echo "  3. npm run dev"
else
    echo -e "${YELLOW}⚠️  Configuración incompleta${NC}"
    echo ""
    echo "Servicios faltantes:"
    [ "$PG_AVAILABLE" = false ] && echo "  - PostgreSQL"
    [ "$REDIS_AVAILABLE" = false ] && echo "  - Redis"
    echo ""
    echo "Ver SETUP_GUIDE.md para instrucciones completas"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Documentación: SETUP_GUIDE.md"
echo "Estado: STATUS.md"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

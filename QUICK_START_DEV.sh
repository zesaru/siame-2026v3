#!/bin/bash
# SIAME 2026v3 - Script de Inicio Rápido para Desarrollo
# Compatible con Mac y Linux

set -e

echo "======================================"
echo "🚀 SIAME 2026v3 - Inicio Rápido"
echo "======================================"
echo ""

# Verificar que Docker esté corriendo
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker no está corriendo. Por favor inicia Docker Desktop."
    exit 1
fi

echo "✅ Docker está corriendo"
echo ""

# Verificar que existe .env
if [ ! -f .env ]; then
    echo "📝 Creando archivo .env desde template..."
    cp .env.example .env
    echo "✅ Archivo .env creado"
    echo "⚠️  IMPORTANTE: Edita .env con tus configuraciones antes de continuar"
    echo ""
    read -p "¿Quieres continuar con valores por defecto? (s/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[SsYy]$ ]]; then
        echo "Abortando. Edita .env y vuelve a ejecutar este script."
        exit 0
    fi
fi

echo "======================================"
echo "Paso 1/5: Iniciando PostgreSQL y Redis"
echo "======================================"
docker compose up -d postgres redis
echo "⏳ Esperando a que los servicios estén saludables..."
sleep 15

# Verificar que estén corriendo
if docker compose ps | grep -q "siame_postgres.*Up"; then
    echo "✅ PostgreSQL iniciado"
else
    echo "❌ PostgreSQL no pudo iniciar"
    docker compose logs postgres
    exit 1
fi

if docker compose ps | grep -q "siame_redis.*Up"; then
    echo "✅ Redis iniciado"
else
    echo "❌ Redis no pudo iniciar"
    docker compose logs redis
    exit 1
fi

echo ""
echo "======================================"
echo "Paso 2/5: Verificando Node.js"
echo "======================================"
cd src/frontend

if [ ! -d "node_modules" ]; then
    echo "📦 Instalando dependencias del frontend..."
    npm install
    echo "✅ Dependencias instaladas"
else
    echo "✅ Dependencias ya instaladas"
fi

echo ""
echo "======================================"
echo "Paso 3/5: Aplicando migraciones de BD"
echo "======================================"
echo "⏳ Aplicando migraciones Prisma..."

if npx prisma migrate dev --name init; then
    echo "✅ Migraciones aplicadas correctamente"
else
    echo "⚠️  Las migraciones pueden haber fallado, pero intentemos continuar..."
fi

echo ""
echo "======================================"
echo "Paso 4/5: Generando cliente Prisma"
echo "======================================"
npx prisma generate
echo "✅ Cliente Prisma generado"

cd ../..

echo ""
echo "======================================"
echo "Paso 5/5: Iniciando todos los servicios"
echo "======================================"
docker compose up -d

echo ""
echo "⏳ Esperando a que todos los servicios inicien..."
sleep 10

echo ""
echo "======================================"
echo "✅ SIAME 2026v3 está corriendo!"
echo "======================================"
echo ""
echo "📍 Servicios disponibles:"
echo ""
echo "   🌐 Frontend:           http://localhost:3000"
echo "   🔌 Backend API:        http://localhost:8000"
echo "   📚 Docs API:           http://localhost:8000/docs"
echo "   📊 Grafana:            http://localhost:3001"
echo "   📈 Prometheus:         http://localhost:9090"
echo "   🗄️  PostgreSQL:         localhost:5432"
echo "   💾 Redis:              localhost:6379"
echo ""
echo "======================================"
echo "📋 Comandos útiles:"
echo "======================================"
echo ""
echo "  Ver logs:              docker compose logs -f"
echo "  Ver estado:            docker compose ps"
echo "  Detener todo:          docker compose stop"
echo "  Reiniciar:             docker compose restart"
echo "  Limpiar todo:          docker compose down -v"
echo ""
echo "======================================"
echo "📖 Documentación:"
echo "======================================"
echo ""
echo "  Desarrollo:            DESARROLLO_LOCAL.md"
echo "  Deployment:            DEPLOYMENT_WINDOWS_SERVER_2025.md"
echo "  General:               README.md"
echo ""
echo "======================================"
echo "🎉 ¡Listo para desarrollar!"
echo "======================================"
echo ""

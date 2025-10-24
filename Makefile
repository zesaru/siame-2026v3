# SIAME 2026v3 - Makefile
# Sistema Inteligente de Administración y Manejo de Expedientes

.PHONY: help setup dev test build clean docker-build docker-up docker-down
.DEFAULT_GOAL := help

# ================================
# VARIABLES
# ================================
PYTHON_VERSION := 3.11
NODE_VERSION := 18
DOCKER_COMPOSE := docker-compose
BACKEND_DIR := src/backend
FRONTEND_DIR := src/frontend

# Colors for output
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[0;33m
BLUE := \033[0;34m
NC := \033[0m # No Color

# ================================
# HELP
# ================================
help: ## Mostrar esta ayuda
	@echo "$(BLUE)SIAME 2026v3 - Sistema Inteligente de Administración y Manejo de Expedientes$(NC)"
	@echo "$(BLUE)================================================================$(NC)"
	@echo ""
	@echo "$(GREEN)Comandos disponibles:$(NC)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# ================================
# SETUP Y INSTALACIÓN
# ================================
setup: ## Configurar el entorno de desarrollo completo
	@echo "$(GREEN)Configurando SIAME 2026v3...$(NC)"
	@make setup-backend
	@make setup-frontend
	@make setup-docker
	@echo "$(GREEN)✅ Configuración completada$(NC)"

setup-backend: ## Configurar el backend Python
	@echo "$(BLUE)Configurando backend...$(NC)"
	cd $(BACKEND_DIR) && python -m venv venv
	cd $(BACKEND_DIR) && source venv/bin/activate && pip install -r requirements.txt
	@echo "$(GREEN)✅ Backend configurado$(NC)"

setup-frontend: ## Configurar el frontend Next.js
	@echo "$(BLUE)Configurando frontend...$(NC)"
	cd $(FRONTEND_DIR) && npm install
	@echo "$(GREEN)✅ Frontend configurado$(NC)"

setup-docker: ## Configurar Docker y contenedores
	@echo "$(BLUE)Configurando Docker...$(NC)"
	@if [ ! -f .env ]; then cp .env.example .env; echo "$(YELLOW)⚠️  Archivo .env creado. Configurar variables antes de continuar.$(NC)"; fi
	@echo "$(GREEN)✅ Docker configurado$(NC)"

# ================================
# DESARROLLO
# ================================
dev: ## Iniciar el entorno de desarrollo completo
	@echo "$(GREEN)Iniciando SIAME 2026v3 en modo desarrollo...$(NC)"
	$(DOCKER_COMPOSE) up -d postgres redis
	@sleep 5
	@make dev-backend &
	@make dev-frontend &
	@echo "$(GREEN)🚀 SIAME 2026v3 iniciado$(NC)"
	@echo "$(BLUE)Frontend: http://localhost:3000$(NC)"
	@echo "$(BLUE)Backend: http://localhost:8000$(NC)"

dev-backend: ## Iniciar solo el backend
	@echo "$(BLUE)Iniciando backend...$(NC)"
	cd $(BACKEND_DIR) && source venv/bin/activate && python -m uvicorn orchestrator.main:app --reload --host 0.0.0.0 --port 8000

dev-frontend: ## Iniciar solo el frontend
	@echo "$(BLUE)Iniciando frontend...$(NC)"
	cd $(FRONTEND_DIR) && npm run dev

# ================================
# TESTING
# ================================
test: ## Ejecutar todos los tests
	@echo "$(GREEN)Ejecutando tests de SIAME 2026v3...$(NC)"
	@make test-backend
	@make test-frontend
	@echo "$(GREEN)✅ Todos los tests completados$(NC)"

test-backend: ## Ejecutar tests del backend
	@echo "$(BLUE)Ejecutando tests del backend...$(NC)"
	cd $(BACKEND_DIR) && source venv/bin/activate && pytest tests/ -v --cov=.

test-frontend: ## Ejecutar tests del frontend
	@echo "$(BLUE)Ejecutando tests del frontend...$(NC)"
	cd $(FRONTEND_DIR) && npm run test

test-e2e: ## Ejecutar tests end-to-end
	@echo "$(BLUE)Ejecutando tests E2E...$(NC)"
	cd $(FRONTEND_DIR) && npm run test:e2e

test-security: ## Ejecutar tests de seguridad
	@echo "$(BLUE)Ejecutando tests de seguridad...$(NC)"
	@echo "$(YELLOW)Escaneando secretos...$(NC)"
	trufflehog filesystem . --only-verified
	@echo "$(YELLOW)Analizando dependencias...$(NC)"
	cd $(FRONTEND_DIR) && npm audit --audit-level moderate
	cd $(BACKEND_DIR) && source venv/bin/activate && safety check

# ================================
# BUILD Y PRODUCCIÓN
# ================================
build: ## Construir aplicación para producción
	@echo "$(GREEN)Construyendo SIAME 2026v3...$(NC)"
	@make build-frontend
	@make build-backend
	@echo "$(GREEN)✅ Build completado$(NC)"

build-frontend: ## Construir frontend
	@echo "$(BLUE)Construyendo frontend...$(NC)"
	cd $(FRONTEND_DIR) && npm run build

build-backend: ## Preparar backend para producción
	@echo "$(BLUE)Preparando backend...$(NC)"
	cd $(BACKEND_DIR) && source venv/bin/activate && python -m pip install --upgrade pip

# ================================
# DOCKER
# ================================
docker-build: ## Construir imágenes Docker
	@echo "$(GREEN)Construyendo imágenes Docker...$(NC)"
	$(DOCKER_COMPOSE) build

docker-up: ## Iniciar servicios con Docker Compose
	@echo "$(GREEN)Iniciando servicios Docker...$(NC)"
	$(DOCKER_COMPOSE) up -d
	@echo "$(GREEN)🐳 Servicios Docker iniciados$(NC)"
	@echo "$(BLUE)Frontend: http://localhost:3000$(NC)"
	@echo "$(BLUE)Backend: http://localhost:8000$(NC)"
	@echo "$(BLUE)Grafana: http://localhost:3001$(NC)"

docker-down: ## Detener servicios Docker
	@echo "$(YELLOW)Deteniendo servicios Docker...$(NC)"
	$(DOCKER_COMPOSE) down

docker-logs: ## Ver logs de Docker Compose
	$(DOCKER_COMPOSE) logs -f

docker-clean: ## Limpiar recursos Docker
	@echo "$(YELLOW)Limpiando recursos Docker...$(NC)"
	$(DOCKER_COMPOSE) down -v --remove-orphans
	docker system prune -f

# ================================
# BASE DE DATOS
# ================================
db-migrate: ## Ejecutar migraciones de base de datos
	@echo "$(BLUE)Ejecutando migraciones...$(NC)"
	cd $(FRONTEND_DIR) && npx prisma migrate deploy

db-seed: ## Poblar base de datos con datos de prueba
	@echo "$(BLUE)Poblando base de datos...$(NC)"
	cd $(FRONTEND_DIR) && npx prisma db seed

db-reset: ## Resetear base de datos
	@echo "$(YELLOW)Reseteando base de datos...$(NC)"
	cd $(FRONTEND_DIR) && npx prisma migrate reset --force

db-studio: ## Abrir Prisma Studio
	@echo "$(BLUE)Abriendo Prisma Studio...$(NC)"
	cd $(FRONTEND_DIR) && npx prisma studio

# ================================
# LINTING Y FORMATTING
# ================================
lint: ## Ejecutar linting en todo el proyecto
	@echo "$(BLUE)Ejecutando linting...$(NC)"
	@make lint-frontend
	@make lint-backend

lint-frontend: ## Linting del frontend
	cd $(FRONTEND_DIR) && npm run lint

lint-backend: ## Linting del backend
	cd $(BACKEND_DIR) && source venv/bin/activate && flake8 . && black --check .

format: ## Formatear código
	@echo "$(BLUE)Formateando código...$(NC)"
	@make format-frontend
	@make format-backend

format-frontend: ## Formatear frontend
	cd $(FRONTEND_DIR) && npm run format

format-backend: ## Formatear backend
	cd $(BACKEND_DIR) && source venv/bin/activate && black .

# ================================
# MONITOREO Y LOGS
# ================================
logs: ## Ver logs del sistema
	@echo "$(BLUE)Mostrando logs del sistema...$(NC)"
	$(DOCKER_COMPOSE) logs -f orchestrator frontend

logs-agents: ## Ver logs de los agentes
	$(DOCKER_COMPOSE) logs -f document-processor database-manager azure-specialist security-guardian workflow-manager communication-hub quality-assurance

monitor: ## Abrir herramientas de monitoreo
	@echo "$(GREEN)Abriendo herramientas de monitoreo...$(NC)"
	@echo "$(BLUE)Grafana: http://localhost:3001$(NC)"
	@echo "$(BLUE)Prometheus: http://localhost:9090$(NC)"

# ================================
# SEGURIDAD
# ================================
security-scan: ## Ejecutar escaneo de seguridad completo
	@echo "$(GREEN)Ejecutando escaneo de seguridad...$(NC)"
	@make test-security
	@echo "$(BLUE)Ejecutando análisis de código...$(NC)"
	cd $(FRONTEND_DIR) && npm run security:audit
	@echo "$(GREEN)✅ Escaneo de seguridad completado$(NC)"

# ================================
# DOCUMENTACIÓN
# ================================
docs: ## Generar documentación
	@echo "$(BLUE)Generando documentación...$(NC)"
	cd docs && mkdocs serve

docs-build: ## Construir documentación estática
	cd docs && mkdocs build

# ================================
# UTILIDADES
# ================================
clean: ## Limpiar archivos temporales
	@echo "$(YELLOW)Limpiando archivos temporales...$(NC)"
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name ".pytest_cache" -delete
	find . -type d -name "node_modules" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".next" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "dist" -exec rm -rf {} + 2>/dev/null || true
	@echo "$(GREEN)✅ Limpieza completada$(NC)"

health: ## Verificar estado del sistema
	@echo "$(BLUE)Verificando estado del sistema...$(NC)"
	@curl -f http://localhost:8000/health || echo "$(RED)❌ Backend no disponible$(NC)"
	@curl -f http://localhost:3000/api/health || echo "$(RED)❌ Frontend no disponible$(NC)"
	@echo "$(GREEN)✅ Verificación completada$(NC)"

status: ## Mostrar estado de los servicios
	@echo "$(BLUE)Estado de los servicios:$(NC)"
	$(DOCKER_COMPOSE) ps

# ================================
# DEPLOYMENT
# ================================
deploy-staging: ## Desplegar a staging
	@echo "$(GREEN)Desplegando a staging...$(NC)"
	@echo "$(YELLOW)⚠️  Implementar scripts de deployment$(NC)"

deploy-production: ## Desplegar a producción
	@echo "$(GREEN)Desplegando a producción...$(NC)"
	@echo "$(RED)⚠️  ATENCIÓN: Despliegue a producción$(NC)"
	@echo "$(YELLOW)⚠️  Implementar scripts de deployment$(NC)"

# ================================
# INFORMACIÓN
# ================================
version: ## Mostrar versión
	@echo "$(GREEN)SIAME 2026v3 - Versión 3.0.0$(NC)"
	@echo "$(BLUE)Sistema Inteligente de Administración y Manejo de Expedientes$(NC)"
	@echo "$(BLUE)Ministerio de Asuntos Exteriores, Unión Europea y Cooperación$(NC)"
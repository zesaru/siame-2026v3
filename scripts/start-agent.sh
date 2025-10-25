#!/bin/bash
set -e

echo "========================================"
echo "🚀 Starting SIAME Agent"
echo "========================================"
echo "Agent Type: $AGENT_TYPE"
echo "Orchestrator URL: $ORCHESTRATOR_URL"
echo "========================================"

# Validar que AGENT_TYPE esté definido
if [ -z "$AGENT_TYPE" ]; then
    echo "❌ ERROR: AGENT_TYPE environment variable is not set"
    exit 1
fi

# Validar que ORCHESTRATOR_URL esté definido
if [ -z "$ORCHESTRATOR_URL" ]; then
    echo "⚠️  WARNING: ORCHESTRATOR_URL is not set. Using default: http://orchestrator:8000"
    export ORCHESTRATOR_URL="http://orchestrator:8000"
fi

# Esperar a que el orchestrator esté disponible
echo "⏳ Waiting for orchestrator to be ready..."
until curl -f "$ORCHESTRATOR_URL/health" > /dev/null 2>&1; do
    echo "Waiting for orchestrator at $ORCHESTRATOR_URL..."
    sleep 5
done
echo "✅ Orchestrator is ready!"

# Asignar puerto según tipo de agente (para healthcheck)
case "$AGENT_TYPE" in
  document_processor)
    export AGENT_PORT=8001
    ;;
  database_manager)
    export AGENT_PORT=8002
    ;;
  azure_specialist)
    export AGENT_PORT=8003
    ;;
  security_guardian)
    export AGENT_PORT=8004
    ;;
  workflow_manager)
    export AGENT_PORT=8005
    ;;
  communication_hub)
    export AGENT_PORT=8006
    ;;
  quality_assurance)
    export AGENT_PORT=8007
    ;;
  *)
    export AGENT_PORT=8001
    ;;
esac

echo "Agent Port: $AGENT_PORT"
echo "========================================"

# Iniciar el agente según su tipo
case "$AGENT_TYPE" in
  document_processor)
    echo "📄 Starting Document Processor Agent on port $AGENT_PORT..."
    cd /app && python agents/document_processor/main.py
    ;;

  database_manager)
    echo "🗄️  Starting Database Manager Agent on port $AGENT_PORT..."
    cd /app && python agents/database_manager/main.py
    ;;

  azure_specialist)
    echo "☁️  Starting Azure Specialist Agent on port $AGENT_PORT..."
    cd /app && python agents/azure_specialist/main.py
    ;;

  security_guardian)
    echo "🔒 Starting Security Guardian Agent on port $AGENT_PORT..."
    cd /app && python agents/security_guardian/main.py
    ;;

  workflow_manager)
    echo "🔄 Starting Workflow Manager Agent on port $AGENT_PORT..."
    cd /app && python agents/workflow_manager/main.py
    ;;

  communication_hub)
    echo "📧 Starting Communication Hub Agent on port $AGENT_PORT..."
    cd /app && python agents/communication_hub/main.py
    ;;

  quality_assurance)
    echo "✅ Starting Quality Assurance Agent on port $AGENT_PORT..."
    cd /app && python agents/quality_assurance/main.py
    ;;

  *)
    echo "❌ ERROR: Unknown AGENT_TYPE: $AGENT_TYPE"
    echo "Valid types: document_processor, database_manager, azure_specialist, security_guardian, workflow_manager, communication_hub, quality_assurance"
    exit 1
    ;;
esac

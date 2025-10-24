#!/usr/bin/env python3
"""
SIAME 2026v3 - Orquestador Principal
Punto de entrada y coordinación del sistema multi-agente diplomático
"""

import asyncio
import logging
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .coordinator import AgentCoordinator
from .task_queue import TaskQueue
from .message_broker import MessageBroker
from .health_monitor import HealthMonitor
from ..shared.config import settings
from ..shared.logger import setup_logging


# Configurar logging
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestión del ciclo de vida de la aplicación"""
    # Startup
    logger.info("🚀 Iniciando SIAME 2026v3 Orchestrator")

    # Inicializar componentes del orquestador
    app.state.task_queue = TaskQueue()
    app.state.message_broker = MessageBroker()
    app.state.health_monitor = HealthMonitor()
    app.state.coordinator = AgentCoordinator(
        task_queue=app.state.task_queue,
        message_broker=app.state.message_broker,
        health_monitor=app.state.health_monitor
    )

    # Iniciar servicios
    await app.state.coordinator.initialize()
    await app.state.health_monitor.start_monitoring()

    logger.info("✅ SIAME 2026v3 Orchestrator iniciado correctamente")

    yield

    # Shutdown
    logger.info("🛑 Deteniendo SIAME 2026v3 Orchestrator")
    await app.state.coordinator.shutdown()
    await app.state.health_monitor.stop_monitoring()
    logger.info("✅ SIAME 2026v3 Orchestrator detenido correctamente")


# Crear aplicación FastAPI
app = FastAPI(
    title="SIAME 2026v3 Orchestrator",
    description="Sistema Inteligente de Administración y Manejo de Expedientes - Orquestador Multi-Agente",
    version="3.0.0",
    docs_url="/docs" if settings.ENVIRONMENT == "development" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT == "development" else None,
    lifespan=lifespan
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Verificación de salud del orquestador"""
    try:
        health_status = await app.state.health_monitor.get_system_health()
        return {
            "status": "healthy",
            "timestamp": health_status["timestamp"],
            "version": "3.0.0",
            "agents": health_status["agents"],
            "services": health_status["services"]
        }
    except Exception as e:
        logger.error(f"Error en health check: {e}")
        raise HTTPException(status_code=503, detail="Service unavailable")


@app.get("/")
async def root():
    """Endpoint raíz del orquestador"""
    return {
        "system": "SIAME 2026v3",
        "component": "Orchestrator",
        "version": "3.0.0",
        "status": "running",
        "ministry": "Ministerio de Asuntos Exteriores, Unión Europea y Cooperación"
    }


@app.post("/tasks")
async def create_task(task_data: dict):
    """Crear nueva tarea para procesamiento por agentes"""
    try:
        task_id = await app.state.coordinator.create_task(task_data)
        return {
            "task_id": task_id,
            "status": "created",
            "message": "Tarea creada y enviada a los agentes"
        }
    except Exception as e:
        logger.error(f"Error creando tarea: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/tasks/{task_id}")
async def get_task_status(task_id: str):
    """Obtener estado de una tarea"""
    try:
        task_status = await app.state.coordinator.get_task_status(task_id)
        return task_status
    except Exception as e:
        logger.error(f"Error obteniendo estado de tarea {task_id}: {e}")
        raise HTTPException(status_code=404, detail="Task not found")


@app.get("/agents")
async def list_agents():
    """Listar agentes disponibles y su estado"""
    try:
        agents_status = await app.state.coordinator.get_agents_status()
        return agents_status
    except Exception as e:
        logger.error(f"Error listando agentes: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/agents/{agent_name}/command")
async def send_agent_command(agent_name: str, command: dict):
    """Enviar comando directo a un agente específico"""
    try:
        result = await app.state.coordinator.send_agent_command(agent_name, command)
        return result
    except Exception as e:
        logger.error(f"Error enviando comando a agente {agent_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def main():
    """Función principal para ejecutar el orquestador"""
    logger.info("🎼 Iniciando SIAME 2026v3 Orchestrator")

    uvicorn.run(
        "src.backend.orchestrator.main:app",
        host=settings.ORCHESTRATOR_HOST,
        port=settings.ORCHESTRATOR_PORT,
        reload=settings.ENVIRONMENT == "development",
        log_level=settings.LOG_LEVEL.lower(),
        workers=1  # Single worker para mantener estado compartido
    )


if __name__ == "__main__":
    main()
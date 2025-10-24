#!/usr/bin/env python3
"""
SIAME 2026v3 - Coordinador de Agentes
Coordinación y gestión de agentes especializados
"""

import asyncio
import logging
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum

from .task_queue import TaskQueue
from .message_broker import MessageBroker
from .health_monitor import HealthMonitor
from ..shared.config import settings


logger = logging.getLogger(__name__)


class AgentType(Enum):
    """Tipos de agentes disponibles en el sistema"""
    DOCUMENT_PROCESSOR = "document_processor"
    DATABASE_MANAGER = "database_manager"
    AZURE_SPECIALIST = "azure_specialist"
    SECURITY_GUARDIAN = "security_guardian"
    WORKFLOW_MANAGER = "workflow_manager"
    COMMUNICATION_HUB = "communication_hub"
    QUALITY_ASSURANCE = "quality_assurance"


class TaskStatus(Enum):
    """Estados posibles de las tareas"""
    CREATED = "created"
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AgentCoordinator:
    """
    Coordinador principal de agentes para SIAME 2026v3

    Responsabilidades:
    - Gestión del ciclo de vida de los agentes
    - Distribución de tareas entre agentes
    - Coordinación de workflows diplomáticos
    - Monitoreo del estado del sistema
    """

    def __init__(self, task_queue: TaskQueue, message_broker: MessageBroker, health_monitor: HealthMonitor):
        self.task_queue = task_queue
        self.message_broker = message_broker
        self.health_monitor = health_monitor

        # Estado interno
        self.agents: Dict[str, Dict[str, Any]] = {}
        self.tasks: Dict[str, Dict[str, Any]] = {}
        self.workflows: Dict[str, Dict[str, Any]] = {}

        # Control de ejecución
        self._running = False
        self._coordination_task: Optional[asyncio.Task] = None

        logger.info("🎼 Coordinador de Agentes inicializado")

    async def initialize(self):
        """Inicializar el coordinador y registrar agentes"""
        logger.info("🔧 Inicializando coordinador de agentes")

        # Registrar agentes disponibles
        await self._register_agents()

        # Iniciar broker de mensajes
        await self.message_broker.initialize()

        # Configurar suscripciones de eventos
        await self._setup_event_subscriptions()

        # Iniciar loop de coordinación
        self._running = True
        self._coordination_task = asyncio.create_task(self._coordination_loop())

        logger.info("✅ Coordinador de agentes inicializado correctamente")

    async def shutdown(self):
        """Detener el coordinador y limpiar recursos"""
        logger.info("🛑 Deteniendo coordinador de agentes")

        self._running = False

        # Cancelar task de coordinación
        if self._coordination_task:
            self._coordination_task.cancel()
            try:
                await self._coordination_task
            except asyncio.CancelledError:
                pass

        # Detener agentes
        await self._shutdown_agents()

        # Cerrar broker de mensajes
        await self.message_broker.shutdown()

        logger.info("✅ Coordinador de agentes detenido")

    async def _register_agents(self):
        """Registrar todos los agentes disponibles"""
        agent_configs = [
            {
                "name": "document_processor",
                "type": AgentType.DOCUMENT_PROCESSOR,
                "description": "Procesamiento inteligente de documentos diplomáticos",
                "capabilities": ["ocr", "classification", "extraction", "validation"],
                "priority": 1
            },
            {
                "name": "database_manager",
                "type": AgentType.DATABASE_MANAGER,
                "description": "Gestión de base de datos y políticas de seguridad",
                "capabilities": ["crud", "migrations", "rls", "audit"],
                "priority": 2
            },
            {
                "name": "azure_specialist",
                "type": AgentType.AZURE_SPECIALIST,
                "description": "Integración con servicios de Microsoft Azure",
                "capabilities": ["form_recognizer", "blob_storage", "key_vault", "cognitive_services"],
                "priority": 1
            },
            {
                "name": "security_guardian",
                "type": AgentType.SECURITY_GUARDIAN,
                "description": "Guardián de seguridad y control de acceso",
                "capabilities": ["access_control", "encryption", "audit", "threat_detection"],
                "priority": 3
            },
            {
                "name": "workflow_manager",
                "type": AgentType.WORKFLOW_MANAGER,
                "description": "Gestión de flujos de trabajo diplomáticos",
                "capabilities": ["diplomatic_flows", "approvals", "status_tracking"],
                "priority": 2
            },
            {
                "name": "communication_hub",
                "type": AgentType.COMMUNICATION_HUB,
                "description": "Hub central de comunicaciones",
                "capabilities": ["email", "notifications", "diplomatic_protocol"],
                "priority": 2
            },
            {
                "name": "quality_assurance",
                "type": AgentType.QUALITY_ASSURANCE,
                "description": "Control de calidad y testing del sistema",
                "capabilities": ["testing", "compliance", "performance_monitoring"],
                "priority": 3
            }
        ]

        for config in agent_configs:
            await self._register_agent(config)

        logger.info(f"📋 Registrados {len(agent_configs)} agentes")

    async def _register_agent(self, config: Dict[str, Any]):
        """Registrar un agente individual"""
        agent_name = config["name"]

        self.agents[agent_name] = {
            "name": agent_name,
            "type": config["type"],
            "description": config["description"],
            "capabilities": config["capabilities"],
            "priority": config["priority"],
            "status": "registered",
            "last_heartbeat": None,
            "active_tasks": [],
            "completed_tasks": 0,
            "failed_tasks": 0,
            "registered_at": datetime.now()
        }

        logger.debug(f"🤖 Agente registrado: {agent_name}")

    async def _setup_event_subscriptions(self):
        """Configurar suscripciones a eventos del sistema"""
        # Suscribirse a eventos de agentes
        await self.message_broker.subscribe("agent.heartbeat", self._handle_agent_heartbeat)
        await self.message_broker.subscribe("agent.task_completed", self._handle_task_completed)
        await self.message_broker.subscribe("agent.task_failed", self._handle_task_failed)
        await self.message_broker.subscribe("agent.status_changed", self._handle_agent_status_changed)

        # Suscribirse a eventos de sistema
        await self.message_broker.subscribe("system.shutdown", self._handle_system_shutdown)

        logger.debug("📡 Suscripciones de eventos configuradas")

    async def _coordination_loop(self):
        """Loop principal de coordinación"""
        logger.info("🔄 Iniciando loop de coordinación")

        while self._running:
            try:
                # Procesar tareas pendientes
                await self._process_pending_tasks()

                # Verificar estado de agentes
                await self._check_agent_health()

                # Gestionar workflows activos
                await self._manage_active_workflows()

                # Limpiar tareas completadas antiguas
                await self._cleanup_old_tasks()

                # Esperar antes del siguiente ciclo
                await asyncio.sleep(settings.COORDINATION_INTERVAL)

            except Exception as e:
                logger.error(f"Error en loop de coordinación: {e}")
                await asyncio.sleep(1)

        logger.info("🔄 Loop de coordinación detenido")

    async def create_task(self, task_data: Dict[str, Any]) -> str:
        """Crear nueva tarea para procesamiento"""
        task_id = str(uuid.uuid4())

        task = {
            "id": task_id,
            "type": task_data.get("type", "unknown"),
            "data": task_data.get("data", {}),
            "priority": task_data.get("priority", 1),
            "status": TaskStatus.CREATED,
            "assigned_agent": None,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "attempts": 0,
            "max_attempts": task_data.get("max_attempts", 3),
            "metadata": task_data.get("metadata", {})
        }

        self.tasks[task_id] = task

        # Encolar tarea para procesamiento
        await self.task_queue.enqueue(task)

        logger.info(f"📝 Tarea creada: {task_id} ({task['type']})")
        return task_id

    async def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Obtener estado de una tarea"""
        if task_id not in self.tasks:
            raise ValueError(f"Tarea no encontrada: {task_id}")

        task = self.tasks[task_id]
        return {
            "id": task["id"],
            "type": task["type"],
            "status": task["status"].value,
            "assigned_agent": task["assigned_agent"],
            "created_at": task["created_at"].isoformat(),
            "updated_at": task["updated_at"].isoformat(),
            "attempts": task["attempts"],
            "metadata": task["metadata"]
        }

    async def get_agents_status(self) -> List[Dict[str, Any]]:
        """Obtener estado de todos los agentes"""
        return [
            {
                "name": agent["name"],
                "type": agent["type"].value,
                "status": agent["status"],
                "capabilities": agent["capabilities"],
                "active_tasks": len(agent["active_tasks"]),
                "completed_tasks": agent["completed_tasks"],
                "failed_tasks": agent["failed_tasks"],
                "last_heartbeat": agent["last_heartbeat"].isoformat() if agent["last_heartbeat"] else None
            }
            for agent in self.agents.values()
        ]

    async def send_agent_command(self, agent_name: str, command: Dict[str, Any]) -> Dict[str, Any]:
        """Enviar comando directo a un agente"""
        if agent_name not in self.agents:
            raise ValueError(f"Agente no encontrado: {agent_name}")

        # Enviar comando a través del broker de mensajes
        result = await self.message_broker.send_command(f"agent.{agent_name}", command)

        logger.info(f"📡 Comando enviado a {agent_name}: {command.get('action', 'unknown')}")
        return result

    async def _process_pending_tasks(self):
        """Procesar tareas pendientes en la cola"""
        while not self.task_queue.is_empty():
            task = await self.task_queue.dequeue()
            if task:
                await self._assign_task_to_agent(task)

    async def _assign_task_to_agent(self, task: Dict[str, Any]):
        """Asignar tarea a un agente apropiado"""
        # Encontrar agente apropiado basado en el tipo de tarea
        suitable_agents = self._find_suitable_agents(task["type"])

        if not suitable_agents:
            logger.warning(f"No se encontró agente apropiado para tarea {task['id']}")
            task["status"] = TaskStatus.FAILED
            return

        # Seleccionar agente con menor carga
        selected_agent = min(suitable_agents, key=lambda a: len(self.agents[a]["active_tasks"]))

        # Asignar tarea
        task["assigned_agent"] = selected_agent
        task["status"] = TaskStatus.PROCESSING
        task["updated_at"] = datetime.now()

        self.agents[selected_agent]["active_tasks"].append(task["id"])

        # Enviar tarea al agente
        await self.message_broker.send_task(f"agent.{selected_agent}", task)

        logger.info(f"📋 Tarea {task['id']} asignada a {selected_agent}")

    def _find_suitable_agents(self, task_type: str) -> List[str]:
        """Encontrar agentes apropiados para un tipo de tarea"""
        # Mapeo de tipos de tarea a agentes
        task_agent_mapping = {
            "document_processing": ["document_processor", "azure_specialist"],
            "database_operation": ["database_manager"],
            "security_check": ["security_guardian"],
            "workflow_execution": ["workflow_manager"],
            "notification": ["communication_hub"],
            "quality_check": ["quality_assurance"]
        }

        suitable_agents = task_agent_mapping.get(task_type, [])
        # Filtrar solo agentes activos
        return [agent for agent in suitable_agents if self.agents.get(agent, {}).get("status") == "active"]

    async def _check_agent_health(self):
        """Verificar salud de los agentes"""
        current_time = datetime.now()

        for agent_name, agent in self.agents.items():
            if agent["last_heartbeat"]:
                time_since_heartbeat = current_time - agent["last_heartbeat"]
                if time_since_heartbeat.total_seconds() > settings.AGENT_HEARTBEAT_TIMEOUT:
                    logger.warning(f"⚠️ Agente {agent_name} no responde")
                    agent["status"] = "unresponsive"

    async def _manage_active_workflows(self):
        """Gestionar workflows activos"""
        # Implementar lógica de gestión de workflows
        pass

    async def _cleanup_old_tasks(self):
        """Limpiar tareas completadas antiguas"""
        current_time = datetime.now()
        cleanup_threshold = settings.TASK_CLEANUP_THRESHOLD_HOURS

        tasks_to_remove = []
        for task_id, task in self.tasks.items():
            if task["status"] in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
                age = current_time - task["updated_at"]
                if age.total_seconds() > cleanup_threshold * 3600:
                    tasks_to_remove.append(task_id)

        for task_id in tasks_to_remove:
            del self.tasks[task_id]

        if tasks_to_remove:
            logger.debug(f"🧹 Limpiadas {len(tasks_to_remove)} tareas antiguas")

    async def _handle_agent_heartbeat(self, event_data: Dict[str, Any]):
        """Manejar heartbeat de agente"""
        agent_name = event_data.get("agent_name")
        if agent_name in self.agents:
            self.agents[agent_name]["last_heartbeat"] = datetime.now()
            self.agents[agent_name]["status"] = "active"

    async def _handle_task_completed(self, event_data: Dict[str, Any]):
        """Manejar finalización exitosa de tarea"""
        task_id = event_data.get("task_id")
        agent_name = event_data.get("agent_name")

        if task_id in self.tasks:
            self.tasks[task_id]["status"] = TaskStatus.COMPLETED
            self.tasks[task_id]["updated_at"] = datetime.now()

        if agent_name in self.agents:
            if task_id in self.agents[agent_name]["active_tasks"]:
                self.agents[agent_name]["active_tasks"].remove(task_id)
            self.agents[agent_name]["completed_tasks"] += 1

        logger.info(f"✅ Tarea completada: {task_id} por {agent_name}")

    async def _handle_task_failed(self, event_data: Dict[str, Any]):
        """Manejar fallo de tarea"""
        task_id = event_data.get("task_id")
        agent_name = event_data.get("agent_name")
        error = event_data.get("error")

        if task_id in self.tasks:
            task = self.tasks[task_id]
            task["attempts"] += 1

            if task["attempts"] >= task["max_attempts"]:
                task["status"] = TaskStatus.FAILED
                logger.error(f"❌ Tarea falló definitivamente: {task_id} - {error}")
            else:
                # Reencolar para reintentar
                task["status"] = TaskStatus.QUEUED
                await self.task_queue.enqueue(task)
                logger.warning(f"🔄 Reintentando tarea: {task_id} (intento {task['attempts']})")

            task["updated_at"] = datetime.now()

        if agent_name in self.agents:
            if task_id in self.agents[agent_name]["active_tasks"]:
                self.agents[agent_name]["active_tasks"].remove(task_id)
            self.agents[agent_name]["failed_tasks"] += 1

    async def _handle_agent_status_changed(self, event_data: Dict[str, Any]):
        """Manejar cambio de estado de agente"""
        agent_name = event_data.get("agent_name")
        new_status = event_data.get("status")

        if agent_name in self.agents:
            self.agents[agent_name]["status"] = new_status
            logger.info(f"🔄 Estado de agente cambiado: {agent_name} -> {new_status}")

    async def _handle_system_shutdown(self, event_data: Dict[str, Any]):
        """Manejar shutdown del sistema"""
        logger.info("🛑 Recibida señal de shutdown del sistema")
        await self.shutdown()

    async def _shutdown_agents(self):
        """Detener todos los agentes"""
        for agent_name in self.agents.keys():
            try:
                await self.message_broker.send_command(f"agent.{agent_name}", {"action": "shutdown"})
            except Exception as e:
                logger.error(f"Error deteniendo agente {agent_name}: {e}")

        logger.info("🤖 Agentes detenidos")
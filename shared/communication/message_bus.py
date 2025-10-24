#!/usr/bin/env python3
"""
SIAME 2026v3 - Message Bus System
Sistema nervioso central que conecta todos los subagentes de SIAME

Este módulo implementa:
1. Queue asíncrono para distribución de tareas
2. Sistema Pub/Sub para eventos del sistema
3. Contexto compartido entre agentes
4. Logging centralizado y monitoreo
5. Manejo de errores y reintento automático de tareas
6. Comunicación bidireccional entre agentes
7. Persistencia de mensajes críticos
"""

import asyncio
import logging
import json
import uuid
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Union, Set
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
from collections import defaultdict, deque
import weakref
import pickle
import gzip

# Importaciones para persistencia
try:
    import aioredis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

try:
    import aiosqlite
    SQLITE_AVAILABLE = True
except ImportError:
    SQLITE_AVAILABLE = False


class MessageType(Enum):
    """Tipos de mensajes del sistema"""
    TASK = "task"                    # Tarea para procesar
    EVENT = "event"                  # Evento del sistema
    RESPONSE = "response"            # Respuesta a una tarea
    NOTIFICATION = "notification"    # Notificación general
    HEARTBEAT = "heartbeat"          # Señal de vida de agente
    ERROR = "error"                  # Error o excepción
    COMMAND = "command"              # Comando de control
    STATUS_UPDATE = "status_update"  # Actualización de estado


class MessagePriority(Enum):
    """Prioridades de mensajes"""
    CRITICAL = 1    # Crítico - Procesar inmediatamente
    HIGH = 2        # Alta - Procesar antes que normal
    NORMAL = 3      # Normal - Prioridad estándar
    LOW = 4         # Baja - Procesar cuando sea posible
    BACKGROUND = 5  # Fondo - Procesar en tiempo libre


class EventType(Enum):
    """Tipos de eventos del sistema"""
    AGENT_REGISTERED = "agent_registered"
    AGENT_DISCONNECTED = "agent_disconnected"
    TASK_STARTED = "task_started"
    TASK_COMPLETED = "task_completed"
    TASK_FAILED = "task_failed"
    DOCUMENT_PROCESSED = "document_processed"
    SYSTEM_ERROR = "system_error"
    SECURITY_ALERT = "security_alert"
    PERFORMANCE_WARNING = "performance_warning"
    WORKFLOW_STARTED = "workflow_started"
    WORKFLOW_COMPLETED = "workflow_completed"


@dataclass
class Message:
    """Mensaje base del sistema"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    type: MessageType = MessageType.TASK
    priority: MessagePriority = MessagePriority.NORMAL
    sender_id: str = ""
    recipient_id: Optional[str] = None  # None = broadcast
    topic: Optional[str] = None
    payload: Dict[str, Any] = field(default_factory=dict)
    headers: Dict[str, str] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    retry_count: int = 0
    max_retries: int = 3
    correlation_id: Optional[str] = None
    reply_to: Optional[str] = None
    trace_id: Optional[str] = None


@dataclass
class Task:
    """Tarea específica para procesamiento"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    task_type: str = ""
    description: str = ""
    agent_type: Optional[str] = None  # Tipo de agente requerido
    input_data: Dict[str, Any] = field(default_factory=dict)
    output_data: Dict[str, Any] = field(default_factory=dict)
    status: str = "pending"  # pending, running, completed, failed
    priority: MessagePriority = MessagePriority.NORMAL
    timeout_seconds: int = 300
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    assigned_agent_id: Optional[str] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    dependencies: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Event:
    """Evento del sistema"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_type: EventType
    source_agent_id: str
    event_data: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    severity: str = "info"  # debug, info, warning, error, critical
    tags: List[str] = field(default_factory=list)
    correlation_id: Optional[str] = None


@dataclass
class AgentContext:
    """Contexto compartido de un agente"""
    agent_id: str
    agent_type: str
    agent_name: str
    status: str = "active"  # active, busy, idle, offline
    capabilities: List[str] = field(default_factory=list)
    current_tasks: List[str] = field(default_factory=list)
    load_factor: float = 0.0  # 0.0 = libre, 1.0 = completamente ocupado
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    last_heartbeat: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


class SharedContext:
    """Contexto compartido entre todos los agentes"""

    def __init__(self):
        self.agents: Dict[str, AgentContext] = {}
        self.global_state: Dict[str, Any] = {}
        self.workflow_states: Dict[str, Dict[str, Any]] = {}
        self.system_metrics: Dict[str, Any] = {
            "total_messages": 0,
            "total_tasks": 0,
            "total_events": 0,
            "active_agents": 0,
            "system_load": 0.0
        }
        self._lock = asyncio.Lock()

    async def register_agent(self, context: AgentContext) -> None:
        """Registra un agente en el contexto compartido"""
        async with self._lock:
            self.agents[context.agent_id] = context
            self.system_metrics["active_agents"] = len([
                a for a in self.agents.values() if a.status != "offline"
            ])

    async def unregister_agent(self, agent_id: str) -> None:
        """Desregistra un agente del contexto compartido"""
        async with self._lock:
            if agent_id in self.agents:
                self.agents[agent_id].status = "offline"
                self.system_metrics["active_agents"] = len([
                    a for a in self.agents.values() if a.status != "offline"
                ])

    async def update_agent_status(self, agent_id: str, status: str, metadata: Optional[Dict] = None) -> None:
        """Actualiza el estado de un agente"""
        async with self._lock:
            if agent_id in self.agents:
                self.agents[agent_id].status = status
                self.agents[agent_id].last_heartbeat = datetime.now()
                if metadata:
                    self.agents[agent_id].metadata.update(metadata)

    async def get_available_agents(self, agent_type: Optional[str] = None) -> List[AgentContext]:
        """Obtiene agentes disponibles para procesamiento"""
        async with self._lock:
            available = []
            for agent in self.agents.values():
                if agent.status in ["active", "idle"] and agent.load_factor < 0.8:
                    if agent_type is None or agent.agent_type == agent_type:
                        available.append(agent)
            return available

    async def set_global_state(self, key: str, value: Any) -> None:
        """Establece una variable global del sistema"""
        async with self._lock:
            self.global_state[key] = value

    async def get_global_state(self, key: str, default: Any = None) -> Any:
        """Obtiene una variable global del sistema"""
        async with self._lock:
            return self.global_state.get(key, default)

    async def update_workflow_state(self, workflow_id: str, state: Dict[str, Any]) -> None:
        """Actualiza el estado de un workflow"""
        async with self._lock:
            if workflow_id not in self.workflow_states:
                self.workflow_states[workflow_id] = {}
            self.workflow_states[workflow_id].update(state)

    async def get_workflow_state(self, workflow_id: str) -> Dict[str, Any]:
        """Obtiene el estado de un workflow"""
        async with self._lock:
            return self.workflow_states.get(workflow_id, {})


class MessageQueue:
    """Cola de mensajes asíncrona con prioridades"""

    def __init__(self, max_size: int = 10000):
        self.max_size = max_size
        self.queues = {
            MessagePriority.CRITICAL: asyncio.Queue(maxsize=max_size),
            MessagePriority.HIGH: asyncio.Queue(maxsize=max_size),
            MessagePriority.NORMAL: asyncio.Queue(maxsize=max_size),
            MessagePriority.LOW: asyncio.Queue(maxsize=max_size),
            MessagePriority.BACKGROUND: asyncio.Queue(maxsize=max_size)
        }
        self.message_history = deque(maxlen=1000)
        self._stats = {
            "messages_queued": 0,
            "messages_processed": 0,
            "messages_failed": 0
        }

    async def put(self, message: Message) -> bool:
        """Coloca un mensaje en la cola apropiada"""
        try:
            queue = self.queues[message.priority]

            # Verificar si la cola está llena
            if queue.full():
                # Para mensajes críticos, intentar hacer espacio
                if message.priority == MessagePriority.CRITICAL:
                    # Descartar mensaje de menor prioridad si es posible
                    await self._make_room_for_critical(message)
                else:
                    return False

            await queue.put(message)
            self.message_history.append({
                "id": message.id,
                "type": message.type.value,
                "priority": message.priority.value,
                "timestamp": message.timestamp,
                "action": "queued"
            })
            self._stats["messages_queued"] += 1
            return True

        except Exception as e:
            logging.error(f"Error putting message in queue: {e}")
            return False

    async def get(self, timeout: Optional[float] = None) -> Optional[Message]:
        """Obtiene el siguiente mensaje de mayor prioridad"""
        try:
            # Intentar obtener mensajes en orden de prioridad
            for priority in MessagePriority:
                queue = self.queues[priority]
                if not queue.empty():
                    try:
                        message = await asyncio.wait_for(queue.get(), timeout=0.1)
                        self.message_history.append({
                            "id": message.id,
                            "type": message.type.value,
                            "priority": message.priority.value,
                            "timestamp": datetime.now(),
                            "action": "dequeued"
                        })
                        return message
                    except asyncio.TimeoutError:
                        continue

            # Si no hay mensajes de alta prioridad, esperar por cualquiera
            if timeout:
                tasks = [
                    asyncio.create_task(queue.get())
                    for queue in self.queues.values()
                ]

                try:
                    done, pending = await asyncio.wait(
                        tasks, timeout=timeout, return_when=asyncio.FIRST_COMPLETED
                    )

                    # Cancelar tareas pendientes
                    for task in pending:
                        task.cancel()

                    if done:
                        message = done.pop().result()
                        return message

                except asyncio.TimeoutError:
                    pass

            return None

        except Exception as e:
            logging.error(f"Error getting message from queue: {e}")
            return None

    async def size(self) -> Dict[str, int]:
        """Obtiene el tamaño de cada cola de prioridad"""
        return {
            priority.name: self.queues[priority].qsize()
            for priority in MessagePriority
        }

    async def stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas de la cola"""
        sizes = await self.size()
        return {
            **self._stats,
            "queue_sizes": sizes,
            "total_queued": sum(sizes.values()),
            "history_size": len(self.message_history)
        }

    async def _make_room_for_critical(self, critical_message: Message) -> None:
        """Hace espacio para un mensaje crítico descartando mensajes de menor prioridad"""
        try:
            # Intentar descartar un mensaje de baja prioridad
            for priority in [MessagePriority.BACKGROUND, MessagePriority.LOW]:
                queue = self.queues[priority]
                if not queue.empty():
                    try:
                        discarded = await asyncio.wait_for(queue.get(), timeout=0.1)
                        logging.warning(f"Discarded low priority message {discarded.id} for critical message")
                        return
                    except asyncio.TimeoutError:
                        continue
        except Exception as e:
            logging.error(f"Error making room for critical message: {e}")


class EventBus:
    """Sistema Pub/Sub para eventos del sistema"""

    def __init__(self):
        self.subscribers: Dict[str, Set[Callable]] = defaultdict(set)
        self.wildcard_subscribers: Set[Callable] = set()
        self.event_history = deque(maxlen=1000)
        self._stats = {
            "events_published": 0,
            "events_delivered": 0,
            "subscription_count": 0
        }

    async def subscribe(self, topic: str, callback: Callable[[Event], None]) -> str:
        """Suscribirse a un topic específico"""
        subscription_id = str(uuid.uuid4())

        if topic == "*":
            self.wildcard_subscribers.add(callback)
        else:
            self.subscribers[topic].add(callback)

        self._stats["subscription_count"] += 1
        logging.debug(f"New subscription to topic '{topic}': {subscription_id}")
        return subscription_id

    async def unsubscribe(self, topic: str, callback: Callable) -> bool:
        """Cancelar suscripción a un topic"""
        try:
            if topic == "*":
                self.wildcard_subscribers.discard(callback)
            else:
                self.subscribers[topic].discard(callback)

            self._stats["subscription_count"] -= 1
            return True
        except Exception as e:
            logging.error(f"Error unsubscribing from topic '{topic}': {e}")
            return False

    async def publish(self, event: Event, topic: Optional[str] = None) -> int:
        """Publica un evento a los suscriptores"""
        try:
            if topic is None:
                topic = event.event_type.value

            # Agregar a historial
            self.event_history.append({
                "id": event.id,
                "type": event.event_type.value,
                "topic": topic,
                "source": event.source_agent_id,
                "timestamp": event.timestamp,
                "severity": event.severity
            })

            self._stats["events_published"] += 1
            delivered_count = 0

            # Notificar suscriptores específicos del topic
            if topic in self.subscribers:
                for callback in self.subscribers[topic].copy():
                    try:
                        if asyncio.iscoroutinefunction(callback):
                            await callback(event)
                        else:
                            callback(event)
                        delivered_count += 1
                    except Exception as e:
                        logging.error(f"Error delivering event to subscriber: {e}")

            # Notificar suscriptores wildcard
            for callback in self.wildcard_subscribers.copy():
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(event)
                    else:
                        callback(event)
                    delivered_count += 1
                except Exception as e:
                    logging.error(f"Error delivering event to wildcard subscriber: {e}")

            self._stats["events_delivered"] += delivered_count
            return delivered_count

        except Exception as e:
            logging.error(f"Error publishing event: {e}")
            return 0

    async def get_topics(self) -> List[str]:
        """Obtiene lista de topics activos"""
        return list(self.subscribers.keys())

    async def stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas del bus de eventos"""
        return {
            **self._stats,
            "active_topics": len(self.subscribers),
            "wildcard_subscribers": len(self.wildcard_subscribers),
            "history_size": len(self.event_history)
        }


class ErrorHandler:
    """Maneja errores y reintentos de tareas"""

    def __init__(self, max_retry_delay: int = 300):
        self.max_retry_delay = max_retry_delay
        self.failed_tasks: Dict[str, Task] = {}
        self.retry_schedule: Dict[str, datetime] = {}
        self.error_patterns: Dict[str, int] = defaultdict(int)

    async def handle_task_error(self, task: Task, error: Exception) -> bool:
        """Maneja error de una tarea y decide si reintentar"""
        try:
            task.retry_count += 1
            task.error_message = str(error)

            # Registrar patrón de error
            error_type = type(error).__name__
            self.error_patterns[error_type] += 1

            # Decidir si reintentar
            if task.retry_count <= task.max_retries:
                # Calcular delay exponencial con jitter
                delay = min(
                    (2 ** task.retry_count) + (time.time() % 1),
                    self.max_retry_delay
                )

                retry_time = datetime.now() + timedelta(seconds=delay)
                self.retry_schedule[task.id] = retry_time

                logging.warning(
                    f"Task {task.id} failed (attempt {task.retry_count}/{task.max_retries}), "
                    f"retrying in {delay:.1f}s. Error: {error}"
                )
                return True
            else:
                # Máximo de reintentos alcanzado
                task.status = "failed"
                self.failed_tasks[task.id] = task

                logging.error(
                    f"Task {task.id} permanently failed after {task.retry_count} attempts. "
                    f"Final error: {error}"
                )
                return False

        except Exception as e:
            logging.error(f"Error in error handler: {e}")
            return False

    async def get_retry_tasks(self) -> List[Task]:
        """Obtiene tareas listas para reintentar"""
        now = datetime.now()
        ready_tasks = []

        for task_id, retry_time in list(self.retry_schedule.items()):
            if now >= retry_time:
                if task_id in self.failed_tasks:
                    task = self.failed_tasks.pop(task_id)
                    task.status = "pending"
                    ready_tasks.append(task)
                del self.retry_schedule[task_id]

        return ready_tasks

    async def get_error_statistics(self) -> Dict[str, Any]:
        """Obtiene estadísticas de errores"""
        return {
            "failed_tasks_count": len(self.failed_tasks),
            "pending_retries": len(self.retry_schedule),
            "error_patterns": dict(self.error_patterns),
            "total_errors": sum(self.error_patterns.values())
        }


class MessageBus:
    """Sistema de comunicación central para SIAME 2026v3"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)

        # Componentes principales
        self.message_queue = MessageQueue(
            max_size=self.config.get("queue_max_size", 10000)
        )
        self.event_bus = EventBus()
        self.shared_context = SharedContext()
        self.error_handler = ErrorHandler(
            max_retry_delay=self.config.get("max_retry_delay", 300)
        )

        # Almacenamiento de tareas
        self.active_tasks: Dict[str, Task] = {}
        self.task_callbacks: Dict[str, List[Callable]] = defaultdict(list)

        # Conexiones de agentes
        self.agent_connections: Dict[str, weakref.ReferenceType] = {}

        # Estado del sistema
        self.is_running = False
        self.worker_tasks: List[asyncio.Task] = []

        # Persistencia (opcional)
        self.persistence_enabled = self.config.get("persistence_enabled", False)
        self.redis_client = None
        self.sqlite_path = self.config.get("sqlite_path", "siame_message_bus.db")

        # Estadísticas globales
        self.global_stats = {
            "start_time": datetime.now(),
            "total_messages": 0,
            "total_tasks": 0,
            "total_events": 0,
            "total_agents": 0
        }

    async def initialize(self) -> bool:
        """Inicializa el message bus"""
        try:
            self.logger.info("Inicializando SIAME Message Bus...")

            # Configurar persistencia si está habilitada
            if self.persistence_enabled:
                await self._setup_persistence()

            # Iniciar workers
            self.is_running = True
            self.worker_tasks = [
                asyncio.create_task(self._message_processor()),
                asyncio.create_task(self._retry_scheduler()),
                asyncio.create_task(self._heartbeat_monitor()),
                asyncio.create_task(self._stats_collector())
            ]

            self.logger.info("Message Bus inicializado exitosamente")
            return True

        except Exception as e:
            self.logger.error(f"Error inicializando Message Bus: {e}")
            return False

    async def shutdown(self) -> None:
        """Cierra el message bus ordenadamente"""
        try:
            self.logger.info("Cerrando Message Bus...")

            self.is_running = False

            # Cancelar workers
            for task in self.worker_tasks:
                task.cancel()

            # Esperar que terminen
            await asyncio.gather(*self.worker_tasks, return_exceptions=True)

            # Persistir estado si está habilitado
            if self.persistence_enabled:
                await self._persist_state()

            # Cerrar conexiones
            if self.redis_client:
                await self.redis_client.close()

            self.logger.info("Message Bus cerrado")

        except Exception as e:
            self.logger.error(f"Error cerrando Message Bus: {e}")

    # API de Agentes

    async def register_agent(self, agent_id: str, agent_type: str, agent_name: str,
                           capabilities: List[str] = None) -> bool:
        """Registra un agente en el sistema"""
        try:
            context = AgentContext(
                agent_id=agent_id,
                agent_type=agent_type,
                agent_name=agent_name,
                capabilities=capabilities or []
            )

            await self.shared_context.register_agent(context)

            # Publicar evento
            event = Event(
                event_type=EventType.AGENT_REGISTERED,
                source_agent_id=agent_id,
                event_data={"agent_type": agent_type, "agent_name": agent_name}
            )
            await self.event_bus.publish(event)

            self.global_stats["total_agents"] += 1
            self.logger.info(f"Agente registrado: {agent_name} ({agent_type}) - {agent_id}")
            return True

        except Exception as e:
            self.logger.error(f"Error registrando agente {agent_id}: {e}")
            return False

    async def unregister_agent(self, agent_id: str) -> bool:
        """Desregistra un agente del sistema"""
        try:
            await self.shared_context.unregister_agent(agent_id)

            # Publicar evento
            event = Event(
                event_type=EventType.AGENT_DISCONNECTED,
                source_agent_id=agent_id,
                event_data={"reason": "unregistered"}
            )
            await self.event_bus.publish(event)

            # Limpiar conexión
            if agent_id in self.agent_connections:
                del self.agent_connections[agent_id]

            self.logger.info(f"Agente desregistrado: {agent_id}")
            return True

        except Exception as e:
            self.logger.error(f"Error desregistrando agente {agent_id}: {e}")
            return False

    # API de Tareas

    async def submit_task(self, task: Task, callback: Optional[Callable] = None) -> bool:
        """Envía una tarea al sistema"""
        try:
            # Almacenar tarea
            self.active_tasks[task.id] = task

            # Registrar callback si se proporciona
            if callback:
                self.task_callbacks[task.id].append(callback)

            # Crear mensaje de tarea
            message = Message(
                type=MessageType.TASK,
                priority=task.priority,
                sender_id="system",
                payload=asdict(task),
                correlation_id=task.id
            )

            # Enviar a cola
            success = await self.message_queue.put(message)

            if success:
                # Publicar evento
                event = Event(
                    event_type=EventType.TASK_STARTED,
                    source_agent_id="system",
                    event_data={"task_id": task.id, "task_type": task.task_type}
                )
                await self.event_bus.publish(event)

                self.global_stats["total_tasks"] += 1
                self.logger.debug(f"Tarea enviada: {task.id} ({task.task_type})")

            return success

        except Exception as e:
            self.logger.error(f"Error enviando tarea {task.id}: {e}")
            return False

    async def complete_task(self, task_id: str, result: Dict[str, Any],
                          agent_id: str) -> bool:
        """Marca una tarea como completada"""
        try:
            if task_id in self.active_tasks:
                task = self.active_tasks[task_id]
                task.status = "completed"
                task.completed_at = datetime.now()
                task.output_data = result

                # Ejecutar callbacks
                for callback in self.task_callbacks.get(task_id, []):
                    try:
                        if asyncio.iscoroutinefunction(callback):
                            await callback(task)
                        else:
                            callback(task)
                    except Exception as e:
                        self.logger.error(f"Error in task callback: {e}")

                # Publicar evento
                event = Event(
                    event_type=EventType.TASK_COMPLETED,
                    source_agent_id=agent_id,
                    event_data={"task_id": task_id, "result": result}
                )
                await self.event_bus.publish(event)

                # Limpiar
                del self.active_tasks[task_id]
                if task_id in self.task_callbacks:
                    del self.task_callbacks[task_id]

                self.logger.debug(f"Tarea completada: {task_id}")
                return True

            return False

        except Exception as e:
            self.logger.error(f"Error completando tarea {task_id}: {e}")
            return False

    async def fail_task(self, task_id: str, error: Exception, agent_id: str) -> bool:
        """Marca una tarea como fallida y maneja reintento"""
        try:
            if task_id in self.active_tasks:
                task = self.active_tasks[task_id]

                # Manejar error y decidir reintento
                should_retry = await self.error_handler.handle_task_error(task, error)

                if not should_retry:
                    # Tarea permanentemente fallida
                    event = Event(
                        event_type=EventType.TASK_FAILED,
                        source_agent_id=agent_id,
                        event_data={
                            "task_id": task_id,
                            "error": str(error),
                            "retry_count": task.retry_count
                        },
                        severity="error"
                    )
                    await self.event_bus.publish(event)

                    # Ejecutar callbacks
                    for callback in self.task_callbacks.get(task_id, []):
                        try:
                            if asyncio.iscoroutinefunction(callback):
                                await callback(task)
                            else:
                                callback(task)
                        except Exception as e:
                            self.logger.error(f"Error in task failure callback: {e}")

                    # Limpiar
                    del self.active_tasks[task_id]
                    if task_id in self.task_callbacks:
                        del self.task_callbacks[task_id]

                return True

            return False

        except Exception as e:
            self.logger.error(f"Error fallando tarea {task_id}: {e}")
            return False

    # API de Eventos

    async def subscribe_to_events(self, topic: str, callback: Callable[[Event], None]) -> str:
        """Suscribirse a eventos del sistema"""
        return await self.event_bus.subscribe(topic, callback)

    async def unsubscribe_from_events(self, topic: str, callback: Callable) -> bool:
        """Cancelar suscripción a eventos"""
        return await self.event_bus.unsubscribe(topic, callback)

    async def publish_event(self, event: Event, topic: Optional[str] = None) -> int:
        """Publicar un evento en el sistema"""
        delivered = await self.event_bus.publish(event, topic)
        self.global_stats["total_events"] += 1
        return delivered

    # API de Contexto Compartido

    async def update_agent_status(self, agent_id: str, status: str, metadata: Optional[Dict] = None) -> None:
        """Actualiza el estado de un agente"""
        await self.shared_context.update_agent_status(agent_id, status, metadata)

    async def get_available_agents(self, agent_type: Optional[str] = None) -> List[AgentContext]:
        """Obtiene agentes disponibles"""
        return await self.shared_context.get_available_agents(agent_type)

    async def set_global_state(self, key: str, value: Any) -> None:
        """Establece estado global"""
        await self.shared_context.set_global_state(key, value)

    async def get_global_state(self, key: str, default: Any = None) -> Any:
        """Obtiene estado global"""
        return await self.shared_context.get_global_state(key, default)

    # API de Monitoreo

    async def get_system_statistics(self) -> Dict[str, Any]:
        """Obtiene estadísticas completas del sistema"""
        queue_stats = await self.message_queue.stats()
        event_stats = await self.event_bus.stats()
        error_stats = await self.error_handler.get_error_statistics()

        return {
            "global_stats": self.global_stats,
            "queue_stats": queue_stats,
            "event_stats": event_stats,
            "error_stats": error_stats,
            "active_tasks": len(self.active_tasks),
            "system_uptime": (datetime.now() - self.global_stats["start_time"]).total_seconds(),
            "context_stats": {
                "active_agents": len([
                    a for a in self.shared_context.agents.values()
                    if a.status != "offline"
                ]),
                "total_agents": len(self.shared_context.agents),
                "workflows_active": len(self.shared_context.workflow_states)
            }
        }

    async def get_agent_status(self, agent_id: str) -> Optional[AgentContext]:
        """Obtiene el estado de un agente específico"""
        return self.shared_context.agents.get(agent_id)

    async def get_task_status(self, task_id: str) -> Optional[Task]:
        """Obtiene el estado de una tarea"""
        return self.active_tasks.get(task_id)

    # Workers internos

    async def _message_processor(self) -> None:
        """Procesa mensajes de la cola"""
        while self.is_running:
            try:
                message = await self.message_queue.get(timeout=1.0)
                if message:
                    await self._handle_message(message)
                    self.global_stats["total_messages"] += 1

            except asyncio.TimeoutError:
                continue
            except Exception as e:
                self.logger.error(f"Error en procesador de mensajes: {e}")
                await asyncio.sleep(1.0)

    async def _handle_message(self, message: Message) -> None:
        """Maneja un mensaje específico"""
        try:
            if message.type == MessageType.TASK:
                await self._handle_task_message(message)
            elif message.type == MessageType.RESPONSE:
                await self._handle_response_message(message)
            elif message.type == MessageType.HEARTBEAT:
                await self._handle_heartbeat_message(message)
            # Agregar más tipos según sea necesario

        except Exception as e:
            self.logger.error(f"Error manejando mensaje {message.id}: {e}")

    async def _handle_task_message(self, message: Message) -> None:
        """Maneja un mensaje de tarea"""
        try:
            task_data = message.payload
            task = Task(**task_data)

            # Encontrar agente apropiado
            available_agents = await self.shared_context.get_available_agents(task.agent_type)

            if available_agents:
                # Seleccionar agente con menor carga
                selected_agent = min(available_agents, key=lambda a: a.load_factor)

                # Asignar tarea
                task.assigned_agent_id = selected_agent.agent_id
                task.started_at = datetime.now()
                task.status = "running"

                # Actualizar contexto del agente
                selected_agent.current_tasks.append(task.id)
                selected_agent.load_factor = len(selected_agent.current_tasks) / 5.0  # Asumir max 5 tareas

                self.logger.debug(f"Tarea {task.id} asignada a agente {selected_agent.agent_id}")

            else:
                # No hay agentes disponibles, reencolar
                await asyncio.sleep(1.0)
                await self.message_queue.put(message)

        except Exception as e:
            self.logger.error(f"Error manejando mensaje de tarea: {e}")

    async def _handle_response_message(self, message: Message) -> None:
        """Maneja un mensaje de respuesta"""
        # TODO: Implementar manejo de respuestas
        pass

    async def _handle_heartbeat_message(self, message: Message) -> None:
        """Maneja un mensaje de heartbeat"""
        try:
            agent_id = message.sender_id
            await self.shared_context.update_agent_status(
                agent_id, "active", {"last_heartbeat": datetime.now()}
            )
        except Exception as e:
            self.logger.error(f"Error manejando heartbeat: {e}")

    async def _retry_scheduler(self) -> None:
        """Programa reintentos de tareas fallidas"""
        while self.is_running:
            try:
                retry_tasks = await self.error_handler.get_retry_tasks()

                for task in retry_tasks:
                    await self.submit_task(task)

                await asyncio.sleep(10)  # Verificar cada 10 segundos

            except Exception as e:
                self.logger.error(f"Error en programador de reintentos: {e}")
                await asyncio.sleep(10)

    async def _heartbeat_monitor(self) -> None:
        """Monitorea heartbeats de agentes"""
        while self.is_running:
            try:
                now = datetime.now()
                timeout_threshold = timedelta(minutes=2)

                for agent_id, agent in self.shared_context.agents.items():
                    if agent.status != "offline":
                        time_since_heartbeat = now - agent.last_heartbeat

                        if time_since_heartbeat > timeout_threshold:
                            await self.shared_context.update_agent_status(agent_id, "offline")

                            event = Event(
                                event_type=EventType.AGENT_DISCONNECTED,
                                source_agent_id=agent_id,
                                event_data={"reason": "heartbeat_timeout"},
                                severity="warning"
                            )
                            await self.event_bus.publish(event)

                await asyncio.sleep(30)  # Verificar cada 30 segundos

            except Exception as e:
                self.logger.error(f"Error en monitor de heartbeat: {e}")
                await asyncio.sleep(30)

    async def _stats_collector(self) -> None:
        """Recolecta estadísticas del sistema"""
        while self.is_running:
            try:
                # Actualizar métricas del contexto compartido
                self.shared_context.system_metrics.update({
                    "total_messages": self.global_stats["total_messages"],
                    "total_tasks": self.global_stats["total_tasks"],
                    "total_events": self.global_stats["total_events"],
                    "active_agents": len([
                        a for a in self.shared_context.agents.values()
                        if a.status != "offline"
                    ])
                })

                # Calcular carga del sistema
                total_agents = len(self.shared_context.agents)
                if total_agents > 0:
                    total_load = sum(a.load_factor for a in self.shared_context.agents.values())
                    self.shared_context.system_metrics["system_load"] = total_load / total_agents

                await asyncio.sleep(60)  # Recolectar cada minuto

            except Exception as e:
                self.logger.error(f"Error en recolector de estadísticas: {e}")
                await asyncio.sleep(60)

    async def _setup_persistence(self) -> None:
        """Configura sistemas de persistencia"""
        try:
            if REDIS_AVAILABLE and self.config.get("redis_url"):
                self.redis_client = await aioredis.from_url(self.config["redis_url"])
                self.logger.info("Redis configurado para persistencia")

            if SQLITE_AVAILABLE:
                await self._setup_sqlite()
                self.logger.info("SQLite configurado para persistencia")

        except Exception as e:
            self.logger.error(f"Error configurando persistencia: {e}")

    async def _setup_sqlite(self) -> None:
        """Configura base de datos SQLite"""
        async with aiosqlite.connect(self.sqlite_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id TEXT PRIMARY KEY,
                    type TEXT,
                    priority INTEGER,
                    sender_id TEXT,
                    payload TEXT,
                    timestamp TEXT,
                    processed BOOLEAN DEFAULT FALSE
                )
            """)

            await db.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    id TEXT PRIMARY KEY,
                    event_type TEXT,
                    source_agent_id TEXT,
                    event_data TEXT,
                    timestamp TEXT,
                    severity TEXT
                )
            """)

            await db.commit()

    async def _persist_state(self) -> None:
        """Persiste el estado actual del sistema"""
        try:
            if self.redis_client:
                # Persistir en Redis
                state = await self.get_system_statistics()
                await self.redis_client.set("siame:system_state", json.dumps(state))

            # Persistir tareas activas en SQLite
            if SQLITE_AVAILABLE:
                async with aiosqlite.connect(self.sqlite_path) as db:
                    for task in self.active_tasks.values():
                        await db.execute(
                            "INSERT OR REPLACE INTO tasks VALUES (?, ?, ?, ?)",
                            (task.id, task.task_type, task.status, json.dumps(asdict(task)))
                        )
                    await db.commit()

        except Exception as e:
            self.logger.error(f"Error persistiendo estado: {e}")


# Función de utilidad para crear instancia global
_global_message_bus: Optional[MessageBus] = None

def get_message_bus(config: Optional[Dict[str, Any]] = None) -> MessageBus:
    """Obtiene la instancia global del message bus"""
    global _global_message_bus
    if _global_message_bus is None:
        _global_message_bus = MessageBus(config)
    return _global_message_bus


# Función principal para testing
async def main():
    """Función principal para testing del message bus"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Crear message bus
    message_bus = MessageBus({
        "queue_max_size": 1000,
        "max_retry_delay": 60,
        "persistence_enabled": False
    })

    try:
        # Inicializar
        await message_bus.initialize()

        # Registrar agente de ejemplo
        await message_bus.register_agent(
            "test_agent_1",
            "test_agent",
            "Test Agent 1",
            ["testing", "example"]
        )

        # Suscribirse a eventos
        async def event_handler(event: Event):
            print(f"Evento recibido: {event.event_type.value} de {event.source_agent_id}")

        await message_bus.subscribe_to_events("*", event_handler)

        # Crear tarea de ejemplo
        task = Task(
            task_type="test_task",
            description="Tarea de prueba",
            input_data={"test": "data"}
        )

        # Enviar tarea
        success = await message_bus.submit_task(task)
        print(f"Tarea enviada: {success}")

        # Simular trabajo
        await asyncio.sleep(2)

        # Completar tarea
        await message_bus.complete_task(
            task.id,
            {"result": "success"},
            "test_agent_1"
        )

        # Obtener estadísticas
        stats = await message_bus.get_system_statistics()
        print(f"Estadísticas: {stats}")

        # Esperar un poco más
        await asyncio.sleep(1)

    finally:
        await message_bus.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
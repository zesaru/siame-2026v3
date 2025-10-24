#!/usr/bin/env python3
"""
SIAME 2026v3 - Task Dispatcher
Módulo responsable de distribuir tareas a los agentes especializados

Este componente:
- Gestiona la cola de tareas pendientes
- Implementa algoritmos de balanceamiento de carga
- Maneja la asignación dinámica de tareas a agentes
- Monitorea el rendimiento y disponibilidad de agentes
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from queue import PriorityQueue
from enum import Enum


class DispatchStrategy(Enum):
    """Estrategias de distribución de tareas"""
    ROUND_ROBIN = "round_robin"
    LEAST_LOADED = "least_loaded"
    PRIORITY_BASED = "priority_based"
    PERFORMANCE_WEIGHTED = "performance_weighted"
    AFFINITY_BASED = "affinity_based"


@dataclass
class TaskQueueItem:
    """Item en la cola de tareas con prioridad"""
    priority: int
    timestamp: datetime
    task_id: str

    def __lt__(self, other):
        if self.priority != other.priority:
            return self.priority < other.priority
        return self.timestamp < other.timestamp


class TaskDispatcher:
    """Dispatcher principal para distribución de tareas"""

    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
        self.logger = logging.getLogger(__name__)

        # Cola de tareas prioritaria
        self.task_queue = PriorityQueue()
        self.pending_tasks: Dict[str, any] = {}  # task_id -> Task

        # Configuración de dispatch
        self.dispatch_strategy = DispatchStrategy.LEAST_LOADED
        self.max_retries = 3
        self.retry_delay = 5.0  # segundos
        self.batch_size = 10

        # Estadísticas y monitoreo
        self.dispatch_stats = {
            "total_dispatched": 0,
            "successful_dispatches": 0,
            "failed_dispatches": 0,
            "retries": 0,
            "average_dispatch_time": 0.0
        }

        # Control de ejecución
        self.is_running = False
        self.dispatch_task = None
        self._shutdown_event = asyncio.Event()

    async def initialize(self) -> bool:
        """Inicializa el dispatcher"""
        try:
            self.logger.info("Inicializando Task Dispatcher...")

            # Iniciar el loop principal de dispatch
            self.is_running = True
            self.dispatch_task = asyncio.create_task(self._dispatch_loop())

            self.logger.info("Task Dispatcher inicializado exitosamente")
            return True

        except Exception as e:
            self.logger.error(f"Error inicializando Task Dispatcher: {e}")
            return False

    async def shutdown(self) -> None:
        """Cierra el dispatcher ordenadamente"""
        self.logger.info("Cerrando Task Dispatcher...")

        self.is_running = False
        self._shutdown_event.set()

        # Cancelar el task principal
        if self.dispatch_task:
            self.dispatch_task.cancel()
            try:
                await self.dispatch_task
            except asyncio.CancelledError:
                pass

        # Procesar tareas pendientes
        await self._process_remaining_tasks()

        self.logger.info("Task Dispatcher cerrado")

    async def dispatch_task(self, task) -> bool:
        """Envía una tarea al dispatcher para su procesamiento"""
        try:
            # Validar tarea
            if not await self._validate_task(task):
                return False

            # Añadir a la cola
            queue_item = TaskQueueItem(
                priority=task.priority,
                timestamp=datetime.now(),
                task_id=task.id
            )

            self.task_queue.put(queue_item)
            self.pending_tasks[task.id] = task

            self.logger.debug(f"Tarea {task.id} añadida a la cola de dispatch")
            return True

        except Exception as e:
            self.logger.error(f"Error enviando tarea {task.id} al dispatcher: {e}")
            return False

    async def reschedule_task(self, task_id: str, new_priority: Optional[int] = None) -> bool:
        """Reprograma una tarea con nueva prioridad"""
        try:
            task = self.pending_tasks.get(task_id)
            if not task:
                return False

            if new_priority is not None:
                task.priority = new_priority

            # Reenviar a la cola
            return await self.dispatch_task(task)

        except Exception as e:
            self.logger.error(f"Error reprogramando tarea {task_id}: {e}")
            return False

    async def cancel_task(self, task_id: str) -> bool:
        """Cancela una tarea pendiente"""
        try:
            if task_id in self.pending_tasks:
                task = self.pending_tasks[task_id]
                task.status = self.orchestrator.TaskStatus.CANCELLED
                del self.pending_tasks[task_id]

                self.logger.info(f"Tarea {task_id} cancelada")
                return True

            return False

        except Exception as e:
            self.logger.error(f"Error cancelando tarea {task_id}: {e}")
            return False

    async def get_queue_status(self) -> Dict:
        """Obtiene el estado actual de la cola de tareas"""
        return {
            "queue_size": self.task_queue.qsize(),
            "pending_tasks": len(self.pending_tasks),
            "dispatch_strategy": self.dispatch_strategy.value,
            "statistics": self.dispatch_stats.copy()
        }

    async def update_dispatch_strategy(self, strategy: DispatchStrategy) -> None:
        """Actualiza la estrategia de distribución"""
        self.dispatch_strategy = strategy
        self.logger.info(f"Estrategia de dispatch actualizada a: {strategy.value}")

    # Métodos privados

    async def _dispatch_loop(self) -> None:
        """Loop principal de distribución de tareas"""
        self.logger.info("Iniciando loop de dispatch")

        while self.is_running:
            try:
                # Procesar batch de tareas
                await self._process_task_batch()

                # Verificar agentes inactivos
                await self._check_agent_health()

                # Actualizar estadísticas
                await self._update_statistics()

                # Esperar antes del siguiente ciclo
                await asyncio.sleep(0.1)

            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error en loop de dispatch: {e}")
                await asyncio.sleep(1.0)

        self.logger.info("Loop de dispatch terminado")

    async def _process_task_batch(self) -> None:
        """Procesa un lote de tareas de la cola"""
        batch_count = 0

        while batch_count < self.batch_size and not self.task_queue.empty():
            try:
                # Obtener siguiente tarea
                queue_item = self.task_queue.get_nowait()
                task = self.pending_tasks.get(queue_item.task_id)

                if not task:
                    continue

                # Intentar dispatch
                start_time = datetime.now()
                success = await self._dispatch_single_task(task)

                # Actualizar estadísticas
                dispatch_time = (datetime.now() - start_time).total_seconds()
                await self._record_dispatch_result(task.id, success, dispatch_time)

                if success:
                    # Remover de pendientes
                    if task.id in self.pending_tasks:
                        del self.pending_tasks[task.id]
                else:
                    # Reintentar si es posible
                    await self._handle_dispatch_failure(task)

                batch_count += 1

            except Exception as e:
                self.logger.error(f"Error procesando tarea en batch: {e}")
                break

    async def _dispatch_single_task(self, task) -> bool:
        """Distribuye una tarea individual a un agente"""
        try:
            # Seleccionar agente según estrategia
            selected_agent = await self._select_agent_for_task(task)

            if not selected_agent:
                self.logger.warning(f"No hay agentes disponibles para tarea {task.id}")
                return False

            # Enviar tarea al agente
            success = await self._send_task_to_agent(task, selected_agent)

            if success:
                task.status = self.orchestrator.TaskStatus.IN_PROGRESS
                task.started_at = datetime.now()
                selected_agent.current_tasks.append(task.id)

                self.logger.info(
                    f"Tarea {task.id} asignada a agente {selected_agent.name}"
                )

            return success

        except Exception as e:
            self.logger.error(f"Error distribuyendo tarea {task.id}: {e}")
            return False

    async def _select_agent_for_task(self, task):
        """Selecciona el mejor agente para una tarea según la estrategia"""
        # Filtrar agentes elegibles
        eligible_agents = [
            agent for agent in self.orchestrator.agents.values()
            if (agent.is_active and
                len(agent.current_tasks) < agent.max_concurrent_tasks and
                task.document_type in agent.supported_document_types and
                any(agent.type in task.required_agents))
        ]

        if not eligible_agents:
            return None

        # Aplicar estrategia de selección
        if self.dispatch_strategy == DispatchStrategy.LEAST_LOADED:
            return min(eligible_agents, key=lambda a: len(a.current_tasks))

        elif self.dispatch_strategy == DispatchStrategy.PERFORMANCE_WEIGHTED:
            return await self._select_by_performance(eligible_agents)

        elif self.dispatch_strategy == DispatchStrategy.ROUND_ROBIN:
            return await self._select_round_robin(eligible_agents)

        elif self.dispatch_strategy == DispatchStrategy.PRIORITY_BASED:
            return await self._select_by_priority(eligible_agents, task)

        else:
            # Default: primer agente disponible
            return eligible_agents[0]

    async def _select_by_performance(self, agents):
        """Selecciona agente basado en métricas de rendimiento"""
        best_agent = None
        best_score = 0

        for agent in agents:
            # Calcular score basado en rendimiento
            success_rate = agent.performance_metrics.get("success_rate", 0.5)
            avg_time = agent.performance_metrics.get("average_task_time", 60.0)
            load_factor = 1.0 - (len(agent.current_tasks) / agent.max_concurrent_tasks)

            # Score combinado (mayor es mejor)
            score = (success_rate * 0.4) + (load_factor * 0.4) + ((1.0 / avg_time) * 0.2)

            if score > best_score:
                best_score = score
                best_agent = agent

        return best_agent

    async def _select_round_robin(self, agents):
        """Selección round-robin simple"""
        # TODO: Implementar contador round-robin persistente
        import random
        return random.choice(agents)

    async def _select_by_priority(self, agents, task):
        """Selecciona agente considerando prioridad de la tarea"""
        # Para tareas de alta prioridad, preferir agentes con mejor rendimiento
        if task.priority <= 3:
            return await self._select_by_performance(agents)
        else:
            return min(agents, key=lambda a: len(a.current_tasks))

    async def _send_task_to_agent(self, task, agent) -> bool:
        """Envía una tarea a un agente específico"""
        try:
            # TODO: Implementar comunicación real con agentes
            # Por ahora, simular envío exitoso
            await asyncio.sleep(0.01)  # Simular latencia de red

            self.logger.debug(
                f"Tarea {task.id} enviada a agente {agent.name}"
            )
            return True

        except Exception as e:
            self.logger.error(
                f"Error enviando tarea {task.id} a agente {agent.name}: {e}"
            )
            return False

    async def _handle_dispatch_failure(self, task) -> None:
        """Maneja fallos en el dispatch de tareas"""
        task.metadata["retry_count"] = task.metadata.get("retry_count", 0) + 1

        if task.metadata["retry_count"] < self.max_retries:
            # Reprogramar con delay
            await asyncio.sleep(self.retry_delay)

            # Reenviar a la cola con menor prioridad
            queue_item = TaskQueueItem(
                priority=task.priority + 1,
                timestamp=datetime.now(),
                task_id=task.id
            )
            self.task_queue.put(queue_item)

            self.dispatch_stats["retries"] += 1
            self.logger.info(
                f"Reintentando tarea {task.id} (intento {task.metadata['retry_count']})"
            )
        else:
            # Marcar como fallida
            task.status = self.orchestrator.TaskStatus.FAILED
            if task.id in self.pending_tasks:
                del self.pending_tasks[task.id]

            self.logger.error(
                f"Tarea {task.id} fallida después de {self.max_retries} intentos"
            )

    async def _check_agent_health(self) -> None:
        """Verifica la salud de los agentes registrados"""
        current_time = datetime.now()
        timeout_threshold = timedelta(minutes=5)

        for agent in list(self.orchestrator.agents.values()):
            if agent.last_heartbeat and (current_time - agent.last_heartbeat) > timeout_threshold:
                self.logger.warning(
                    f"Agente {agent.name} sin heartbeat por {current_time - agent.last_heartbeat}"
                )

                # Marcar como inactivo si no responde
                if (current_time - agent.last_heartbeat) > timedelta(minutes=10):
                    agent.is_active = False
                    await self.orchestrator._reassign_agent_tasks(agent.id)

    async def _update_statistics(self) -> None:
        """Actualiza las estadísticas del dispatcher"""
        # Calcular tiempo promedio de dispatch
        if self.dispatch_stats["total_dispatched"] > 0:
            success_rate = (
                self.dispatch_stats["successful_dispatches"] /
                self.dispatch_stats["total_dispatched"]
            )
            self.dispatch_stats["success_rate"] = success_rate

    async def _record_dispatch_result(self, task_id: str, success: bool, dispatch_time: float) -> None:
        """Registra el resultado de un dispatch"""
        self.dispatch_stats["total_dispatched"] += 1

        if success:
            self.dispatch_stats["successful_dispatches"] += 1
        else:
            self.dispatch_stats["failed_dispatches"] += 1

        # Actualizar tiempo promedio
        current_avg = self.dispatch_stats["average_dispatch_time"]
        total = self.dispatch_stats["total_dispatched"]
        new_avg = ((current_avg * (total - 1)) + dispatch_time) / total
        self.dispatch_stats["average_dispatch_time"] = new_avg

    async def _validate_task(self, task) -> bool:
        """Valida que una tarea sea válida para dispatch"""
        if not task.id:
            self.logger.error("Tarea sin ID válido")
            return False

        if not task.required_agents:
            self.logger.error(f"Tarea {task.id} sin agentes requeridos")
            return False

        if task.status != self.orchestrator.TaskStatus.PENDING:
            self.logger.error(f"Tarea {task.id} no está en estado PENDING")
            return False

        return True

    async def _process_remaining_tasks(self) -> None:
        """Procesa las tareas restantes durante el cierre"""
        while not self.task_queue.empty():
            try:
                queue_item = self.task_queue.get_nowait()
                task = self.pending_tasks.get(queue_item.task_id)
                if task:
                    task.status = self.orchestrator.TaskStatus.CANCELLED
                    self.logger.info(f"Tarea {task.id} cancelada durante cierre")
            except:
                break

        # Limpiar tareas pendientes
        for task in self.pending_tasks.values():
            task.status = self.orchestrator.TaskStatus.CANCELLED

        self.pending_tasks.clear()

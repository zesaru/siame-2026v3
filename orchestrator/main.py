#!/usr/bin/env python3
"""
SIAME 2026v3 - Sistema Inteligente de Analisis Multiagente Especializado
Orchestrator Principal - Coordina todos los subagentes especializados en documentos diplomaticos

Este modulo implementa el cerebro central que:
- Gestiona la coordinacion entre subagentes especializados
- Maneja el routing de documentos segun su tipo
- Coordina tareas complejas que requieren multiples agentes
- Mantiene el estado global del sistema
"""

import asyncio
import logging
import uuid
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from pathlib import Path

from task_dispatcher import TaskDispatcher
from result_aggregator import ResultAggregator


class DocumentType(Enum):
    """Tipos de documentos diplomaticos soportados"""
    TREATY = "treaty"
    AGREEMENT = "agreement"
    PROTOCOL = "protocol"
    MEMORANDUM = "memorandum"
    DIPLOMATIC_NOTE = "diplomatic_note"
    CONSULAR_DOCUMENT = "consular_document"
    TRADE_AGREEMENT = "trade_agreement"
    SECURITY_PACT = "security_pact"
    MULTILATERAL_TREATY = "multilateral_treaty"
    BILATERAL_AGREEMENT = "bilateral_agreement"
    UNKNOWN = "unknown"


class AgentType(Enum):
    """Tipos de agentes especializados disponibles"""
    ANALYST = "analyst"
    DEVELOPER = "developer"
    TESTER = "tester"
    DEPLOYER = "deployer"
    DOCUMENT_CLASSIFIER = "document_classifier"
    LEGAL_ANALYZER = "legal_analyzer"
    TRANSLATION_SPECIALIST = "translation_specialist"
    COMPLIANCE_CHECKER = "compliance_checker"


class TaskStatus(Enum):
    """Estados posibles de una tarea"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Task:
    """Representa una tarea que puede ser asignada a un agente"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    type: str = ""
    description: str = ""
    document_type: DocumentType = DocumentType.UNKNOWN
    required_agents: List[AgentType] = field(default_factory=list)
    priority: int = 5  # 1-10, donde 1 es m�xima prioridad
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    assigned_agents: List[str] = field(default_factory=list)
    input_data: Dict[str, Any] = field(default_factory=dict)
    output_data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)  # IDs de tareas dependientes
    callbacks: List[Callable] = field(default_factory=list)


@dataclass
class Agent:
    """Representa un agente especializado"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    type: AgentType = AgentType.ANALYST
    name: str = ""
    description: str = ""
    capabilities: List[str] = field(default_factory=list)
    supported_document_types: List[DocumentType] = field(default_factory=list)
    max_concurrent_tasks: int = 3
    current_tasks: List[str] = field(default_factory=list)
    is_active: bool = True
    performance_metrics: Dict[str, Any] = field(default_factory=dict)
    last_heartbeat: Optional[datetime] = None


class SIAMEOrchestrator:
    """Orchestrator principal del sistema SIAME 2026v3"""

    def __init__(self, config_path: Optional[Path] = None):
        self.logger = logging.getLogger(__name__)
        self.config_path = config_path or Path("config/system_settings.yaml")

        # Componentes principales
        self.task_dispatcher = TaskDispatcher(self)
        self.result_aggregator = ResultAggregator(self)

        # Estado del sistema
        self.agents: Dict[str, Agent] = {}
        self.tasks: Dict[str, Task] = {}
        self.active_workflows: Dict[str, List[str]] = {}  # workflow_id -> task_ids
        self.system_metrics: Dict[str, Any] = {
            "tasks_processed": 0,
            "documents_analyzed": 0,
            "agents_active": 0,
            "average_task_duration": 0.0,
            "success_rate": 0.0
        }

        # Control de ejecuci�n
        self.is_running = False
        self._shutdown_event = asyncio.Event()

        self.logger.info("SIAME Orchestrator inicializado")

    async def initialize(self) -> bool:
        """Inicializa el orchestrator y todos sus componentes"""
        try:
            self.logger.info("Iniciando SIAME Orchestrator...")

            # Cargar configuraci�n
            await self._load_configuration()

            # Inicializar agentes
            await self._initialize_agents()

            # Inicializar componentes
            await self.task_dispatcher.initialize()
            await self.result_aggregator.initialize()

            # Iniciar servicios de monitoreo
            await self._start_monitoring_services()

            self.is_running = True
            self.logger.info("SIAME Orchestrator iniciado exitosamente")
            return True

        except Exception as e:
            self.logger.error(f"Error al inicializar orchestrator: {e}")
            return False

    async def shutdown(self) -> None:
        """Cierra ordenadamente el orchestrator"""
        self.logger.info("Iniciando cierre del orchestrator...")

        self.is_running = False
        self._shutdown_event.set()

        # Completar tareas en progreso
        await self._complete_pending_tasks()

        # Desactivar agentes
        await self._deactivate_agents()

        # Cerrar componentes
        await self.task_dispatcher.shutdown()
        await self.result_aggregator.shutdown()

        self.logger.info("Orchestrator cerrado exitosamente")

    async def process_document(self, document_path: Path,
                             document_type: Optional[DocumentType] = None,
                             workflow_config: Optional[Dict] = None) -> str:
        """Procesa un documento diplom�tico usando el flujo de agentes apropiado"""
        try:
            # Detectar tipo de documento si no se especifica
            if document_type is None:
                document_type = await self._detect_document_type(document_path)

            # Crear workflow para el documento
            workflow_id = await self._create_document_workflow(
                document_path, document_type, workflow_config
            )

            self.logger.info(
                f"Iniciando procesamiento de documento {document_path.name} "
                f"(tipo: {document_type.value}, workflow: {workflow_id})"
            )

            # Ejecutar workflow
            await self._execute_workflow(workflow_id)

            # Actualizar m�tricas
            self.system_metrics["documents_analyzed"] += 1

            return workflow_id

        except Exception as e:
            self.logger.error(f"Error procesando documento {document_path}: {e}")
            raise

    async def submit_task(self, task: Task) -> str:
        """Env�a una tarea al sistema para su procesamiento"""
        try:
            self.tasks[task.id] = task

            # Validar dependencias
            await self._validate_task_dependencies(task)

            # Asignar agentes apropiados
            await self._assign_agents_to_task(task)

            # Enviar a dispatcher
            await self.task_dispatcher.dispatch_task(task)

            self.logger.info(f"Tarea {task.id} enviada para procesamiento")
            return task.id

        except Exception as e:
            self.logger.error(f"Error enviando tarea {task.id}: {e}")
            task.status = TaskStatus.FAILED
            raise

    async def get_task_status(self, task_id: str) -> Optional[TaskStatus]:
        """Obtiene el estado actual de una tarea"""
        task = self.tasks.get(task_id)
        return task.status if task else None

    async def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """Obtiene el estado completo de un workflow"""
        if workflow_id not in self.active_workflows:
            return {"error": "Workflow no encontrado"}

        task_ids = self.active_workflows[workflow_id]
        tasks_status = {}

        for task_id in task_ids:
            task = self.tasks.get(task_id)
            if task:
                tasks_status[task_id] = {
                    "status": task.status.value,
                    "type": task.type,
                    "assigned_agents": task.assigned_agents,
                    "progress": self._calculate_task_progress(task)
                }

        return {
            "workflow_id": workflow_id,
            "tasks": tasks_status,
            "overall_progress": self._calculate_workflow_progress(workflow_id)
        }

    async def register_agent(self, agent: Agent) -> bool:
        """Registra un nuevo agente en el sistema"""
        try:
            self.agents[agent.id] = agent
            agent.last_heartbeat = datetime.now()

            self.logger.info(
                f"Agente registrado: {agent.name} ({agent.type.value})"
            )

            self.system_metrics["agents_active"] = len(
                [a for a in self.agents.values() if a.is_active]
            )

            return True

        except Exception as e:
            self.logger.error(f"Error registrando agente {agent.name}: {e}")
            return False

    async def unregister_agent(self, agent_id: str) -> bool:
        """Desregistra un agente del sistema"""
        try:
            if agent_id in self.agents:
                agent = self.agents[agent_id]

                # Reasignar tareas activas
                await self._reassign_agent_tasks(agent_id)

                # Remover agente
                del self.agents[agent_id]

                self.logger.info(f"Agente {agent.name} desregistrado")

                self.system_metrics["agents_active"] = len(
                    [a for a in self.agents.values() if a.is_active]
                )

                return True
            return False

        except Exception as e:
            self.logger.error(f"Error desregistrando agente {agent_id}: {e}")
            return False

    async def get_system_status(self) -> Dict[str, Any]:
        """Obtiene el estado general del sistema"""
        return {
            "status": "running" if self.is_running else "stopped",
            "agents": {
                "total": len(self.agents),
                "active": len([a for a in self.agents.values() if a.is_active]),
                "by_type": self._get_agents_by_type()
            },
            "tasks": {
                "total": len(self.tasks),
                "by_status": self._get_tasks_by_status()
            },
            "workflows": {
                "active": len(self.active_workflows)
            },
            "metrics": self.system_metrics
        }

    # M�todos privados de implementaci�n

    async def _load_configuration(self) -> None:
        """Carga la configuraci�n del sistema"""
        # TODO: Implementar carga de configuraci�n desde YAML
        self.logger.info("Configuraci�n cargada")

    async def _initialize_agents(self) -> None:
        """Inicializa los agentes base del sistema"""
        # Crear agentes base
        base_agents = [
            Agent(
                type=AgentType.ANALYST,
                name="Analizador Diplom�tico Principal",
                description="Especialista en an�lisis de documentos diplom�ticos",
                capabilities=["document_analysis", "content_extraction", "classification"],
                supported_document_types=list(DocumentType)
            ),
            Agent(
                type=AgentType.DOCUMENT_CLASSIFIER,
                name="Clasificador de Documentos",
                description="Especialista en clasificaci�n autom�tica de documentos",
                capabilities=["document_classification", "type_detection"],
                supported_document_types=list(DocumentType)
            )
        ]

        for agent in base_agents:
            await self.register_agent(agent)

    async def _start_monitoring_services(self) -> None:
        """Inicia los servicios de monitoreo del sistema"""
        # TODO: Implementar servicios de monitoreo
        self.logger.info("Servicios de monitoreo iniciados")

    async def _complete_pending_tasks(self) -> None:
        """Completa o cancela tareas pendientes durante el cierre"""
        pending_tasks = [t for t in self.tasks.values()
                        if t.status in [TaskStatus.PENDING, TaskStatus.IN_PROGRESS]]

        for task in pending_tasks:
            task.status = TaskStatus.CANCELLED
            self.logger.info(f"Tarea {task.id} cancelada durante cierre")

    async def _deactivate_agents(self) -> None:
        """Desactiva todos los agentes"""
        for agent in self.agents.values():
            agent.is_active = False

        self.logger.info("Todos los agentes desactivados")

    async def _detect_document_type(self, document_path: Path) -> DocumentType:
        """Detecta autom�ticamente el tipo de documento"""
        # TODO: Implementar detecci�n inteligente usando agente clasificador
        return DocumentType.UNKNOWN

    async def _create_document_workflow(self, document_path: Path,
                                      document_type: DocumentType,
                                      config: Optional[Dict]) -> str:
        """Crea un workflow para procesar un documento"""
        workflow_id = str(uuid.uuid4())
        task_ids = []

        # Crear tareas seg�n el tipo de documento
        if document_type == DocumentType.TREATY:
            tasks = await self._create_treaty_workflow_tasks(document_path)
        elif document_type == DocumentType.TRADE_AGREEMENT:
            tasks = await self._create_trade_workflow_tasks(document_path)
        else:
            tasks = await self._create_generic_workflow_tasks(document_path)

        for task in tasks:
            task_ids.append(task.id)
            self.tasks[task.id] = task

        self.active_workflows[workflow_id] = task_ids
        return workflow_id

    async def _execute_workflow(self, workflow_id: str) -> None:
        """Ejecuta un workflow completo"""
        task_ids = self.active_workflows[workflow_id]

        for task_id in task_ids:
            task = self.tasks[task_id]
            await self.submit_task(task)

    async def _create_treaty_workflow_tasks(self, document_path: Path) -> List[Task]:
        """Crea tareas espec�ficas para procesamiento de tratados"""
        return [
            Task(
                type="document_classification",
                description=f"Clasificar documento {document_path.name}",
                document_type=DocumentType.TREATY,
                required_agents=[AgentType.DOCUMENT_CLASSIFIER],
                input_data={"document_path": str(document_path)}
            ),
            Task(
                type="legal_analysis",
                description=f"An�lisis legal de {document_path.name}",
                document_type=DocumentType.TREATY,
                required_agents=[AgentType.LEGAL_ANALYZER, AgentType.ANALYST],
                input_data={"document_path": str(document_path)}
            )
        ]

    async def _create_trade_workflow_tasks(self, document_path: Path) -> List[Task]:
        """Crea tareas espec�ficas para acuerdos comerciales"""
        return [
            Task(
                type="document_classification",
                description=f"Clasificar documento {document_path.name}",
                document_type=DocumentType.TRADE_AGREEMENT,
                required_agents=[AgentType.DOCUMENT_CLASSIFIER],
                input_data={"document_path": str(document_path)}
            ),
            Task(
                type="compliance_check",
                description=f"Verificaci�n de cumplimiento de {document_path.name}",
                document_type=DocumentType.TRADE_AGREEMENT,
                required_agents=[AgentType.COMPLIANCE_CHECKER],
                input_data={"document_path": str(document_path)}
            )
        ]

    async def _create_generic_workflow_tasks(self, document_path: Path) -> List[Task]:
        """Crea tareas gen�ricas para documentos no espec�ficos"""
        return [
            Task(
                type="document_analysis",
                description=f"An�lisis general de {document_path.name}",
                required_agents=[AgentType.ANALYST],
                input_data={"document_path": str(document_path)}
            )
        ]

    async def _validate_task_dependencies(self, task: Task) -> None:
        """Valida que las dependencias de una tarea est�n satisfechas"""
        for dep_id in task.dependencies:
            dep_task = self.tasks.get(dep_id)
            if not dep_task or dep_task.status != TaskStatus.COMPLETED:
                raise ValueError(f"Dependencia {dep_id} no satisfecha para tarea {task.id}")

    async def _assign_agents_to_task(self, task: Task) -> None:
        """Asigna agentes apropiados a una tarea"""
        for agent_type in task.required_agents:
            suitable_agents = [
                agent for agent in self.agents.values()
                if (agent.type == agent_type and
                    agent.is_active and
                    len(agent.current_tasks) < agent.max_concurrent_tasks and
                    task.document_type in agent.supported_document_types)
            ]

            if suitable_agents:
                # Seleccionar el agente con menos carga
                selected_agent = min(suitable_agents, key=lambda a: len(a.current_tasks))
                task.assigned_agents.append(selected_agent.id)
                selected_agent.current_tasks.append(task.id)
            else:
                raise ValueError(f"No hay agentes disponibles para tipo {agent_type.value}")

    async def _reassign_agent_tasks(self, agent_id: str) -> None:
        """Reasigna las tareas de un agente que se desconecta"""
        agent = self.agents.get(agent_id)
        if not agent:
            return

        for task_id in agent.current_tasks:
            task = self.tasks.get(task_id)
            if task and task.status == TaskStatus.IN_PROGRESS:
                task.status = TaskStatus.PENDING
                task.assigned_agents = [a for a in task.assigned_agents if a != agent_id]
                # TODO: Reasignar a otro agente

    def _calculate_task_progress(self, task: Task) -> float:
        """Calcula el progreso de una tarea"""
        if task.status == TaskStatus.COMPLETED:
            return 1.0
        elif task.status == TaskStatus.IN_PROGRESS:
            return 0.5
        else:
            return 0.0

    def _calculate_workflow_progress(self, workflow_id: str) -> float:
        """Calcula el progreso total de un workflow"""
        task_ids = self.active_workflows.get(workflow_id, [])
        if not task_ids:
            return 0.0

        total_progress = sum(
            self._calculate_task_progress(self.tasks[task_id])
            for task_id in task_ids if task_id in self.tasks
        )

        return total_progress / len(task_ids)

    def _get_agents_by_type(self) -> Dict[str, int]:
        """Obtiene conteo de agentes por tipo"""
        counts = {}
        for agent in self.agents.values():
            agent_type = agent.type.value
            counts[agent_type] = counts.get(agent_type, 0) + 1
        return counts

    def _get_tasks_by_status(self) -> Dict[str, int]:
        """Obtiene conteo de tareas por estado"""
        counts = {}
        for task in self.tasks.values():
            status = task.status.value
            counts[status] = counts.get(status, 0) + 1
        return counts


# Funci�n principal para ejecutar el orchestrator
async def main():
    """Funci�n principal para ejecutar el orchestrator como aplicaci�n independiente"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    orchestrator = SIAMEOrchestrator()

    try:
        await orchestrator.initialize()

        # Mantener el orchestrator ejecut�ndose
        while orchestrator.is_running:
            await asyncio.sleep(1)

    except KeyboardInterrupt:
        logging.info("Cierre solicitado por usuario")
    finally:
        await orchestrator.shutdown()


if __name__ == "__main__":
    asyncio.run(main())

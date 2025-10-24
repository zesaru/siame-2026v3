#!/usr/bin/env python3
"""
SIAME 2026v3 - Result Aggregator
Módulo responsable de agregar y consolidar resultados de múltiples agentes

Este componente:
- Recolecta resultados de tareas completadas
- Consolida resultados de workflows multi-agente
- Genera reportes integrados y análisis consolidados
- Maneja la persistencia de resultados
"""

import asyncio
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field, asdict
from pathlib import Path
from enum import Enum


class ResultType(Enum):
    """Tipos de resultados que pueden ser agregados"""
    DOCUMENT_ANALYSIS = "document_analysis"
    CLASSIFICATION_RESULT = "classification_result"
    LEGAL_ANALYSIS = "legal_analysis"
    COMPLIANCE_CHECK = "compliance_check"
    TRANSLATION = "translation"
    SUMMARY = "summary"
    METADATA_EXTRACTION = "metadata_extraction"
    WORKFLOW_COMPLETION = "workflow_completion"


class AggregationStrategy(Enum):
    """Estrategias para agregar resultados"""
    MERGE = "merge"  # Combinar todos los resultados
    CONSENSUS = "consensus"  # Buscar consenso entre resultados
    BEST_SCORE = "best_score"  # Seleccionar el mejor resultado
    WEIGHTED_AVERAGE = "weighted_average"  # Promedio ponderado
    HIERARCHICAL = "hierarchical"  # Agregación jerárquica


@dataclass
class TaskResult:
    """Resultado de una tarea individual"""
    task_id: str
    agent_id: str
    agent_type: str
    result_type: ResultType
    status: str
    confidence_score: float = 0.0
    execution_time: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)
    data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


@dataclass
class AggregatedResult:
    """Resultado agregado de múltiples tareas/agentes"""
    workflow_id: str
    document_path: str
    document_type: str
    aggregation_strategy: AggregationStrategy
    created_at: datetime = field(default_factory=datetime.now)
    task_results: List[TaskResult] = field(default_factory=list)
    consolidated_data: Dict[str, Any] = field(default_factory=dict)
    confidence_scores: Dict[str, float] = field(default_factory=dict)
    summary: Dict[str, Any] = field(default_factory=dict)
    quality_metrics: Dict[str, float] = field(default_factory=dict)
    processing_stats: Dict[str, Any] = field(default_factory=dict)


class ResultAggregator:
    """Agregador principal de resultados del sistema"""

    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
        self.logger = logging.getLogger(__name__)

        # Almacenamiento de resultados
        self.task_results: Dict[str, TaskResult] = {}
        self.aggregated_results: Dict[str, AggregatedResult] = {}
        self.workflow_results: Dict[str, List[str]] = {}  # workflow_id -> result_ids

        # Configuración
        self.default_strategy = AggregationStrategy.MERGE
        self.min_confidence_threshold = 0.6
        self.max_result_age = timedelta(hours=24)
        self.auto_cleanup_enabled = True

        # Estadísticas
        self.aggregation_stats = {
            "total_results_processed": 0,
            "workflows_completed": 0,
            "average_confidence": 0.0,
            "aggregations_performed": 0,
            "quality_score_average": 0.0
        }

        # Control de ejecución
        self.is_running = False
        self.cleanup_task = None
        self._shutdown_event = asyncio.Event()

    async def initialize(self) -> bool:
        """Inicializa el agregador de resultados"""
        try:
            self.logger.info("Inicializando Result Aggregator...")

            # Cargar resultados persistidos
            await self._load_persisted_results()

            # Iniciar servicios de limpieza
            if self.auto_cleanup_enabled:
                self.cleanup_task = asyncio.create_task(self._cleanup_loop())

            self.is_running = True
            self.logger.info("Result Aggregator inicializado exitosamente")
            return True

        except Exception as e:
            self.logger.error(f"Error inicializando Result Aggregator: {e}")
            return False

    async def shutdown(self) -> None:
        """Cierra el agregador ordenadamente"""
        self.logger.info("Cerrando Result Aggregator...")

        self.is_running = False
        self._shutdown_event.set()

        # Cancelar tareas de limpieza
        if self.cleanup_task:
            self.cleanup_task.cancel()
            try:
                await self.cleanup_task
            except asyncio.CancelledError:
                pass

        # Persistir resultados
        await self._persist_results()

        self.logger.info("Result Aggregator cerrado")

    async def add_task_result(self, result: TaskResult) -> bool:
        """Añade un resultado de tarea al agregador"""
        try:
            # Validar resultado
            if not await self._validate_result(result):
                return False

            # Almacenar resultado
            self.task_results[result.task_id] = result

            # Actualizar estadísticas
            self.aggregation_stats["total_results_processed"] += 1
            await self._update_confidence_stats(result.confidence_score)

            self.logger.debug(f"Resultado de tarea {result.task_id} agregado")

            # Verificar si podemos agregar resultados de workflow
            await self._check_workflow_completion(result.task_id)

            return True

        except Exception as e:
            self.logger.error(f"Error agregando resultado de tarea {result.task_id}: {e}")
            return False

    async def aggregate_workflow_results(self, workflow_id: str,
                                       strategy: Optional[AggregationStrategy] = None) -> Optional[AggregatedResult]:
        """Agrega los resultados de un workflow completo"""
        try:
            if workflow_id not in self.orchestrator.active_workflows:
                self.logger.error(f"Workflow {workflow_id} no encontrado")
                return None

            # Obtener tareas del workflow
            task_ids = self.orchestrator.active_workflows[workflow_id]
            task_results = []

            for task_id in task_ids:
                if task_id in self.task_results:
                    task_results.append(self.task_results[task_id])

            if not task_results:
                self.logger.warning(f"No hay resultados disponibles para workflow {workflow_id}")
                return None

            # Determinar estrategia de agregación
            aggregation_strategy = strategy or self.default_strategy

            # Crear resultado agregado
            aggregated = await self._create_aggregated_result(
                workflow_id, task_results, aggregation_strategy
            )

            # Almacenar resultado agregado
            self.aggregated_results[workflow_id] = aggregated
            self.workflow_results[workflow_id] = [r.task_id for r in task_results]

            # Actualizar estadísticas
            self.aggregation_stats["workflows_completed"] += 1
            self.aggregation_stats["aggregations_performed"] += 1

            self.logger.info(
                f"Resultados de workflow {workflow_id} agregados exitosamente "
                f"(estrategia: {aggregation_strategy.value})"
            )

            return aggregated

        except Exception as e:
            self.logger.error(f"Error agregando resultados de workflow {workflow_id}: {e}")
            return None

    async def get_aggregated_result(self, workflow_id: str) -> Optional[AggregatedResult]:
        """Obtiene un resultado agregado por ID de workflow"""
        return self.aggregated_results.get(workflow_id)

    async def get_task_result(self, task_id: str) -> Optional[TaskResult]:
        """Obtiene un resultado de tarea por ID"""
        return self.task_results.get(task_id)

    async def search_results(self, query: Dict[str, Any]) -> List[Union[TaskResult, AggregatedResult]]:
        """Busca resultados según criterios especificados"""
        results = []

        # Buscar en resultados de tareas
        for result in self.task_results.values():
            if await self._matches_query(result, query):
                results.append(result)

        # Buscar en resultados agregados
        for result in self.aggregated_results.values():
            if await self._matches_query(result, query):
                results.append(result)

        return results

    async def generate_report(self, workflow_id: str,
                            report_format: str = "json") -> Optional[Dict[str, Any]]:
        """Genera un reporte consolidado para un workflow"""
        try:
            aggregated = self.aggregated_results.get(workflow_id)
            if not aggregated:
                return None

            report = {
                "workflow_id": workflow_id,
                "document_info": {
                    "path": aggregated.document_path,
                    "type": aggregated.document_type,
                    "processed_at": aggregated.created_at.isoformat()
                },
                "processing_summary": aggregated.summary,
                "consolidated_results": aggregated.consolidated_data,
                "quality_metrics": aggregated.quality_metrics,
                "confidence_scores": aggregated.confidence_scores,
                "task_details": [
                    {
                        "task_id": tr.task_id,
                        "agent_type": tr.agent_type,
                        "result_type": tr.result_type.value,
                        "confidence": tr.confidence_score,
                        "execution_time": tr.execution_time,
                        "status": tr.status
                    }
                    for tr in aggregated.task_results
                ],
                "statistics": aggregated.processing_stats,
                "generated_at": datetime.now().isoformat()
            }

            return report

        except Exception as e:
            self.logger.error(f"Error generando reporte para workflow {workflow_id}: {e}")
            return None

    async def export_results(self, output_path: Path,
                           workflow_ids: Optional[List[str]] = None,
                           format_type: str = "json") -> bool:
        """Exporta resultados a archivo"""
        try:
            # Determinar qué workflows exportar
            if workflow_ids is None:
                workflow_ids = list(self.aggregated_results.keys())

            export_data = {
                "export_info": {
                    "timestamp": datetime.now().isoformat(),
                    "total_workflows": len(workflow_ids),
                    "format": format_type
                },
                "workflows": {}
            }

            # Generar reportes para cada workflow
            for workflow_id in workflow_ids:
                report = await self.generate_report(workflow_id, format_type)
                if report:
                    export_data["workflows"][workflow_id] = report

            # Escribir archivo
            output_path.parent.mkdir(parents=True, exist_ok=True)

            if format_type.lower() == "json":
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, indent=2, ensure_ascii=False)

            self.logger.info(f"Resultados exportados a {output_path}")
            return True

        except Exception as e:
            self.logger.error(f"Error exportando resultados: {e}")
            return False

    async def get_statistics(self) -> Dict[str, Any]:
        """Obtiene estadísticas del agregador"""
        return {
            "aggregation_stats": self.aggregation_stats.copy(),
            "storage_stats": {
                "task_results_count": len(self.task_results),
                "aggregated_results_count": len(self.aggregated_results),
                "workflows_tracked": len(self.workflow_results)
            },
            "quality_stats": await self._calculate_quality_statistics()
        }

    # Métodos privados

    async def _create_aggregated_result(self, workflow_id: str,
                                      task_results: List[TaskResult],
                                      strategy: AggregationStrategy) -> AggregatedResult:
        """Crea un resultado agregado usando la estrategia especificada"""
        # Obtener información del workflow
        first_task = self.orchestrator.tasks.get(task_results[0].task_id)
        document_path = first_task.input_data.get("document_path", "") if first_task else ""
        document_type = first_task.document_type.value if first_task else "unknown"

        aggregated = AggregatedResult(
            workflow_id=workflow_id,
            document_path=document_path,
            document_type=document_type,
            aggregation_strategy=strategy,
            task_results=task_results
        )

        # Aplicar estrategia de agregación
        if strategy == AggregationStrategy.MERGE:
            await self._merge_results(aggregated)
        elif strategy == AggregationStrategy.CONSENSUS:
            await self._consensus_aggregation(aggregated)
        elif strategy == AggregationStrategy.BEST_SCORE:
            await self._best_score_aggregation(aggregated)
        elif strategy == AggregationStrategy.WEIGHTED_AVERAGE:
            await self._weighted_average_aggregation(aggregated)
        else:
            await self._merge_results(aggregated)  # Default

        # Calcular métricas de calidad
        aggregated.quality_metrics = await self._calculate_quality_metrics(aggregated)

        # Generar estadísticas de procesamiento
        aggregated.processing_stats = await self._calculate_processing_stats(aggregated)

        return aggregated

    async def _merge_results(self, aggregated: AggregatedResult) -> None:
        """Estrategia de agregación por fusión simple"""
        consolidated = {}
        confidence_scores = {}

        for result in aggregated.task_results:
            # Fusionar datos
            for key, value in result.data.items():
                if key not in consolidated:
                    consolidated[key] = []
                consolidated[key].append({
                    "value": value,
                    "agent_type": result.agent_type,
                    "confidence": result.confidence_score
                })

            # Agregar scores de confianza
            confidence_scores[result.result_type.value] = result.confidence_score

        aggregated.consolidated_data = consolidated
        aggregated.confidence_scores = confidence_scores

        # Generar resumen
        aggregated.summary = {
            "total_tasks": len(aggregated.task_results),
            "agent_types": list(set(r.agent_type for r in aggregated.task_results)),
            "result_types": list(set(r.result_type.value for r in aggregated.task_results)),
            "average_confidence": sum(confidence_scores.values()) / len(confidence_scores) if confidence_scores else 0.0
        }

    async def _consensus_aggregation(self, aggregated: AggregatedResult) -> None:
        """Estrategia de agregación por consenso"""
        # TODO: Implementar lógica de consenso
        await self._merge_results(aggregated)  # Fallback temporal

    async def _best_score_aggregation(self, aggregated: AggregatedResult) -> None:
        """Estrategia de agregación por mejor puntuación"""
        best_results = {}
        confidence_scores = {}

        # Agrupar por tipo de resultado
        results_by_type = {}
        for result in aggregated.task_results:
            result_type = result.result_type.value
            if result_type not in results_by_type:
                results_by_type[result_type] = []
            results_by_type[result_type].append(result)

        # Seleccionar el mejor resultado de cada tipo
        for result_type, results in results_by_type.items():
            best_result = max(results, key=lambda r: r.confidence_score)
            best_results[result_type] = best_result.data
            confidence_scores[result_type] = best_result.confidence_score

        aggregated.consolidated_data = best_results
        aggregated.confidence_scores = confidence_scores

        # Generar resumen
        aggregated.summary = {
            "total_tasks": len(aggregated.task_results),
            "selection_strategy": "best_confidence_score",
            "average_confidence": sum(confidence_scores.values()) / len(confidence_scores) if confidence_scores else 0.0
        }

    async def _weighted_average_aggregation(self, aggregated: AggregatedResult) -> None:
        """Estrategia de agregación por promedio ponderado"""
        # TODO: Implementar promedio ponderado inteligente
        await self._merge_results(aggregated)  # Fallback temporal

    async def _calculate_quality_metrics(self, aggregated: AggregatedResult) -> Dict[str, float]:
        """Calcula métricas de calidad para un resultado agregado"""
        metrics = {}

        # Consistency score (qué tan consistentes son los resultados)
        confidence_scores = list(aggregated.confidence_scores.values())
        if confidence_scores:
            metrics["confidence_variance"] = self._calculate_variance(confidence_scores)
            metrics["min_confidence"] = min(confidence_scores)
            metrics["max_confidence"] = max(confidence_scores)
            metrics["average_confidence"] = sum(confidence_scores) / len(confidence_scores)

        # Completeness score (qué tan completos son los resultados)
        total_possible_agents = len(self.orchestrator.agents)
        agents_used = len(set(r.agent_type for r in aggregated.task_results))
        metrics["agent_coverage"] = agents_used / total_possible_agents if total_possible_agents > 0 else 0.0

        # Processing efficiency
        execution_times = [r.execution_time for r in aggregated.task_results if r.execution_time > 0]
        if execution_times:
            metrics["average_execution_time"] = sum(execution_times) / len(execution_times)
            metrics["total_processing_time"] = sum(execution_times)

        return metrics

    async def _calculate_processing_stats(self, aggregated: AggregatedResult) -> Dict[str, Any]:
        """Calcula estadísticas de procesamiento"""
        stats = {
            "total_tasks": len(aggregated.task_results),
            "successful_tasks": len([r for r in aggregated.task_results if r.status == "completed"]),
            "failed_tasks": len([r for r in aggregated.task_results if r.status == "failed"]),
            "total_execution_time": sum(r.execution_time for r in aggregated.task_results),
            "agents_involved": list(set(r.agent_type for r in aggregated.task_results)),
            "result_types": list(set(r.result_type.value for r in aggregated.task_results))
        }

        # Calcular tasa de éxito
        if stats["total_tasks"] > 0:
            stats["success_rate"] = stats["successful_tasks"] / stats["total_tasks"]
        else:
            stats["success_rate"] = 0.0

        return stats

    def _calculate_variance(self, values: List[float]) -> float:
        """Calcula la varianza de una lista de valores"""
        if len(values) < 2:
            return 0.0

        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance

    async def _validate_result(self, result: TaskResult) -> bool:
        """Valida un resultado de tarea"""
        if not result.task_id:
            self.logger.error("Resultado sin task_id")
            return False

        if not result.agent_id:
            self.logger.error(f"Resultado {result.task_id} sin agent_id")
            return False

        if result.confidence_score < 0 or result.confidence_score > 1:
            self.logger.warning(
                f"Resultado {result.task_id} con confidence_score inválido: {result.confidence_score}"
            )
            result.confidence_score = max(0, min(1, result.confidence_score))

        return True

    async def _check_workflow_completion(self, task_id: str) -> None:
        """Verifica si un workflow está completo y puede ser agregado"""
        # Encontrar workflow que contiene esta tarea
        for workflow_id, task_ids in self.orchestrator.active_workflows.items():
            if task_id in task_ids:
                # Verificar si todas las tareas están completas
                all_completed = all(
                    tid in self.task_results for tid in task_ids
                )

                if all_completed and workflow_id not in self.aggregated_results:
                    # Agregar automáticamente
                    await self.aggregate_workflow_results(workflow_id)
                break

    async def _matches_query(self, result: Union[TaskResult, AggregatedResult],
                           query: Dict[str, Any]) -> bool:
        """Verifica si un resultado coincide con una consulta"""
        # TODO: Implementar lógica de búsqueda más sofisticada
        return True

    async def _update_confidence_stats(self, confidence: float) -> None:
        """Actualiza estadísticas de confianza"""
        current_avg = self.aggregation_stats["average_confidence"]
        total = self.aggregation_stats["total_results_processed"]

        if total == 1:
            self.aggregation_stats["average_confidence"] = confidence
        else:
            new_avg = ((current_avg * (total - 1)) + confidence) / total
            self.aggregation_stats["average_confidence"] = new_avg

    async def _calculate_quality_statistics(self) -> Dict[str, float]:
        """Calcula estadísticas generales de calidad"""
        if not self.aggregated_results:
            return {}

        all_quality_metrics = []
        for result in self.aggregated_results.values():
            if result.quality_metrics:
                all_quality_metrics.append(result.quality_metrics)

        if not all_quality_metrics:
            return {}

        # Calcular promedios
        quality_stats = {}
        for key in all_quality_metrics[0].keys():
            values = [metrics.get(key, 0) for metrics in all_quality_metrics]
            quality_stats[f"avg_{key}"] = sum(values) / len(values)

        return quality_stats

    async def _cleanup_loop(self) -> None:
        """Loop de limpieza de resultados antiguos"""
        while self.is_running:
            try:
                await self._cleanup_old_results()
                await asyncio.sleep(3600)  # Ejecutar cada hora
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error en loop de limpieza: {e}")
                await asyncio.sleep(60)

    async def _cleanup_old_results(self) -> None:
        """Limpia resultados antiguos"""
        current_time = datetime.now()
        cutoff_time = current_time - self.max_result_age

        # Limpiar resultados de tareas
        old_task_results = [
            task_id for task_id, result in self.task_results.items()
            if result.timestamp < cutoff_time
        ]

        for task_id in old_task_results:
            del self.task_results[task_id]

        # Limpiar resultados agregados
        old_aggregated_results = [
            workflow_id for workflow_id, result in self.aggregated_results.items()
            if result.created_at < cutoff_time
        ]

        for workflow_id in old_aggregated_results:
            del self.aggregated_results[workflow_id]
            if workflow_id in self.workflow_results:
                del self.workflow_results[workflow_id]

        if old_task_results or old_aggregated_results:
            self.logger.info(
                f"Limpieza completada: {len(old_task_results)} resultados de tareas y "
                f"{len(old_aggregated_results)} resultados agregados eliminados"
            )

    async def _load_persisted_results(self) -> None:
        """Carga resultados persistidos desde almacenamiento"""
        # TODO: Implementar carga desde almacenamiento persistente
        self.logger.info("Resultados persistidos cargados")

    async def _persist_results(self) -> None:
        """Persiste resultados en almacenamiento"""
        # TODO: Implementar persistencia en almacenamiento
        self.logger.info("Resultados persistidos")

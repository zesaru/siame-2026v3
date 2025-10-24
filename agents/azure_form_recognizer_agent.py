#!/usr/bin/env python3
"""
SIAME 2026v3 - Azure Form Recognizer Specialist Agent
Agente especializado en Azure Form Recognizer para documentos diplomáticos

Este agente maneja:
- Configuración y entrenamiento de modelos personalizados
- Extracción de datos de hojas de remisión y guías de valija
- Procesamiento OCR de documentos diplomáticos
- Análisis de tablas y estructuras complejas
- Validación y clasificación de documentos extraídos
"""

import asyncio
import logging
import json
import base64
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum

# Importaciones de Azure
try:
    from azure.ai.formrecognizer import DocumentAnalysisClient
    from azure.ai.formrecognizer.aio import DocumentAnalysisClient as AsyncDocumentAnalysisClient
    from azure.ai.formrecognizer import DocumentModelAdministrationClient
    from azure.core.credentials import AzureKeyCredential
    from azure.core.exceptions import HttpResponseError
    AZURE_AVAILABLE = True
except ImportError:
    AZURE_AVAILABLE = False


class DocumentProcessingStatus(Enum):
    """Estados de procesamiento de documentos"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REQUIRES_REVIEW = "requires_review"


class ModelType(Enum):
    """Tipos de modelos de Form Recognizer"""
    PREBUILT_DOCUMENT = "prebuilt-document"
    PREBUILT_LAYOUT = "prebuilt-layout"
    PREBUILT_READ = "prebuilt-read"
    CUSTOM_HOJA_REMISION = "custom-hoja-remision"
    CUSTOM_GUIA_VALIJA = "custom-guia-valija"
    CUSTOM_NOTA_DIPLOMATICA = "custom-nota-diplomatica"


@dataclass
class FormRecognizerConfig:
    """Configuración de Azure Form Recognizer"""
    endpoint: str
    api_key: str
    subscription_id: str
    resource_group: str
    account_name: str
    custom_models: Dict[str, str] = field(default_factory=dict)


@dataclass
class ExtractionResult:
    """Resultado de extracción de un documento"""
    document_id: str
    file_path: str
    model_used: ModelType
    processing_status: DocumentProcessingStatus
    confidence_score: float
    extracted_data: Dict[str, Any] = field(default_factory=dict)
    tables: List[Dict[str, Any]] = field(default_factory=list)
    key_value_pairs: Dict[str, str] = field(default_factory=dict)
    entities: List[Dict[str, Any]] = field(default_factory=list)
    processing_time: float = 0.0
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    raw_response: Optional[Dict[str, Any]] = None


@dataclass
class CustomModelTraining:
    """Configuración de entrenamiento de modelo personalizado"""
    model_name: str
    document_type: str
    training_data_path: Path
    model_description: str
    labels_file: Optional[Path] = None
    expected_fields: List[str] = field(default_factory=list)


class AzureFormRecognizerAgent:
    """Agente especializado en Azure Form Recognizer para documentos diplomáticos"""

    def __init__(self, config: FormRecognizerConfig, agent_id: str = None):
        self.agent_id = agent_id or f"azure_fr_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.logger = logging.getLogger(__name__)
        self.config = config

        # Clientes de Azure
        self.analysis_client = None
        self.admin_client = None

        # Modelos diplomáticos personalizados
        self.diplomatic_models = {
            "hoja_remision": {
                "model_id": "custom-hoja-remision",
                "fields": [
                    "numero_remision",
                    "fecha",
                    "origen",
                    "destino",
                    "clasificacion",
                    "tipo_documento",
                    "descripcion",
                    "responsable"
                ],
                "confidence_threshold": 0.8
            },
            "guia_valija": {
                "model_id": "custom-guia-valija",
                "fields": [
                    "numero_guia",
                    "fecha_envio",
                    "valija_numero",
                    "peso_total",
                    "cantidad_documentos",
                    "destino",
                    "transportista",
                    "observaciones"
                ],
                "confidence_threshold": 0.8
            },
            "nota_diplomatica": {
                "model_id": "custom-nota-diplomatica",
                "fields": [
                    "numero_nota",
                    "fecha",
                    "de",
                    "para",
                    "asunto",
                    "referencia",
                    "cuerpo_texto",
                    "firma"
                ],
                "confidence_threshold": 0.7
            }
        }

        # Estadísticas del agente
        self.stats = {
            "documents_processed": 0,
            "successful_extractions": 0,
            "failed_extractions": 0,
            "custom_models_trained": 0,
            "average_confidence": 0.0,
            "total_processing_time": 0.0
        }

        # Cache de resultados
        self.results_cache: Dict[str, ExtractionResult] = {}

    async def initialize(self) -> bool:
        """Inicializa el agente y conexiones con Azure"""
        try:
            if not AZURE_AVAILABLE:
                self.logger.error("Azure SDK no disponible")
                return False

            self.logger.info("Inicializando Azure Form Recognizer Agent")

            # Crear clientes
            credential = AzureKeyCredential(self.config.api_key)

            self.analysis_client = AsyncDocumentAnalysisClient(
                endpoint=self.config.endpoint,
                credential=credential
            )

            self.admin_client = DocumentModelAdministrationClient(
                endpoint=self.config.endpoint,
                credential=credential
            )

            # Validar conexión
            await self._validate_connection()

            # Verificar modelos personalizados
            await self._check_custom_models()

            self.logger.info("Azure Form Recognizer Agent inicializado exitosamente")
            return True

        except Exception as e:
            self.logger.error(f"Error inicializando Azure Form Recognizer Agent: {e}")
            return False

    async def process_diplomatic_document(self, file_path: Path,
                                        document_type: str = "auto",
                                        use_custom_model: bool = True) -> ExtractionResult:
        """Procesa un documento diplomático usando Form Recognizer"""
        start_time = datetime.now()

        try:
            self.logger.info(f"Procesando documento diplomático: {file_path}")

            # Crear resultado inicial
            result = ExtractionResult(
                document_id=f"doc_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                file_path=str(file_path),
                model_used=ModelType.PREBUILT_DOCUMENT,
                processing_status=DocumentProcessingStatus.PROCESSING,
                confidence_score=0.0
            )

            # Detectar tipo de documento si es automático
            if document_type == "auto":
                document_type = await self._detect_document_type(file_path)

            # Seleccionar modelo apropiado
            model_to_use = await self._select_model(document_type, use_custom_model)
            result.model_used = model_to_use

            # Procesar documento
            if model_to_use.value.startswith("custom-") and use_custom_model:
                extraction_data = await self._process_with_custom_model(file_path, model_to_use, document_type)
            else:
                extraction_data = await self._process_with_prebuilt_model(file_path, model_to_use)

            # Completar resultado
            result.extracted_data = extraction_data.get("extracted_data", {})
            result.tables = extraction_data.get("tables", [])
            result.key_value_pairs = extraction_data.get("key_value_pairs", {})
            result.entities = extraction_data.get("entities", [])
            result.confidence_score = extraction_data.get("average_confidence", 0.0)
            result.raw_response = extraction_data.get("raw_response")

            # Validar extracción
            await self._validate_extraction(result, document_type)

            # Determinar estado final
            if result.confidence_score >= 0.8:
                result.processing_status = DocumentProcessingStatus.COMPLETED
            elif result.confidence_score >= 0.6:
                result.processing_status = DocumentProcessingStatus.REQUIRES_REVIEW
                result.warnings.append("Confianza baja - requiere revisión manual")
            else:
                result.processing_status = DocumentProcessingStatus.FAILED
                result.errors.append("Confianza insuficiente para extracción automática")

            # Calcular tiempo de procesamiento
            processing_time = (datetime.now() - start_time).total_seconds()
            result.processing_time = processing_time

            # Actualizar estadísticas
            await self._update_stats(result)

            # Cachear resultado
            self.results_cache[result.document_id] = result

            self.logger.info(
                f"Documento procesado: {result.document_id} "
                f"(confianza: {result.confidence_score:.2f}, "
                f"tiempo: {processing_time:.2f}s)"
            )

            return result

        except Exception as e:
            self.logger.error(f"Error procesando documento {file_path}: {e}")

            result.processing_status = DocumentProcessingStatus.FAILED
            result.errors.append(str(e))
            result.processing_time = (datetime.now() - start_time).total_seconds()

            return result

    async def train_custom_model(self, training_config: CustomModelTraining) -> Dict[str, Any]:
        """Entrena un modelo personalizado para documentos diplomáticos"""
        try:
            self.logger.info(f"Entrenando modelo personalizado: {training_config.model_name}")

            if not self.admin_client:
                raise Exception("Cliente de administración no inicializado")

            # Preparar datos de entrenamiento
            training_data = await self._prepare_training_data(training_config)

            # Iniciar entrenamiento
            training_poller = self.admin_client.begin_build_document_model(
                build_mode="template",  # o "neural" para documentos más variados
                blob_container_url=training_data["container_url"],
                model_id=training_config.model_name,
                description=training_config.model_description
            )

            # Esperar finalización del entrenamiento
            custom_model = training_poller.result()

            # Actualizar configuración local
            self.config.custom_models[training_config.document_type] = custom_model.model_id

            # Actualizar modelos diplomáticos
            if training_config.document_type in self.diplomatic_models:
                self.diplomatic_models[training_config.document_type]["model_id"] = custom_model.model_id

            self.stats["custom_models_trained"] += 1

            self.logger.info(f"Modelo entrenado exitosamente: {custom_model.model_id}")

            return {
                "success": True,
                "model_id": custom_model.model_id,
                "model_info": {
                    "created_on": custom_model.created_on.isoformat(),
                    "description": custom_model.description,
                    "doc_types": list(custom_model.doc_types.keys()) if custom_model.doc_types else []
                }
            }

        except Exception as e:
            self.logger.error(f"Error entrenando modelo personalizado: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def extract_hoja_remision_data(self, file_path: Path) -> Dict[str, Any]:
        """Extrae datos específicos de una hoja de remisión"""
        try:
            result = await self.process_diplomatic_document(file_path, "hoja_remision", True)

            if result.processing_status == DocumentProcessingStatus.FAILED:
                return {"error": "Failed to process document", "errors": result.errors}

            # Mapear campos específicos de hoja de remisión
            hoja_data = {
                "numero_remision": result.extracted_data.get("numero_remision", ""),
                "fecha": result.extracted_data.get("fecha", ""),
                "origen": result.extracted_data.get("origen", ""),
                "destino": result.extracted_data.get("destino", ""),
                "clasificacion": result.extracted_data.get("clasificacion", ""),
                "tipo_documento": result.extracted_data.get("tipo_documento", ""),
                "descripcion": result.extracted_data.get("descripcion", ""),
                "responsable": result.extracted_data.get("responsable", ""),
                "confidence_score": result.confidence_score,
                "processing_status": result.processing_status.value,
                "requires_review": result.processing_status == DocumentProcessingStatus.REQUIRES_REVIEW
            }

            return hoja_data

        except Exception as e:
            self.logger.error(f"Error extrayendo datos de hoja de remisión: {e}")
            return {"error": str(e)}

    async def extract_guia_valija_data(self, file_path: Path) -> Dict[str, Any]:
        """Extrae datos específicos de una guía de valija"""
        try:
            result = await self.process_diplomatic_document(file_path, "guia_valija", True)

            if result.processing_status == DocumentProcessingStatus.FAILED:
                return {"error": "Failed to process document", "errors": result.errors}

            # Mapear campos específicos de guía de valija
            valija_data = {
                "numero_guia": result.extracted_data.get("numero_guia", ""),
                "fecha_envio": result.extracted_data.get("fecha_envio", ""),
                "valija_numero": result.extracted_data.get("valija_numero", ""),
                "peso_total": result.extracted_data.get("peso_total", ""),
                "cantidad_documentos": result.extracted_data.get("cantidad_documentos", ""),
                "destino": result.extracted_data.get("destino", ""),
                "transportista": result.extracted_data.get("transportista", ""),
                "observaciones": result.extracted_data.get("observaciones", ""),
                "confidence_score": result.confidence_score,
                "processing_status": result.processing_status.value,
                "requires_review": result.processing_status == DocumentProcessingStatus.REQUIRES_REVIEW
            }

            return valija_data

        except Exception as e:
            self.logger.error(f"Error extrayendo datos de guía de valija: {e}")
            return {"error": str(e)}

    async def get_extraction_result(self, document_id: str) -> Optional[ExtractionResult]:
        """Obtiene el resultado de extracción por ID"""
        return self.results_cache.get(document_id)

    async def list_custom_models(self) -> List[Dict[str, Any]]:
        """Lista todos los modelos personalizados disponibles"""
        try:
            if not self.admin_client:
                raise Exception("Cliente de administración no inicializado")

            models = []
            async for model in self.admin_client.list_document_models():
                model_info = {
                    "model_id": model.model_id,
                    "description": model.description,
                    "created_on": model.created_on.isoformat() if model.created_on else None,
                    "api_version": model.api_version,
                    "doc_types": list(model.doc_types.keys()) if model.doc_types else []
                }
                models.append(model_info)

            return models

        except Exception as e:
            self.logger.error(f"Error listando modelos personalizados: {e}")
            return []

    async def get_agent_statistics(self) -> Dict[str, Any]:
        """Obtiene estadísticas del agente"""
        return {
            "agent_id": self.agent_id,
            "agent_type": "Azure Form Recognizer Specialist",
            "statistics": self.stats,
            "supported_documents": list(self.diplomatic_models.keys()),
            "custom_models": self.config.custom_models,
            "cache_size": len(self.results_cache),
            "azure_endpoint": self.config.endpoint
        }

    # Métodos privados

    async def _validate_connection(self) -> None:
        """Valida la conexión con Azure Form Recognizer"""
        try:
            # Intentar listar modelos para verificar conexión
            models = self.admin_client.list_document_models()
            model_count = 0
            async for model in models:
                model_count += 1
                if model_count >= 1:  # Solo necesitamos verificar que funciona
                    break

            self.logger.info(f"Conexión con Azure Form Recognizer validada ({model_count} modelos disponibles)")

        except Exception as e:
            raise Exception(f"Error validando conexión con Azure: {e}")

    async def _check_custom_models(self) -> None:
        """Verifica la disponibilidad de modelos personalizados"""
        try:
            available_models = await self.list_custom_models()

            for doc_type, model_config in self.diplomatic_models.items():
                model_id = model_config["model_id"]
                model_exists = any(m["model_id"] == model_id for m in available_models)

                if model_exists:
                    self.logger.info(f"Modelo personalizado disponible: {model_id}")
                else:
                    self.logger.warning(f"Modelo personalizado no encontrado: {model_id}")

        except Exception as e:
            self.logger.error(f"Error verificando modelos personalizados: {e}")

    async def _detect_document_type(self, file_path: Path) -> str:
        """Detecta automáticamente el tipo de documento"""
        try:
            # Leer contenido del archivo para análisis básico
            content = ""
            if file_path.suffix.lower() == ".txt":
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read().lower()

            # Patrones de detección
            patterns = {
                "hoja_remision": ["hoja de remisión", "remisión", "hr-", "número de remisión"],
                "guia_valija": ["guía de valija", "valija diplomática", "gv-", "número de guía"],
                "nota_diplomatica": ["nota diplomática", "nota verbal", "excelencia", "embajada"]
            }

            # Buscar coincidencias
            best_match = "comunicacion_oficial"  # Default
            max_matches = 0

            for doc_type, keywords in patterns.items():
                matches = sum(1 for keyword in keywords if keyword in content)
                if matches > max_matches:
                    max_matches = matches
                    best_match = doc_type

            self.logger.info(f"Tipo de documento detectado: {best_match}")
            return best_match

        except Exception as e:
            self.logger.error(f"Error detectando tipo de documento: {e}")
            return "comunicacion_oficial"

    async def _select_model(self, document_type: str, use_custom: bool) -> ModelType:
        """Selecciona el modelo apropiado para el procesamiento"""
        if use_custom and document_type in self.diplomatic_models:
            model_id = self.diplomatic_models[document_type]["model_id"]

            # Verificar si el modelo personalizado existe
            if model_id in self.config.custom_models.values():
                return ModelType(f"custom-{document_type}")

        # Fallback a modelo prebuilt
        return ModelType.PREBUILT_DOCUMENT

    async def _process_with_custom_model(self, file_path: Path, model: ModelType,
                                       document_type: str) -> Dict[str, Any]:
        """Procesa documento con modelo personalizado"""
        try:
            model_id = self.diplomatic_models[document_type]["model_id"]

            with open(file_path, "rb") as document:
                poller = await self.analysis_client.begin_analyze_document(
                    model_id=model_id,
                    document=document
                )
                result = await poller.result()

            return await self._extract_custom_model_data(result, document_type)

        except Exception as e:
            self.logger.error(f"Error procesando con modelo personalizado: {e}")
            # Fallback a modelo prebuilt
            return await self._process_with_prebuilt_model(file_path, ModelType.PREBUILT_DOCUMENT)

    async def _process_with_prebuilt_model(self, file_path: Path, model: ModelType) -> Dict[str, Any]:
        """Procesa documento con modelo prebuilt"""
        try:
            with open(file_path, "rb") as document:
                poller = await self.analysis_client.begin_analyze_document(
                    model_id=model.value,
                    document=document
                )
                result = await poller.result()

            return await self._extract_prebuilt_model_data(result)

        except Exception as e:
            self.logger.error(f"Error procesando con modelo prebuilt: {e}")
            raise

    async def _extract_custom_model_data(self, result, document_type: str) -> Dict[str, Any]:
        """Extrae datos de resultado de modelo personalizado"""
        extracted_data = {}
        confidence_scores = []

        # Extraer campos específicos del documento
        expected_fields = self.diplomatic_models[document_type]["fields"]

        for document in result.documents:
            for field_name in expected_fields:
                field = document.fields.get(field_name)
                if field:
                    extracted_data[field_name] = field.value
                    confidence_scores.append(field.confidence)

        # Extraer tablas
        tables = []
        for table in result.tables:
            table_data = {
                "row_count": table.row_count,
                "column_count": table.column_count,
                "cells": []
            }
            for cell in table.cells:
                cell_data = {
                    "content": cell.content,
                    "row_index": cell.row_index,
                    "column_index": cell.column_index,
                    "confidence": cell.confidence
                }
                table_data["cells"].append(cell_data)
            tables.append(table_data)

        # Extraer pares clave-valor
        key_value_pairs = {}
        for kv_pair in result.key_value_pairs:
            if kv_pair.key and kv_pair.value:
                key_content = kv_pair.key.content
                value_content = kv_pair.value.content
                confidence = min(kv_pair.key.confidence, kv_pair.value.confidence)

                key_value_pairs[key_content] = value_content
                confidence_scores.append(confidence)

        # Calcular confianza promedio
        average_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0

        return {
            "extracted_data": extracted_data,
            "tables": tables,
            "key_value_pairs": key_value_pairs,
            "entities": [],  # Los modelos personalizados no extraen entidades
            "average_confidence": average_confidence,
            "raw_response": self._convert_to_dict(result)
        }

    async def _extract_prebuilt_model_data(self, result) -> Dict[str, Any]:
        """Extrae datos de resultado de modelo prebuilt"""
        extracted_data = {}
        confidence_scores = []

        # Extraer contenido por páginas
        content_by_page = []
        for page in result.pages:
            page_content = {
                "page_number": page.page_number,
                "lines": [line.content for line in page.lines],
                "words": [{"content": word.content, "confidence": word.confidence} for word in page.words]
            }
            content_by_page.append(page_content)
            confidence_scores.extend([word.confidence for word in page.words])

        # Extraer tablas
        tables = []
        for table in result.tables:
            table_data = {
                "row_count": table.row_count,
                "column_count": table.column_count,
                "cells": []
            }
            for cell in table.cells:
                cell_data = {
                    "content": cell.content,
                    "row_index": cell.row_index,
                    "column_index": cell.column_index,
                    "confidence": cell.confidence
                }
                table_data["cells"].append(cell_data)
                confidence_scores.append(cell.confidence)
            tables.append(table_data)

        # Extraer pares clave-valor
        key_value_pairs = {}
        for kv_pair in result.key_value_pairs:
            if kv_pair.key and kv_pair.value:
                key_content = kv_pair.key.content
                value_content = kv_pair.value.content
                confidence = min(kv_pair.key.confidence, kv_pair.value.confidence)

                key_value_pairs[key_content] = value_content
                confidence_scores.append(confidence)

        # Agregar contenido por páginas a extracted_data
        extracted_data["content_by_page"] = content_by_page

        # Calcular confianza promedio
        average_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0

        return {
            "extracted_data": extracted_data,
            "tables": tables,
            "key_value_pairs": key_value_pairs,
            "entities": [],
            "average_confidence": average_confidence,
            "raw_response": self._convert_to_dict(result)
        }

    async def _validate_extraction(self, result: ExtractionResult, document_type: str) -> None:
        """Valida el resultado de extracción"""
        if document_type in self.diplomatic_models:
            expected_fields = self.diplomatic_models[document_type]["fields"]
            missing_fields = []

            for field in expected_fields:
                if field not in result.extracted_data or not result.extracted_data[field]:
                    missing_fields.append(field)

            if missing_fields:
                result.warnings.append(f"Campos faltantes: {', '.join(missing_fields)}")

        # Validar confianza mínima
        threshold = self.diplomatic_models.get(document_type, {}).get("confidence_threshold", 0.7)
        if result.confidence_score < threshold:
            result.warnings.append(f"Confianza ({result.confidence_score:.2f}) por debajo del umbral ({threshold})")

    async def _update_stats(self, result: ExtractionResult) -> None:
        """Actualiza estadísticas del agente"""
        self.stats["documents_processed"] += 1
        self.stats["total_processing_time"] += result.processing_time

        if result.processing_status == DocumentProcessingStatus.COMPLETED:
            self.stats["successful_extractions"] += 1
        elif result.processing_status == DocumentProcessingStatus.FAILED:
            self.stats["failed_extractions"] += 1

        # Actualizar confianza promedio
        total_docs = self.stats["documents_processed"]
        current_avg = self.stats["average_confidence"]
        new_avg = ((current_avg * (total_docs - 1)) + result.confidence_score) / total_docs
        self.stats["average_confidence"] = new_avg

    async def _prepare_training_data(self, config: CustomModelTraining) -> Dict[str, Any]:
        """Prepara datos para entrenamiento de modelo personalizado"""
        # TODO: Implementar preparación de datos de entrenamiento
        # Esto incluiría subir documentos a Azure Storage y crear archivos de etiquetas
        return {
            "container_url": f"https://{self.config.account_name}.blob.core.windows.net/training-data",
            "labels_file": str(config.labels_file) if config.labels_file else None
        }

    def _convert_to_dict(self, azure_result) -> Dict[str, Any]:
        """Convierte resultado de Azure a diccionario serializable"""
        try:
            # Implementación básica - en producción sería más robusta
            return {
                "model_id": getattr(azure_result, 'model_id', 'unknown'),
                "api_version": getattr(azure_result, 'api_version', 'unknown'),
                "created_on": datetime.now().isoformat()
            }
        except Exception:
            return {"converted": True, "timestamp": datetime.now().isoformat()}


# Función principal para testing
async def main():
    """Función principal para testing del agente"""
    logging.basicConfig(level=logging.INFO)

    # Configuración de ejemplo
    config = FormRecognizerConfig(
        endpoint="https://your-region.api.cognitive.microsoft.com/",
        api_key="your_api_key_here",
        subscription_id="your_subscription_id",
        resource_group="your_resource_group",
        account_name="your_storage_account"
    )

    agent = AzureFormRecognizerAgent(config)

    # Solo ejecutar si Azure está disponible
    if AZURE_AVAILABLE and config.api_key != "your_api_key_here":
        await agent.initialize()

        # Ejemplo de procesamiento
        test_file = Path("test_document.pdf")
        if test_file.exists():
            result = await agent.process_diplomatic_document(test_file)
            print(f"Resultado: {result}")

    # Obtener estadísticas
    stats = await agent.get_agent_statistics()
    print(f"Estadísticas del agente: {stats}")


if __name__ == "__main__":
    asyncio.run(main())
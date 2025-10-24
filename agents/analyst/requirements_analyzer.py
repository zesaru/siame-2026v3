#!/usr/bin/env python3
"""
SIAME 2026v3 - Requirements Analyzer Agent
Subagente especializado en análisis de documentos diplomáticos y generación de especificaciones técnicas

Este agente entiende:
- Tipos específicos de documentos diplomáticos (Hojas de remisión OGA, PCO, PRU, etc.)
- Guías de valija (entrada/salida, ordinaria/extraordinaria)
- Niveles de clasificación de seguridad diplomática
- Requerimientos específicos de Azure Form Recognizer
- Estructura de datos del sector diplomático

Genera especificaciones técnicas detalladas basadas en conversaciones en lenguaje natural.
"""

import asyncio
import logging
import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum

# Importaciones internas
import uuid


class DocumentSubtype(Enum):
    """Subtipos específicos de documentos diplomáticos"""
    # Hojas de Remisión por área
    HOJA_OGA = "hoja_oga"  # Oficina de Gestión Administrativa
    HOJA_PCO = "hoja_pco"  # Protocolo y Ceremonial Oficial
    HOJA_PRU = "hoja_pru"  # Política y Relaciones Exteriores Unilaterales
    HOJA_PMU = "hoja_pmu"  # Política y Relaciones Exteriores Multilaterales
    HOJA_ECO = "hoja_eco"  # Asuntos Económicos
    HOJA_CON = "hoja_con"  # Asuntos Consulares
    HOJA_CUL = "hoja_cul"  # Asuntos Culturales
    HOJA_TEC = "hoja_tec"  # Cooperación Técnica

    # Guías de Valija
    GUIA_ENTRADA_ORD = "guia_entrada_ordinaria"
    GUIA_ENTRADA_EXT = "guia_entrada_extraordinaria"
    GUIA_SALIDA_ORD = "guia_salida_ordinaria"
    GUIA_SALIDA_EXT = "guia_salida_extraordinaria"

    # Otros documentos específicos
    NOTA_VERBAL = "nota_verbal"
    AIDE_MEMOIRE = "aide_memoire"
    MEMORANDUM_ENTENDIMIENTO = "memorandum_entendimiento"
    ACUERDO_COOPERACION = "acuerdo_cooperacion"
    PROTOCOLO_ADICIONAL = "protocolo_adicional"


class SecurityClassification(Enum):
    """Niveles específicos de clasificación diplomática"""
    PUBLICO = "publico"
    USO_OFICIAL = "uso_oficial"
    RESERVADO = "reservado"
    CONFIDENCIAL = "confidencial"
    SECRETO = "secreto"
    ULTRA_SECRETO = "ultra_secreto"


class ProcessingComplexity(Enum):
    """Niveles de complejidad de procesamiento"""
    SIMPLE = "simple"      # Documentos con estructura fija
    MEDIUM = "medium"      # Documentos con variaciones menores
    COMPLEX = "complex"    # Documentos con estructura variable
    EXPERT = "expert"      # Documentos que requieren análisis especializado


@dataclass
class DocumentField:
    """Campo específico de un documento diplomático"""
    name: str
    display_name: str
    field_type: str  # text, date, number, select, multiline
    required: bool
    validation_rules: List[str] = field(default_factory=list)
    possible_values: Optional[List[str]] = None
    extraction_patterns: List[str] = field(default_factory=list)
    confidence_threshold: float = 0.8
    position_hints: List[str] = field(default_factory=list)
    related_fields: List[str] = field(default_factory=list)


@dataclass
class DocumentTemplate:
    """Plantilla de documento diplomático"""
    document_type: DocumentSubtype
    display_name: str
    description: str
    security_level: SecurityClassification
    complexity: ProcessingComplexity
    fields: List[DocumentField] = field(default_factory=list)
    required_sections: List[str] = field(default_factory=list)
    optional_sections: List[str] = field(default_factory=list)
    validation_rules: List[str] = field(default_factory=list)
    azure_model_requirements: Dict[str, Any] = field(default_factory=dict)
    sample_formats: List[str] = field(default_factory=list)


@dataclass
class TechnicalSpecification:
    """Especificación técnica generada"""
    id: str
    title: str
    description: str
    document_types: List[DocumentSubtype]
    created_at: datetime = field(default_factory=datetime.now)

    # Especificaciones de Azure Form Recognizer
    azure_config: Dict[str, Any] = field(default_factory=dict)

    # Especificaciones de base de datos
    database_schema: Dict[str, Any] = field(default_factory=dict)

    # Especificaciones de API
    api_endpoints: List[Dict[str, Any]] = field(default_factory=list)

    # Especificaciones de seguridad
    security_requirements: Dict[str, Any] = field(default_factory=dict)

    # Especificaciones de frontend
    ui_components: List[Dict[str, Any]] = field(default_factory=list)

    # Métricas y validación
    performance_requirements: Dict[str, Any] = field(default_factory=dict)

    # Documentación generada
    technical_documentation: str = ""
    implementation_notes: List[str] = field(default_factory=list)


class RequirementsAnalyzerAgent:
    """Agente analizador de requerimientos para documentos diplomáticos"""

    def __init__(self, agent_id: str = None):
        self.agent_id = agent_id or f"req_analyzer_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.logger = logging.getLogger(__name__)

        # Plantillas de documentos diplomáticos
        self.document_templates = self._initialize_document_templates()

        # Patrones de conversación para análisis
        self.conversation_patterns = self._initialize_conversation_patterns()

        # Especificaciones generadas
        self.generated_specs: Dict[str, TechnicalSpecification] = {}

        # Estadísticas del agente
        self.stats = {
            "requirements_analyzed": 0,
            "specifications_generated": 0,
            "document_types_covered": 0,
            "conversations_processed": 0
        }

    async def analyze_requirements_from_conversation(self, conversation: str,
                                                   context: Optional[Dict[str, Any]] = None) -> TechnicalSpecification:
        """Analiza requerimientos a partir de una conversación en lenguaje natural"""
        try:
            self.logger.info("Analizando requerimientos desde conversación")

            # Extraer información clave de la conversación
            extracted_info = await self._extract_conversation_info(conversation, context)

            # Identificar tipos de documentos mencionados
            document_types = await self._identify_document_types(extracted_info)

            # Generar especificación técnica
            spec = await self._generate_technical_specification(extracted_info, document_types)

            # Validar y refinar especificación
            await self._validate_and_refine_specification(spec)

            # Almacenar especificación
            self.generated_specs[spec.id] = spec

            # Actualizar estadísticas
            self.stats["requirements_analyzed"] += 1
            self.stats["specifications_generated"] += 1
            self.stats["conversations_processed"] += 1

            self.logger.info(f"Especificación técnica generada: {spec.id}")
            return spec

        except Exception as e:
            self.logger.error(f"Error analizando requerimientos: {e}")
            raise

    async def analyze_document_type_requirements(self, document_type: DocumentSubtype,
                                               additional_requirements: Optional[List[str]] = None) -> Dict[str, Any]:
        """Analiza requerimientos específicos para un tipo de documento"""
        try:
            template = self.document_templates.get(document_type)
            if not template:
                raise ValueError(f"Tipo de documento no soportado: {document_type}")

            requirements = {
                "document_info": {
                    "type": document_type.value,
                    "display_name": template.display_name,
                    "description": template.description,
                    "security_level": template.security_level.value,
                    "complexity": template.complexity.value
                },
                "field_requirements": [],
                "azure_form_recognizer": template.azure_model_requirements,
                "database_requirements": await self._generate_database_requirements(template),
                "api_requirements": await self._generate_api_requirements(template),
                "security_requirements": await self._generate_security_requirements(template),
                "ui_requirements": await self._generate_ui_requirements(template)
            }

            # Agregar campos específicos
            for field in template.fields:
                field_req = {
                    "name": field.name,
                    "display_name": field.display_name,
                    "type": field.field_type,
                    "required": field.required,
                    "validation": field.validation_rules,
                    "extraction_patterns": field.extraction_patterns,
                    "confidence_threshold": field.confidence_threshold
                }
                requirements["field_requirements"].append(field_req)

            return requirements

        except Exception as e:
            self.logger.error(f"Error analizando requerimientos del documento: {e}")
            raise

    async def generate_azure_form_recognizer_config(self, document_types: List[DocumentSubtype]) -> Dict[str, Any]:
        """Genera configuración específica para Azure Form Recognizer"""
        try:
            config = {
                "models": {},
                "training_requirements": {},
                "field_mappings": {},
                "confidence_thresholds": {},
                "validation_rules": {}
            }

            for doc_type in document_types:
                template = self.document_templates.get(doc_type)
                if not template:
                    continue

                model_name = f"siame-{doc_type.value.replace('_', '-')}"

                config["models"][doc_type.value] = {
                    "model_name": model_name,
                    "model_description": f"Modelo para {template.display_name}",
                    "complexity": template.complexity.value,
                    "expected_accuracy": self._get_expected_accuracy(template.complexity),
                    "training_data_requirements": {
                        "minimum_samples": self._get_minimum_samples(template.complexity),
                        "recommended_samples": self._get_recommended_samples(template.complexity),
                        "sample_diversity": self._get_sample_diversity_requirements(template)
                    }
                }

                # Configuración de campos
                field_config = {}
                for field in template.fields:
                    field_config[field.name] = {
                        "type": field.field_type,
                        "required": field.required,
                        "confidence_threshold": field.confidence_threshold,
                        "extraction_patterns": field.extraction_patterns,
                        "validation": field.validation_rules
                    }

                config["field_mappings"][doc_type.value] = field_config
                config["confidence_thresholds"][doc_type.value] = template.azure_model_requirements.get("min_confidence", 0.8)

            return config

        except Exception as e:
            self.logger.error(f"Error generando configuración Azure: {e}")
            raise

    async def generate_database_schema(self, document_types: List[DocumentSubtype]) -> Dict[str, Any]:
        """Genera esquema de base de datos para tipos de documentos"""
        try:
            schema = {
                "tables": {},
                "relationships": [],
                "indexes": [],
                "constraints": [],
                "security_policies": []
            }

            # Tabla principal de documentos
            schema["tables"]["diplomatic_documents"] = {
                "columns": {
                    "id": {"type": "UUID", "primary_key": True, "default": "gen_random_uuid()"},
                    "document_type": {"type": "VARCHAR(50)", "not_null": True},
                    "document_subtype": {"type": "VARCHAR(50)", "not_null": True},
                    "security_classification": {"type": "VARCHAR(20)", "not_null": True},
                    "title": {"type": "TEXT"},
                    "content": {"type": "TEXT"},
                    "file_path": {"type": "TEXT"},
                    "file_hash": {"type": "VARCHAR(64)"},
                    "created_at": {"type": "TIMESTAMP", "default": "CURRENT_TIMESTAMP"},
                    "updated_at": {"type": "TIMESTAMP", "default": "CURRENT_TIMESTAMP"},
                    "created_by": {"type": "UUID", "not_null": True},
                    "department": {"type": "VARCHAR(100)"},
                    "status": {"type": "VARCHAR(20)", "default": "'pending'"}
                }
            }

            # Tablas específicas por tipo de documento
            for doc_type in document_types:
                table_name = f"doc_{doc_type.value}"
                template = self.document_templates.get(doc_type)

                if template:
                    columns = {
                        "id": {"type": "UUID", "primary_key": True, "default": "gen_random_uuid()"},
                        "document_id": {"type": "UUID", "not_null": True, "foreign_key": "diplomatic_documents.id"}
                    }

                    # Agregar campos específicos
                    for field in template.fields:
                        column_type = self._get_sql_type(field.field_type)
                        columns[field.name] = {
                            "type": column_type,
                            "not_null": field.required
                        }

                    schema["tables"][table_name] = {"columns": columns}

                    # Agregar relación
                    schema["relationships"].append({
                        "from_table": table_name,
                        "from_column": "document_id",
                        "to_table": "diplomatic_documents",
                        "to_column": "id",
                        "type": "one_to_one"
                    })

            # Tabla de auditoría
            schema["tables"]["document_audit_log"] = {
                "columns": {
                    "id": {"type": "UUID", "primary_key": True, "default": "gen_random_uuid()"},
                    "document_id": {"type": "UUID", "not_null": True},
                    "action": {"type": "VARCHAR(50)", "not_null": True},
                    "user_id": {"type": "UUID", "not_null": True},
                    "timestamp": {"type": "TIMESTAMP", "default": "CURRENT_TIMESTAMP"},
                    "ip_address": {"type": "INET"},
                    "user_agent": {"type": "TEXT"},
                    "details": {"type": "JSONB"}
                }
            }

            # Índices
            schema["indexes"] = [
                {"table": "diplomatic_documents", "columns": ["document_type", "document_subtype"]},
                {"table": "diplomatic_documents", "columns": ["security_classification"]},
                {"table": "diplomatic_documents", "columns": ["created_at"]},
                {"table": "diplomatic_documents", "columns": ["department"]},
                {"table": "document_audit_log", "columns": ["document_id", "timestamp"]}
            ]

            # Políticas de seguridad
            schema["security_policies"] = [
                {
                    "table": "diplomatic_documents",
                    "policy": "security_level_access",
                    "description": "Controla acceso basado en nivel de clasificación"
                },
                {
                    "table": "document_audit_log",
                    "policy": "audit_retention",
                    "description": "Retención de logs de auditoría por 7 años"
                }
            ]

            return schema

        except Exception as e:
            self.logger.error(f"Error generando esquema de base de datos: {e}")
            raise

    async def generate_api_specification(self, document_types: List[DocumentSubtype]) -> Dict[str, Any]:
        """Genera especificación de API para tipos de documentos"""
        try:
            api_spec = {
                "openapi": "3.0.0",
                "info": {
                    "title": "SIAME Diplomatic Documents API",
                    "version": "3.0.0",
                    "description": "API para gestión de documentos diplomáticos"
                },
                "paths": {},
                "components": {
                    "schemas": {},
                    "securitySchemes": {
                        "BearerAuth": {
                            "type": "http",
                            "scheme": "bearer",
                            "bearerFormat": "JWT"
                        }
                    }
                },
                "security": [{"BearerAuth": []}]
            }

            # Endpoints comunes
            api_spec["paths"]["/api/v1/documents"] = {
                "get": {
                    "summary": "Listar documentos diplomáticos",
                    "parameters": [
                        {"name": "type", "in": "query", "schema": {"type": "string"}},
                        {"name": "security_level", "in": "query", "schema": {"type": "string"}},
                        {"name": "department", "in": "query", "schema": {"type": "string"}},
                        {"name": "page", "in": "query", "schema": {"type": "integer", "default": 1}},
                        {"name": "limit", "in": "query", "schema": {"type": "integer", "default": 50}}
                    ],
                    "responses": {
                        "200": {"description": "Lista de documentos"},
                        "403": {"description": "Acceso denegado"}
                    }
                },
                "post": {
                    "summary": "Crear nuevo documento",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "multipart/form-data": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "file": {"type": "string", "format": "binary"},
                                        "document_type": {"type": "string"},
                                        "security_classification": {"type": "string"}
                                    }
                                }
                            }
                        }
                    },
                    "responses": {
                        "201": {"description": "Documento creado"},
                        "400": {"description": "Datos inválidos"},
                        "403": {"description": "Acceso denegado"}
                    }
                }
            }

            # Endpoints específicos por tipo de documento
            for doc_type in document_types:
                template = self.document_templates.get(doc_type)
                if not template:
                    continue

                endpoint_name = f"/api/v1/documents/{doc_type.value.replace('_', '-')}"

                # Schema del documento
                schema_name = f"{doc_type.value.replace('_', '')}Schema"
                properties = {}

                for field in template.fields:
                    field_schema = {"type": self._get_openapi_type(field.field_type)}
                    if field.possible_values:
                        field_schema["enum"] = field.possible_values
                    properties[field.name] = field_schema

                api_spec["components"]["schemas"][schema_name] = {
                    "type": "object",
                    "properties": properties,
                    "required": [f.name for f in template.fields if f.required]
                }

                # Endpoints específicos
                api_spec["paths"][endpoint_name] = {
                    "get": {
                        "summary": f"Listar documentos {template.display_name}",
                        "responses": {
                            "200": {
                                "description": f"Lista de {template.display_name}",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "array",
                                            "items": {"$ref": f"#/components/schemas/{schema_name}"}
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "post": {
                        "summary": f"Crear {template.display_name}",
                        "requestBody": {
                            "required": True,
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": f"#/components/schemas/{schema_name}"}
                                }
                            }
                        },
                        "responses": {
                            "201": {"description": "Documento creado"}
                        }
                    }
                }

            return api_spec

        except Exception as e:
            self.logger.error(f"Error generando especificación API: {e}")
            raise

    async def get_agent_statistics(self) -> Dict[str, Any]:
        """Obtiene estadísticas del agente"""
        return {
            "agent_id": self.agent_id,
            "agent_type": "Requirements Analyzer",
            "statistics": self.stats,
            "supported_document_types": [dt.value for dt in DocumentSubtype],
            "security_classifications": [sc.value for sc in SecurityClassification],
            "generated_specifications": len(self.generated_specs),
            "document_templates": len(self.document_templates)
        }

    # Métodos privados

    def _initialize_document_templates(self) -> Dict[DocumentSubtype, DocumentTemplate]:
        """Inicializa plantillas de documentos diplomáticos"""
        templates = {}

        # Hoja de Remisión OGA (Oficina de Gestión Administrativa)
        templates[DocumentSubtype.HOJA_OGA] = DocumentTemplate(
            document_type=DocumentSubtype.HOJA_OGA,
            display_name="Hoja de Remisión OGA",
            description="Hoja de remisión para documentos de la Oficina de Gestión Administrativa",
            security_level=SecurityClassification.USO_OFICIAL,
            complexity=ProcessingComplexity.SIMPLE,
            fields=[
                DocumentField("numero_remision", "Número de Remisión", "text", True,
                            extraction_patterns=[r"HR-OGA-\d{4}-\d{3}", r"Remisión\s*N[°º]?\s*(\S+)"]),
                DocumentField("fecha", "Fecha", "date", True,
                            extraction_patterns=[r"\d{1,2}[-/]\d{1,2}[-/]\d{4}", r"\d{4}[-/]\d{1,2}[-/]\d{1,2}"]),
                DocumentField("origen", "Oficina de Origen", "text", True,
                            extraction_patterns=[r"Origen:\s*(.+)", r"De:\s*(.+)"]),
                DocumentField("destino", "Destino", "text", True,
                            extraction_patterns=[r"Destino:\s*(.+)", r"Para:\s*(.+)"]),
                DocumentField("asunto", "Asunto", "text", True),
                DocumentField("descripcion", "Descripción", "multiline", False),
                DocumentField("responsable", "Responsable", "text", True),
                DocumentField("clasificacion", "Clasificación", "select", True,
                            possible_values=["USO OFICIAL", "RESERVADO", "CONFIDENCIAL"])
            ],
            azure_model_requirements={
                "min_confidence": 0.85,
                "model_type": "custom",
                "training_samples": 50
            }
        )

        # Hoja de Remisión PCO (Protocolo y Ceremonial Oficial)
        templates[DocumentSubtype.HOJA_PCO] = DocumentTemplate(
            document_type=DocumentSubtype.HOJA_PCO,
            display_name="Hoja de Remisión PCO",
            description="Hoja de remisión para documentos de Protocolo y Ceremonial Oficial",
            security_level=SecurityClassification.RESERVADO,
            complexity=ProcessingComplexity.MEDIUM,
            fields=[
                DocumentField("numero_remision", "Número de Remisión", "text", True,
                            extraction_patterns=[r"HR-PCO-\d{4}-\d{3}", r"PCO-\d+/\d{4}"]),
                DocumentField("fecha", "Fecha", "date", True),
                DocumentField("evento_protocolar", "Evento Protocolar", "text", True),
                DocumentField("dignatarios", "Dignatarios Involucrados", "multiline", False),
                DocumentField("lugar_evento", "Lugar del Evento", "text", False),
                DocumentField("fecha_evento", "Fecha del Evento", "date", False),
                DocumentField("nivel_protocolo", "Nivel de Protocolo", "select", True,
                            possible_values=["ALTO", "MEDIO", "BÁSICO"]),
                DocumentField("requerimientos_especiales", "Requerimientos Especiales", "multiline", False)
            ],
            azure_model_requirements={
                "min_confidence": 0.8,
                "model_type": "custom",
                "training_samples": 75
            }
        )

        # Hoja de Remisión PRU (Política y Relaciones Exteriores Unilaterales)
        templates[DocumentSubtype.HOJA_PRU] = DocumentTemplate(
            document_type=DocumentSubtype.HOJA_PRU,
            display_name="Hoja de Remisión PRU",
            description="Hoja de remisión para Política y Relaciones Exteriores Unilaterales",
            security_level=SecurityClassification.CONFIDENCIAL,
            complexity=ProcessingComplexity.COMPLEX,
            fields=[
                DocumentField("numero_remision", "Número de Remisión", "text", True,
                            extraction_patterns=[r"HR-PRU-\d{4}-\d{3}", r"PRU-\d+/\d{4}"]),
                DocumentField("pais_objetivo", "País Objetivo", "text", True),
                DocumentField("tipo_relacion", "Tipo de Relación", "select", True,
                            possible_values=["BILATERAL", "REGIONAL", "ESPECIAL"]),
                DocumentField("area_tematica", "Área Temática", "select", True,
                            possible_values=["POLÍTICA", "ECONÓMICA", "CULTURAL", "TÉCNICA", "MILITAR"]),
                DocumentField("urgencia", "Nivel de Urgencia", "select", True,
                            possible_values=["ALTA", "MEDIA", "BAJA"]),
                DocumentField("impacto_politico", "Impacto Político", "multiline", False),
                DocumentField("recomendaciones", "Recomendaciones", "multiline", False)
            ],
            azure_model_requirements={
                "min_confidence": 0.75,
                "model_type": "custom",
                "training_samples": 100
            }
        )

        # Guía de Valija Entrada Ordinaria
        templates[DocumentSubtype.GUIA_ENTRADA_ORD] = DocumentTemplate(
            document_type=DocumentSubtype.GUIA_ENTRADA_ORD,
            display_name="Guía de Valija - Entrada Ordinaria",
            description="Guía para valija diplomática de entrada en envío ordinario",
            security_level=SecurityClassification.USO_OFICIAL,
            complexity=ProcessingComplexity.SIMPLE,
            fields=[
                DocumentField("numero_guia", "Número de Guía", "text", True,
                            extraction_patterns=[r"GV-ENT-ORD-\d{4}-\d{3}", r"Guía\s*N[°º]?\s*(\S+)"]),
                DocumentField("fecha_recepcion", "Fecha de Recepción", "date", True),
                DocumentField("origen_valija", "Origen de la Valija", "text", True),
                DocumentField("numero_valija", "Número de Valija", "text", True),
                DocumentField("peso_total", "Peso Total", "text", True),
                DocumentField("cantidad_documentos", "Cantidad de Documentos", "number", True),
                DocumentField("transportista", "Empresa Transportista", "text", True),
                DocumentField("numero_guia_aerea", "Número de Guía Aérea", "text", False),
                DocumentField("estado_valija", "Estado de la Valija", "select", True,
                            possible_values=["ÍNTEGRA", "DAÑADA", "VIOLADA"]),
                DocumentField("observaciones", "Observaciones", "multiline", False)
            ],
            azure_model_requirements={
                "min_confidence": 0.9,
                "model_type": "custom",
                "training_samples": 40
            }
        )

        # Guía de Valija Salida Extraordinaria
        templates[DocumentSubtype.GUIA_SALIDA_EXT] = DocumentTemplate(
            document_type=DocumentSubtype.GUIA_SALIDA_EXT,
            display_name="Guía de Valija - Salida Extraordinaria",
            description="Guía para valija diplomática de salida en envío extraordinario",
            security_level=SecurityClassification.SECRETO,
            complexity=ProcessingComplexity.COMPLEX,
            fields=[
                DocumentField("numero_guia", "Número de Guía", "text", True,
                            extraction_patterns=[r"GV-SAL-EXT-\d{4}-\d{3}", r"EXTRAORDINARIA\s*(\S+)"]),
                DocumentField("destino_valija", "Destino de la Valija", "text", True),
                DocumentField("justificacion_extraordinaria", "Justificación Extraordinaria", "multiline", True),
                DocumentField("autorizacion_superior", "Autorización Superior", "text", True),
                DocumentField("nivel_urgencia", "Nivel de Urgencia", "select", True,
                            possible_values=["CRÍTICA", "ALTA", "MEDIA"]),
                DocumentField("tiempo_estimado_entrega", "Tiempo Estimado de Entrega", "text", True),
                DocumentField("medidas_seguridad_especiales", "Medidas de Seguridad Especiales", "multiline", False),
                DocumentField("contacto_emergencia", "Contacto de Emergencia", "text", True),
                DocumentField("instrucciones_especiales", "Instrucciones Especiales", "multiline", False)
            ],
            azure_model_requirements={
                "min_confidence": 0.75,
                "model_type": "custom",
                "training_samples": 150
            }
        )

        return templates

    def _initialize_conversation_patterns(self) -> Dict[str, List[str]]:
        """Inicializa patrones de conversación para análisis"""
        return {
            "document_type_identification": [
                r"necesito\s+procesar\s+(.+?)(?:\s+de\s+(.+?))?",
                r"trabajar\s+con\s+(.+?)(?:\s+del?\s+(.+?))?",
                r"documentos?\s+(?:de\s+)?(.+?)(?:\s+para\s+(.+?))?",
                r"hojas?\s+de\s+remisión\s+(.+)",
                r"guías?\s+de\s+valija\s+(.+)",
                r"(?:tipo|clase)\s+(.+?)\s+documentos?"
            ],
            "security_level_identification": [
                r"clasificación\s+(.+?)(?:\s|$)",
                r"nivel\s+(?:de\s+)?seguridad\s+(.+?)(?:\s|$)",
                r"(?:público|reservado|confidencial|secreto|ultra.?secreto)",
                r"uso\s+oficial",
                r"acceso\s+(?:restringido|limitado|controlado)"
            ],
            "functional_requirements": [
                r"debe\s+(?:poder\s+)?(.+?)(?:\s+y\s+|\s*$)",
                r"necesita\s+(.+?)(?:\s+para\s+|\s*$)",
                r"requiere\s+(.+?)(?:\s+que\s+|\s*$)",
                r"tiene\s+que\s+(.+?)(?:\s+cuando\s+|\s*$)",
                r"(?:funcionalidad|característica|capacidad)\s+(?:de\s+)?(.+)"
            ],
            "technical_requirements": [
                r"azure\s+form\s+recognizer",
                r"base\s+de\s+datos\s+(.+)",
                r"api\s+(?:rest|restful)",
                r"interfaz\s+(?:de\s+)?usuario",
                r"autenticación\s+(.+)",
                r"(?:postgresql|sql\s+server|mysql)"
            ]
        }

    async def _extract_conversation_info(self, conversation: str, context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Extrae información clave de la conversación"""
        info = {
            "document_types": [],
            "security_levels": [],
            "functional_requirements": [],
            "technical_requirements": [],
            "constraints": [],
            "stakeholders": [],
            "departments": [],
            "urgency": "medium"
        }

        conversation_lower = conversation.lower()

        # Identificar tipos de documentos
        for pattern in self.conversation_patterns["document_type_identification"]:
            matches = re.findall(pattern, conversation_lower)
            for match in matches:
                if isinstance(match, tuple):
                    info["document_types"].extend([m.strip() for m in match if m.strip()])
                else:
                    info["document_types"].append(match.strip())

        # Identificar niveles de seguridad
        for pattern in self.conversation_patterns["security_level_identification"]:
            matches = re.findall(pattern, conversation_lower)
            info["security_levels"].extend(matches)

        # Identificar requerimientos funcionales
        for pattern in self.conversation_patterns["functional_requirements"]:
            matches = re.findall(pattern, conversation_lower)
            info["functional_requirements"].extend(matches)

        # Identificar requerimientos técnicos
        for pattern in self.conversation_patterns["technical_requirements"]:
            if re.search(pattern, conversation_lower):
                info["technical_requirements"].append(pattern.replace(r'\s+', ' '))

        # Identificar departamentos
        departments = [
            "oga", "pco", "pru", "pmu", "eco", "con", "cul", "tec",
            "gestión administrativa", "protocolo", "relaciones exteriores",
            "asuntos económicos", "consulares", "culturales", "cooperación técnica"
        ]

        for dept in departments:
            if dept in conversation_lower:
                info["departments"].append(dept)

        # Identificar urgencia
        if any(word in conversation_lower for word in ["urgente", "prioritario", "inmediato", "crítico"]):
            info["urgency"] = "high"
        elif any(word in conversation_lower for word in ["cuando sea posible", "no urgente", "rutina"]):
            info["urgency"] = "low"

        return info

    async def _identify_document_types(self, extracted_info: Dict[str, Any]) -> List[DocumentSubtype]:
        """Identifica tipos específicos de documentos basados en información extraída"""
        identified_types = []

        doc_type_mapping = {
            "oga": DocumentSubtype.HOJA_OGA,
            "pco": DocumentSubtype.HOJA_PCO,
            "pru": DocumentSubtype.HOJA_PRU,
            "pmu": DocumentSubtype.HOJA_PMU,
            "eco": DocumentSubtype.HOJA_ECO,
            "con": DocumentSubtype.HOJA_CON,
            "cul": DocumentSubtype.HOJA_CUL,
            "tec": DocumentSubtype.HOJA_TEC,
            "valija entrada ordinaria": DocumentSubtype.GUIA_ENTRADA_ORD,
            "valija entrada extraordinaria": DocumentSubtype.GUIA_ENTRADA_EXT,
            "valija salida ordinaria": DocumentSubtype.GUIA_SALIDA_ORD,
            "valija salida extraordinaria": DocumentSubtype.GUIA_SALIDA_EXT,
            "nota verbal": DocumentSubtype.NOTA_VERBAL,
            "aide memoire": DocumentSubtype.AIDE_MEMOIRE
        }

        # Buscar coincidencias directas
        for doc_text in extracted_info["document_types"]:
            for key, doc_type in doc_type_mapping.items():
                if key in doc_text.lower():
                    if doc_type not in identified_types:
                        identified_types.append(doc_type)

        # Inferir tipos basado en departamentos
        for dept in extracted_info["departments"]:
            if dept == "oga" and DocumentSubtype.HOJA_OGA not in identified_types:
                identified_types.append(DocumentSubtype.HOJA_OGA)
            elif dept == "pco" and DocumentSubtype.HOJA_PCO not in identified_types:
                identified_types.append(DocumentSubtype.HOJA_PCO)
            # ... más mapeos según sea necesario

        # Si no se identifica ningún tipo específico, usar genéricos
        if not identified_types:
            if any("hoja" in dt for dt in extracted_info["document_types"]):
                identified_types.append(DocumentSubtype.HOJA_OGA)  # Por defecto
            elif any("valija" in dt for dt in extracted_info["document_types"]):
                identified_types.append(DocumentSubtype.GUIA_ENTRADA_ORD)  # Por defecto

        return identified_types

    async def _generate_technical_specification(self, extracted_info: Dict[str, Any],
                                              document_types: List[DocumentSubtype]) -> TechnicalSpecification:
        """Genera especificación técnica completa"""
        spec_id = f"spec_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"

        spec = TechnicalSpecification(
            id=spec_id,
            title=f"Especificación Técnica - {', '.join([dt.value for dt in document_types])}",
            description="Especificación técnica generada automáticamente basada en análisis de requerimientos",
            document_types=document_types
        )

        # Generar configuración de Azure
        spec.azure_config = await self.generate_azure_form_recognizer_config(document_types)

        # Generar esquema de base de datos
        spec.database_schema = await self.generate_database_schema(document_types)

        # Generar especificación de API
        api_spec = await self.generate_api_specification(document_types)
        spec.api_endpoints = api_spec.get("paths", {})

        # Generar requerimientos de seguridad
        spec.security_requirements = await self._generate_security_requirements_from_info(extracted_info)

        # Generar componentes de UI
        spec.ui_components = await self._generate_ui_components(document_types)

        # Generar requerimientos de rendimiento
        spec.performance_requirements = await self._generate_performance_requirements(document_types)

        # Generar documentación técnica
        spec.technical_documentation = await self._generate_technical_documentation(spec, extracted_info)

        return spec

    async def _validate_and_refine_specification(self, spec: TechnicalSpecification) -> None:
        """Valida y refina la especificación generada"""
        # Validar completitud
        if not spec.document_types:
            spec.implementation_notes.append("ADVERTENCIA: No se identificaron tipos de documentos específicos")

        # Validar consistencia de seguridad
        max_security_level = SecurityClassification.PUBLICO
        for doc_type in spec.document_types:
            template = self.document_templates.get(doc_type)
            if template and template.security_level.value > max_security_level.value:
                max_security_level = template.security_level

        if max_security_level != SecurityClassification.PUBLICO:
            spec.implementation_notes.append(
                f"Nivel de seguridad máximo requerido: {max_security_level.value}"
            )

        # Validar complejidad
        max_complexity = ProcessingComplexity.SIMPLE
        for doc_type in spec.document_types:
            template = self.document_templates.get(doc_type)
            if template and template.complexity.value > max_complexity.value:
                max_complexity = template.complexity

        if max_complexity in [ProcessingComplexity.COMPLEX, ProcessingComplexity.EXPERT]:
            spec.implementation_notes.append(
                f"Complejidad de procesamiento: {max_complexity.value} - Considerar recursos adicionales"
            )

    async def _generate_database_requirements(self, template: DocumentTemplate) -> Dict[str, Any]:
        """Genera requerimientos específicos de base de datos para una plantilla"""
        return {
            "table_name": f"doc_{template.document_type.value}",
            "security_level": template.security_level.value,
            "audit_required": template.security_level != SecurityClassification.PUBLICO,
            "encryption_required": template.security_level in [SecurityClassification.SECRETO, SecurityClassification.ULTRA_SECRETO],
            "backup_frequency": "daily" if template.security_level != SecurityClassification.PUBLICO else "weekly"
        }

    async def _generate_api_requirements(self, template: DocumentTemplate) -> Dict[str, Any]:
        """Genera requerimientos de API para una plantilla"""
        return {
            "authentication_required": True,
            "authorization_level": template.security_level.value,
            "rate_limiting": True,
            "audit_logging": template.security_level != SecurityClassification.PUBLICO,
            "field_validation": [field.name for field in template.fields if field.required]
        }

    async def _generate_security_requirements(self, template: DocumentTemplate) -> Dict[str, Any]:
        """Genera requerimientos de seguridad para una plantilla"""
        return {
            "classification_level": template.security_level.value,
            "access_control": "rbac",
            "encryption_at_rest": template.security_level in [SecurityClassification.CONFIDENCIAL, SecurityClassification.SECRETO, SecurityClassification.ULTRA_SECRETO],
            "encryption_in_transit": True,
            "audit_trail": template.security_level != SecurityClassification.PUBLICO,
            "data_retention_years": 7 if template.security_level != SecurityClassification.PUBLICO else 3
        }

    async def _generate_ui_requirements(self, template: DocumentTemplate) -> Dict[str, Any]:
        """Genera requerimientos de UI para una plantilla"""
        return {
            "form_fields": len(template.fields),
            "validation_real_time": True,
            "security_indicators": template.security_level != SecurityClassification.PUBLICO,
            "responsive_design": True,
            "accessibility_compliant": True
        }

    def _get_expected_accuracy(self, complexity: ProcessingComplexity) -> float:
        """Obtiene precisión esperada basada en complejidad"""
        mapping = {
            ProcessingComplexity.SIMPLE: 0.95,
            ProcessingComplexity.MEDIUM: 0.90,
            ProcessingComplexity.COMPLEX: 0.85,
            ProcessingComplexity.EXPERT: 0.80
        }
        return mapping.get(complexity, 0.85)

    def _get_minimum_samples(self, complexity: ProcessingComplexity) -> int:
        """Obtiene número mínimo de muestras para entrenamiento"""
        mapping = {
            ProcessingComplexity.SIMPLE: 30,
            ProcessingComplexity.MEDIUM: 50,
            ProcessingComplexity.COMPLEX: 100,
            ProcessingComplexity.EXPERT: 200
        }
        return mapping.get(complexity, 50)

    def _get_recommended_samples(self, complexity: ProcessingComplexity) -> int:
        """Obtiene número recomendado de muestras para entrenamiento"""
        return self._get_minimum_samples(complexity) * 2

    def _get_sample_diversity_requirements(self, template: DocumentTemplate) -> Dict[str, Any]:
        """Obtiene requerimientos de diversidad de muestras"""
        return {
            "different_formats": ["pdf", "doc", "docx", "scanned"],
            "quality_variations": ["high", "medium", "low"],
            "layout_variations": template.complexity != ProcessingComplexity.SIMPLE,
            "handwriting_samples": template.complexity == ProcessingComplexity.EXPERT
        }

    def _get_sql_type(self, field_type: str) -> str:
        """Convierte tipo de campo a tipo SQL"""
        mapping = {
            "text": "VARCHAR(255)",
            "multiline": "TEXT",
            "date": "DATE",
            "number": "INTEGER",
            "select": "VARCHAR(50)"
        }
        return mapping.get(field_type, "TEXT")

    def _get_openapi_type(self, field_type: str) -> str:
        """Convierte tipo de campo a tipo OpenAPI"""
        mapping = {
            "text": "string",
            "multiline": "string",
            "date": "string",
            "number": "integer",
            "select": "string"
        }
        return mapping.get(field_type, "string")

    async def _generate_security_requirements_from_info(self, extracted_info: Dict[str, Any]) -> Dict[str, Any]:
        """Genera requerimientos de seguridad basados en información extraída"""
        max_security = SecurityClassification.USO_OFICIAL

        for level_text in extracted_info["security_levels"]:
            if "secreto" in level_text:
                max_security = SecurityClassification.SECRETO
            elif "confidencial" in level_text:
                max_security = SecurityClassification.CONFIDENCIAL
            elif "reservado" in level_text:
                max_security = SecurityClassification.RESERVADO

        return {
            "required_clearance": max_security.value,
            "multi_factor_auth": max_security in [SecurityClassification.SECRETO, SecurityClassification.ULTRA_SECRETO],
            "session_timeout_minutes": 30 if max_security != SecurityClassification.PUBLICO else 60,
            "audit_all_access": max_security != SecurityClassification.PUBLICO
        }

    async def _generate_ui_components(self, document_types: List[DocumentSubtype]) -> List[Dict[str, Any]]:
        """Genera especificaciones de componentes UI"""
        components = []

        for doc_type in document_types:
            template = self.document_templates.get(doc_type)
            if not template:
                continue

            component = {
                "name": f"{doc_type.value.replace('_', '')}Form",
                "type": "form",
                "fields": [],
                "validation": True,
                "security_indicators": template.security_level != SecurityClassification.PUBLICO
            }

            for field in template.fields:
                ui_field = {
                    "name": field.name,
                    "label": field.display_name,
                    "type": field.field_type,
                    "required": field.required,
                    "validation_rules": field.validation_rules
                }

                if field.possible_values:
                    ui_field["options"] = field.possible_values

                component["fields"].append(ui_field)

            components.append(component)

        return components

    async def _generate_performance_requirements(self, document_types: List[DocumentSubtype]) -> Dict[str, Any]:
        """Genera requerimientos de rendimiento"""
        return {
            "document_processing_time_seconds": 30,
            "form_recognizer_timeout_seconds": 120,
            "api_response_time_ms": 500,
            "concurrent_users": 100,
            "documents_per_hour": 1000,
            "availability_percentage": 99.5,
            "backup_window_hours": 4
        }

    async def _generate_technical_documentation(self, spec: TechnicalSpecification,
                                              extracted_info: Dict[str, Any]) -> str:
        """Genera documentación técnica detallada"""
        doc = f"""
# Especificación Técnica: {spec.title}

## Resumen Ejecutivo

Esta especificación define los requerimientos técnicos para el procesamiento de documentos diplomáticos específicos identificados en el análisis de requerimientos.

**Tipos de Documentos:** {', '.join([dt.value for dt in spec.document_types])}

**Fecha de Generación:** {spec.created_at.strftime('%Y-%m-%d %H:%M:%S')}

## Requerimientos Funcionales

### Procesamiento de Documentos
- Extracción automática de datos usando Azure Form Recognizer
- Validación de campos requeridos
- Clasificación automática de documentos
- Generación de metadatos

### Seguridad
- Control de acceso basado en clasificación de seguridad
- Auditoría completa de acciones
- Encriptación de datos sensibles
- Autenticación multi-factor para documentos clasificados

## Arquitectura Técnica

### Azure Form Recognizer
- Modelos personalizados por tipo de documento
- Confianza mínima: 75-90% según complejidad
- Procesamiento en tiempo real

### Base de Datos
- PostgreSQL con esquemas específicos por documento
- Auditoría automática para documentos clasificados
- Backup diario para información sensible

### API
- RESTful API con OpenAPI 3.0
- Autenticación JWT
- Rate limiting y validación

### Frontend
- Componentes React especializados
- Validación en tiempo real
- Indicadores de seguridad

## Consideraciones de Implementación

{chr(10).join(f'- {note}' for note in spec.implementation_notes)}

## Cronograma Estimado

1. **Fase 1 (Semanas 1-2):** Configuración de Azure Form Recognizer
2. **Fase 2 (Semanas 3-4):** Desarrollo de esquemas de base de datos
3. **Fase 3 (Semanas 5-6):** Implementación de API
4. **Fase 4 (Semanas 7-8):** Desarrollo de componentes UI
5. **Fase 5 (Semanas 9-10):** Testing y validación

## Recursos Requeridos

- Desarrollador Azure especializado (40 horas)
- Desarrollador Backend (60 horas)
- Desarrollador Frontend (50 horas)
- Especialista en seguridad (20 horas)
- Testing y QA (30 horas)

Total estimado: 200 horas de desarrollo
"""
        return doc.strip()


# Función principal para testing
async def main():
    """Función principal para testing del agente"""
    logging.basicConfig(level=logging.INFO)

    agent = RequirementsAnalyzerAgent()

    # Ejemplo de conversación para análisis
    conversation = """
    Necesito procesar hojas de remisión de la OGA y también guías de valija
    de entrada ordinaria. Los documentos tienen clasificación de uso oficial
    y reservado. Debe integrar con Azure Form Recognizer para extracción
    automática y usar una base de datos PostgreSQL. La interfaz debe ser
    en Next.js con autenticación por niveles.
    """

    print("Analizando requerimientos desde conversación...")
    spec = await agent.analyze_requirements_from_conversation(conversation)

    print(f"\nEspecificación generada: {spec.id}")
    print(f"Tipos de documentos: {[dt.value for dt in spec.document_types]}")
    print(f"Configuración Azure: {len(spec.azure_config.get('models', {})) > 0}")
    print(f"Esquemas DB: {len(spec.database_schema.get('tables', {}))}")

    # Análisis específico de tipo de documento
    print("\nAnalizando requerimientos específicos para Hoja OGA...")
    requirements = await agent.analyze_document_type_requirements(DocumentSubtype.HOJA_OGA)
    print(f"Campos requeridos: {len(requirements['field_requirements'])}")

    # Estadísticas del agente
    stats = await agent.get_agent_statistics()
    print(f"\nEstadísticas del agente: {stats}")


if __name__ == "__main__":
    asyncio.run(main())
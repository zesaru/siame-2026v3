#!/usr/bin/env python3
"""
SIAME 2026v3 - Document Classifier Agent
Agente especializado en clasificación automática de documentos diplomáticos

Este agente implementa:
- Detección automática de tipos de documentos diplomáticos
- Análisis de contenido y estructura
- Extracción de metadatos clave
- Clasificación basada en patrones y características específicas
"""

import asyncio
import logging
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum

# Importaciones para procesamiento de texto
import hashlib
import mimetypes


class DocumentConfidence(Enum):
    """Niveles de confianza en la clasificación"""
    VERY_HIGH = 0.9
    HIGH = 0.8
    MEDIUM = 0.6
    LOW = 0.4
    VERY_LOW = 0.2


@dataclass
class ClassificationFeature:
    """Característica utilizada para clasificación"""
    name: str
    weight: float
    value: Any
    confidence: float


@dataclass
class DocumentMetadata:
    """Metadatos extraídos del documento"""
    title: Optional[str] = None
    authors: List[str] = field(default_factory=list)
    date: Optional[datetime] = None
    language: Optional[str] = None
    countries_involved: List[str] = field(default_factory=list)
    organizations: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    document_format: Optional[str] = None
    page_count: Optional[int] = None
    word_count: Optional[int] = None


@dataclass
class ClassificationResult:
    """Resultado de la clasificación de un documento"""
    document_path: str
    detected_type: str
    confidence_score: float
    alternative_types: List[Tuple[str, float]] = field(default_factory=list)
    features_used: List[ClassificationFeature] = field(default_factory=list)
    metadata: DocumentMetadata = field(default_factory=DocumentMetadata)
    processing_time: float = 0.0
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


class DocumentClassifierAgent:
    """Agente clasificador de documentos diplomáticos"""

    def __init__(self, agent_id: str = None):
        self.agent_id = agent_id or f"doc_classifier_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.logger = logging.getLogger(__name__)

        # Patrones de clasificación para diferentes tipos de documentos
        self.classification_patterns = self._initialize_classification_patterns()

        # Palabras clave por tipo de documento
        self.document_keywords = self._initialize_document_keywords()

        # Configuración
        self.min_confidence_threshold = 0.4
        self.max_alternatives = 3

        # Estadísticas
        self.classification_stats = {
            "documents_processed": 0,
            "successful_classifications": 0,
            "average_confidence": 0.0,
            "processing_time_total": 0.0
        }

    async def classify_document(self, document_path: Path) -> ClassificationResult:
        """Clasifica un documento diplomático"""
        start_time = datetime.now()

        try:
            self.logger.info(f"Iniciando clasificación de documento: {document_path}")

            # Validar que el archivo existe
            if not document_path.exists():
                raise FileNotFoundError(f"Documento no encontrado: {document_path}")

            # Crear resultado inicial
            result = ClassificationResult(
                document_path=str(document_path),
                detected_type="UNKNOWN",
                confidence_score=0.0
            )

            # Extraer contenido del documento
            content = await self._extract_document_content(document_path)
            if not content:
                result.errors.append("No se pudo extraer contenido del documento")
                return result

            # Extraer metadatos
            result.metadata = await self._extract_metadata(document_path, content)

            # Realizar clasificación
            classification_features = await self._analyze_document_features(content, result.metadata)
            result.features_used = classification_features

            # Calcular puntuaciones para cada tipo de documento
            type_scores = await self._calculate_type_scores(classification_features)

            # Determinar tipo principal y alternativas
            if type_scores:
                # Ordenar por puntuación
                sorted_scores = sorted(type_scores.items(), key=lambda x: x[1], reverse=True)

                # Tipo principal
                result.detected_type = sorted_scores[0][0]
                result.confidence_score = sorted_scores[0][1]

                # Tipos alternativos
                for doc_type, score in sorted_scores[1:self.max_alternatives + 1]:
                    if score >= self.min_confidence_threshold:
                        result.alternative_types.append((doc_type, score))

            # Validar resultado
            await self._validate_classification_result(result)

            # Actualizar estadísticas
            processing_time = (datetime.now() - start_time).total_seconds()
            result.processing_time = processing_time
            await self._update_statistics(result)

            self.logger.info(
                f"Documento clasificado como {result.detected_type} "
                f"(confianza: {result.confidence_score:.2f})"
            )

            return result

        except Exception as e:
            self.logger.error(f"Error clasificando documento {document_path}: {e}")

            result = ClassificationResult(
                document_path=str(document_path),
                detected_type="UNKNOWN",
                confidence_score=0.0,
                processing_time=(datetime.now() - start_time).total_seconds()
            )
            result.errors.append(str(e))
            return result

    async def batch_classify(self, document_paths: List[Path]) -> List[ClassificationResult]:
        """Clasifica múltiples documentos en lote"""
        self.logger.info(f"Iniciando clasificación de lote: {len(document_paths)} documentos")

        results = []
        for doc_path in document_paths:
            result = await self.classify_document(doc_path)
            results.append(result)

        self.logger.info(f"Clasificación de lote completada: {len(results)} resultados")
        return results

    async def get_classification_statistics(self) -> Dict[str, Any]:
        """Obtiene estadísticas del clasificador"""
        return {
            "agent_id": self.agent_id,
            "statistics": self.classification_stats.copy(),
            "configuration": {
                "min_confidence_threshold": self.min_confidence_threshold,
                "max_alternatives": self.max_alternatives,
                "supported_types": list(self.document_keywords.keys())
            }
        }

    # Métodos privados

    def _initialize_classification_patterns(self) -> Dict[str, List[str]]:
        """Inicializa patrones regex para clasificación"""
        return {
            "TREATY": [
                r"tratado\s+(?:de|entre|sobre)",
                r"treaty\s+(?:of|between|on)",
                r"convenio\s+internacional",
                r"international\s+convention",
                r"acuerdo\s+marco",
                r"framework\s+agreement"
            ],
            "AGREEMENT": [
                r"acuerdo\s+(?:de|entre|sobre)",
                r"agreement\s+(?:of|between|on)",
                r"memorando\s+de\s+(?:entendimiento|cooperación)",
                r"memorandum\s+of\s+(?:understanding|cooperation)",
                r"protocolo\s+de\s+cooperación",
                r"cooperation\s+protocol"
            ],
            "DIPLOMATIC_NOTE": [
                r"nota\s+diplomática",
                r"diplomatic\s+note",
                r"nota\s+verbal",
                r"verbal\s+note",
                r"aide[-\s]memoire",
                r"comunicación\s+oficial"
            ],
            "TRADE_AGREEMENT": [
                r"acuerdo\s+comercial",
                r"trade\s+agreement",
                r"tratado\s+de\s+libre\s+comercio",
                r"free\s+trade\s+agreement",
                r"acuerdo\s+económico",
                r"economic\s+agreement",
                r"partnership\s+agreement"
            ],
            "SECURITY_PACT": [
                r"pacto\s+de\s+seguridad",
                r"security\s+pact",
                r"acuerdo\s+de\s+defensa",
                r"defense\s+agreement",
                r"alianza\s+militar",
                r"military\s+alliance",
                r"tratado\s+de\s+no\s+agresión",
                r"non[-\s]aggression\s+pact"
            ],
            "PROTOCOL": [
                r"protocolo\s+(?:adicional|anexo)",
                r"additional\s+protocol",
                r"protocolo\s+de\s+enmienda",
                r"amendment\s+protocol",
                r"protocolo\s+facultativo",
                r"optional\s+protocol"
            ],
            "MULTILATERAL_TREATY": [
                r"tratado\s+multilateral",
                r"multilateral\s+treaty",
                r"convención\s+internacional",
                r"international\s+convention",
                r"carta\s+(?:de|constitutiva)",
                r"charter\s+of"
            ]
        }

    def _initialize_document_keywords(self) -> Dict[str, List[str]]:
        """Inicializa palabras clave por tipo de documento"""
        return {
            "TREATY": [
                "ratificación", "ratification", "depositario", "depositary",
                "entrada en vigor", "entry into force", "denuncia", "denunciation",
                "adhesión", "accession", "reservas", "reservations"
            ],
            "AGREEMENT": [
                "cooperación", "cooperation", "colaboración", "collaboration",
                "intercambio", "exchange", "asistencia", "assistance",
                "implementación", "implementation"
            ],
            "DIPLOMATIC_NOTE": [
                "embajada", "embassy", "consulado", "consulate",
                "cancillería", "foreign ministry", "relaciones exteriores",
                "foreign affairs", "excelencia", "excellency"
            ],
            "TRADE_AGREEMENT": [
                "comercio", "trade", "aranceles", "tariffs", "exportación", "export",
                "importación", "import", "inversión", "investment",
                "mercancías", "goods", "servicios", "services"
            ],
            "SECURITY_PACT": [
                "defensa", "defense", "seguridad", "security", "militar", "military",
                "fuerzas armadas", "armed forces", "amenaza", "threat",
                "agresión", "aggression", "disuasión", "deterrence"
            ],
            "PROTOCOL": [
                "modificación", "modification", "enmienda", "amendment",
                "actualización", "update", "revisión", "revision",
                "suplemento", "supplement"
            ],
            "MULTILATERAL_TREATY": [
                "estados partes", "states parties", "organización", "organization",
                "naciones unidas", "united nations", "regional", "regional",
                "internacional", "international"
            ]
        }

    async def _extract_document_content(self, document_path: Path) -> Optional[str]:
        """Extrae el contenido textual del documento"""
        try:
            # Detectar tipo MIME
            mime_type, _ = mimetypes.guess_type(str(document_path))

            if mime_type == "text/plain" or document_path.suffix.lower() == ".txt":
                with open(document_path, 'r', encoding='utf-8', errors='ignore') as f:
                    return f.read()

            elif mime_type == "application/pdf" or document_path.suffix.lower() == ".pdf":
                # TODO: Implementar extracción de PDF
                self.logger.warning(f"Extracción de PDF no implementada para {document_path}")
                return None

            elif document_path.suffix.lower() in [".doc", ".docx"]:
                # TODO: Implementar extracción de Word
                self.logger.warning(f"Extracción de Word no implementada para {document_path}")
                return None

            else:
                # Intentar como texto plano
                with open(document_path, 'r', encoding='utf-8', errors='ignore') as f:
                    return f.read()

        except Exception as e:
            self.logger.error(f"Error extrayendo contenido de {document_path}: {e}")
            return None

    async def _extract_metadata(self, document_path: Path, content: str) -> DocumentMetadata:
        """Extrae metadatos del documento"""
        metadata = DocumentMetadata()

        try:
            # Información del archivo
            metadata.document_format = document_path.suffix.lower()

            if content:
                # Conteo de palabras aproximado
                metadata.word_count = len(content.split())

                # Detectar idioma (básico)
                metadata.language = await self._detect_language(content)

                # Extraer título (primera línea significativa)
                lines = content.split('\n')
                for line in lines:
                    if line.strip() and len(line.strip()) > 10:
                        metadata.title = line.strip()[:200]  # Limitar longitud
                        break

                # Extraer países mencionados
                metadata.countries_involved = await self._extract_countries(content)

                # Extraer organizaciones
                metadata.organizations = await self._extract_organizations(content)

                # Extraer fechas
                metadata.date = await self._extract_dates(content)

                # Extraer palabras clave
                metadata.keywords = await self._extract_keywords(content)

        except Exception as e:
            self.logger.error(f"Error extrayendo metadatos: {e}")

        return metadata

    async def _analyze_document_features(self, content: str, metadata: DocumentMetadata) -> List[ClassificationFeature]:
        """Analiza características del documento para clasificación"""
        features = []

        # Características basadas en patrones
        for doc_type, patterns in self.classification_patterns.items():
            pattern_matches = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, content, re.IGNORECASE))
                pattern_matches += matches

            if pattern_matches > 0:
                confidence = min(pattern_matches / 10.0, 1.0)  # Normalizar
                features.append(ClassificationFeature(
                    name=f"pattern_match_{doc_type.lower()}",
                    weight=0.4,
                    value=pattern_matches,
                    confidence=confidence
                ))

        # Características basadas en palabras clave
        for doc_type, keywords in self.document_keywords.items():
            keyword_score = 0
            content_lower = content.lower()

            for keyword in keywords:
                if keyword.lower() in content_lower:
                    keyword_score += 1

            if keyword_score > 0:
                confidence = min(keyword_score / len(keywords), 1.0)
                features.append(ClassificationFeature(
                    name=f"keyword_score_{doc_type.lower()}",
                    weight=0.3,
                    value=keyword_score,
                    confidence=confidence
                ))

        # Características estructurales
        if metadata.word_count:
            # Longitud del documento
            if metadata.word_count < 500:
                doc_length_type = "short"
            elif metadata.word_count < 2000:
                doc_length_type = "medium"
            else:
                doc_length_type = "long"

            features.append(ClassificationFeature(
                name="document_length",
                weight=0.1,
                value=doc_length_type,
                confidence=0.7
            ))

        # Características de contenido
        if metadata.countries_involved:
            if len(metadata.countries_involved) > 2:
                features.append(ClassificationFeature(
                    name="multilateral_indicator",
                    weight=0.2,
                    value=len(metadata.countries_involved),
                    confidence=0.8
                ))

        return features

    async def _calculate_type_scores(self, features: List[ClassificationFeature]) -> Dict[str, float]:
        """Calcula puntuaciones para cada tipo de documento"""
        type_scores = {}

        # Inicializar puntuaciones
        for doc_type in self.document_keywords.keys():
            type_scores[doc_type] = 0.0

        # Procesar características
        for feature in features:
            # Extraer tipo de documento de la característica
            if "pattern_match_" in feature.name:
                doc_type = feature.name.replace("pattern_match_", "").upper()
                if doc_type in type_scores:
                    type_scores[doc_type] += feature.weight * feature.confidence

            elif "keyword_score_" in feature.name:
                doc_type = feature.name.replace("keyword_score_", "").upper()
                if doc_type in type_scores:
                    type_scores[doc_type] += feature.weight * feature.confidence

            # Características especiales
            elif feature.name == "multilateral_indicator":
                type_scores["MULTILATERAL_TREATY"] += feature.weight * feature.confidence
                type_scores["TRADE_AGREEMENT"] += feature.weight * feature.confidence * 0.5

        # Normalizar puntuaciones
        max_possible_score = 1.0  # Ajustar según sea necesario
        for doc_type in type_scores:
            type_scores[doc_type] = min(type_scores[doc_type], max_possible_score)

        return type_scores

    async def _detect_language(self, content: str) -> Optional[str]:
        """Detecta el idioma del documento (implementación básica)"""
        spanish_indicators = ["de", "la", "el", "en", "con", "por", "para", "que", "del", "las"]
        english_indicators = ["the", "of", "and", "to", "in", "for", "with", "that", "this", "from"]

        content_words = content.lower().split()[:100]  # Primeras 100 palabras

        spanish_count = sum(1 for word in content_words if word in spanish_indicators)
        english_count = sum(1 for word in content_words if word in english_indicators)

        if spanish_count > english_count:
            return "es"
        elif english_count > spanish_count:
            return "en"
        else:
            return None

    async def _extract_countries(self, content: str) -> List[str]:
        """Extrae nombres de países mencionados en el documento"""
        # Lista básica de países (debería expandirse)
        countries = [
            "Argentina", "Brasil", "Chile", "Colombia", "Perú", "Venezuela",
            "México", "Estados Unidos", "Canadá", "España", "Francia", "Reino Unido",
            "Alemania", "Italia", "Rusia", "China", "Japón", "India"
        ]

        found_countries = []
        content_lower = content.lower()

        for country in countries:
            if country.lower() in content_lower:
                found_countries.append(country)

        return found_countries

    async def _extract_organizations(self, content: str) -> List[str]:
        """Extrae nombres de organizaciones mencionadas"""
        organizations = [
            "Naciones Unidas", "United Nations", "ONU", "UN",
            "OEA", "OAS", "Unión Europea", "European Union",
            "MERCOSUR", "UNASUR", "CELAC", "OTAN", "NATO"
        ]

        found_orgs = []
        content_lower = content.lower()

        for org in organizations:
            if org.lower() in content_lower:
                found_orgs.append(org)

        return found_orgs

    async def _extract_dates(self, content: str) -> Optional[datetime]:
        """Extrae fechas del documento"""
        # Patrones básicos de fechas
        date_patterns = [
            r"\d{1,2}/\d{1,2}/\d{4}",
            r"\d{1,2}-\d{1,2}-\d{4}",
            r"\d{4}-\d{1,2}-\d{1,2}",
            r"\d{1,2}\s+de\s+\w+\s+de\s+\d{4}"
        ]

        for pattern in date_patterns:
            matches = re.findall(pattern, content)
            if matches:
                # TODO: Implementar parsing más sofisticado
                return datetime.now()  # Placeholder

        return None

    async def _extract_keywords(self, content: str) -> List[str]:
        """Extrae palabras clave relevantes del documento"""
        # Implementación básica - debería mejorarse con técnicas de NLP
        words = re.findall(r'\b\w{4,}\b', content.lower())

        # Filtrar palabras comunes
        stop_words = {
            "que", "para", "con", "por", "una", "este", "esta", "como",
            "the", "and", "for", "with", "this", "that", "from", "have"
        }

        keywords = [word for word in words if word not in stop_words]

        # Contar frecuencias y retornar las más comunes
        from collections import Counter
        word_counts = Counter(keywords)
        return [word for word, count in word_counts.most_common(10) if count > 1]

    async def _validate_classification_result(self, result: ClassificationResult) -> None:
        """Valida el resultado de clasificación"""
        if result.confidence_score < self.min_confidence_threshold:
            result.warnings.append(
                f"Confianza baja ({result.confidence_score:.2f}) - "
                f"clasificación puede no ser confiable"
            )

        if not result.features_used:
            result.warnings.append("No se encontraron características distintivas")

        if result.detected_type == "UNKNOWN":
            result.warnings.append("No se pudo determinar el tipo de documento")

    async def _update_statistics(self, result: ClassificationResult) -> None:
        """Actualiza estadísticas del clasificador"""
        self.classification_stats["documents_processed"] += 1
        self.classification_stats["processing_time_total"] += result.processing_time

        if result.confidence_score >= self.min_confidence_threshold:
            self.classification_stats["successful_classifications"] += 1

        # Actualizar confianza promedio
        total_docs = self.classification_stats["documents_processed"]
        current_avg = self.classification_stats["average_confidence"]

        new_avg = ((current_avg * (total_docs - 1)) + result.confidence_score) / total_docs
        self.classification_stats["average_confidence"] = new_avg


# Función de utilidad para testing
async def main():
    """Función principal para testing del clasificador"""
    logging.basicConfig(level=logging.INFO)

    classifier = DocumentClassifierAgent()

    # Ejemplo de uso
    test_doc = Path("test_document.txt")
    if test_doc.exists():
        result = await classifier.classify_document(test_doc)
        print(f"Tipo detectado: {result.detected_type}")
        print(f"Confianza: {result.confidence_score:.2f}")
        print(f"Alternativas: {result.alternative_types}")


if __name__ == "__main__":
    asyncio.run(main())
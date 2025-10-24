#!/usr/bin/env python3
"""
SIAME 2026v3 - Azure Specialist Agent
Subagente experto en Azure para infraestructura diplomática

Este agente puede:
1. Configurar Azure Form Recognizer para documentos diplomáticos específicos
2. Implementar modelos personalizados para hojas de remisión y guías de valija
3. Configurar Blob Storage con niveles de seguridad diplomática
4. Integrar Key Vault para gestión segura de secretos
5. Generar código Python/TypeScript para integración completa con Azure
6. Automatizar despliegue de infraestructura con ARM/Bicep templates
"""

import asyncio
import logging
import json
import uuid
import base64
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum
import secrets
import string

# Importaciones de Azure (opcionales)
try:
    from azure.identity import DefaultAzureCredential, ClientSecretCredential
    from azure.mgmt.resource import ResourceManagementClient
    from azure.mgmt.storage import StorageManagementClient
    from azure.mgmt.cognitiveservices import CognitiveServicesManagementClient
    from azure.mgmt.keyvault import KeyVaultManagementClient
    from azure.storage.blob import BlobServiceClient
    from azure.keyvault.secrets import SecretClient
    from azure.ai.formrecognizer import DocumentModelAdministrationClient
    AZURE_SDK_AVAILABLE = True
except ImportError:
    AZURE_SDK_AVAILABLE = False


class AzureServiceType(Enum):
    """Tipos de servicios Azure soportados"""
    FORM_RECOGNIZER = "form_recognizer"
    BLOB_STORAGE = "blob_storage"
    KEY_VAULT = "key_vault"
    COGNITIVE_SERVICES = "cognitive_services"
    APP_SERVICE = "app_service"
    CONTAINER_REGISTRY = "container_registry"
    APPLICATION_INSIGHTS = "application_insights"


class SecurityTier(Enum):
    """Niveles de seguridad para configuración Azure"""
    PUBLIC = "public"
    RESTRICTED = "restricted"
    CONFIDENTIAL = "confidential"
    SECRET = "secret"
    TOP_SECRET = "top_secret"


class DiplomaticDocumentModel(Enum):
    """Modelos específicos para documentos diplomáticos"""
    HOJA_OGA = "siame-hoja-oga-v1"
    HOJA_PCO = "siame-hoja-pco-v1"
    HOJA_PRU = "siame-hoja-pru-v1"
    GUIA_ENTRADA_ORD = "siame-guia-entrada-ordinaria-v1"
    GUIA_ENTRADA_EXT = "siame-guia-entrada-extraordinaria-v1"
    GUIA_SALIDA_ORD = "siame-guia-salida-ordinaria-v1"
    GUIA_SALIDA_EXT = "siame-guia-salida-extraordinaria-v1"
    NOTA_DIPLOMATICA = "siame-nota-diplomatica-v1"


@dataclass
class AzureConfiguration:
    """Configuración completa de Azure para SIAME"""
    subscription_id: str
    tenant_id: str
    client_id: str
    client_secret: str
    resource_group: str
    location: str = "East US"
    environment: str = "development"  # development, staging, production


@dataclass
class FormRecognizerConfig:
    """Configuración de Azure Form Recognizer"""
    service_name: str
    sku: str = "S0"  # F0 (free), S0 (standard)
    endpoint: str = ""
    api_key: str = ""
    custom_models: Dict[str, str] = field(default_factory=dict)
    training_data_container: str = "training-data"


@dataclass
class BlobStorageConfig:
    """Configuración de Azure Blob Storage"""
    account_name: str
    account_key: str = ""
    connection_string: str = ""
    containers: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    security_settings: Dict[str, Any] = field(default_factory=dict)


@dataclass
class KeyVaultConfig:
    """Configuración de Azure Key Vault"""
    vault_name: str
    vault_url: str = ""
    access_policies: List[Dict[str, Any]] = field(default_factory=list)
    secrets: Dict[str, str] = field(default_factory=dict)


@dataclass
class AzureDeploymentResult:
    """Resultado de despliegue en Azure"""
    service_type: AzureServiceType
    resource_name: str
    endpoint: str
    success: bool
    error_message: Optional[str] = None
    configuration: Dict[str, Any] = field(default_factory=dict)
    generated_code: Optional[str] = None


class AzureSpecialistAgent:
    """Agente especialista en Azure para SIAME 2026v3"""

    def __init__(self, agent_id: str = None):
        self.agent_id = agent_id or f"azure_specialist_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.logger = logging.getLogger(__name__)

        # Configuración de Azure
        self.azure_config: Optional[AzureConfiguration] = None
        self.credentials = None

        # Clientes de Azure Management
        self.resource_client = None
        self.storage_client = None
        self.cognitive_client = None
        self.keyvault_client = None

        # Configuraciones de servicios
        self.form_recognizer_config: Optional[FormRecognizerConfig] = None
        self.blob_storage_config: Optional[BlobStorageConfig] = None
        self.key_vault_config: Optional[KeyVaultConfig] = None

        # Templates de infraestructura
        self.arm_templates = self._initialize_arm_templates()
        self.bicep_templates = self._initialize_bicep_templates()

        # Estadísticas del agente
        self.stats = {
            "services_deployed": 0,
            "models_trained": 0,
            "containers_created": 0,
            "secrets_stored": 0,
            "code_generated": 0
        }

    async def initialize(self, azure_config: AzureConfiguration) -> bool:
        """Inicializa el agente Azure con configuración"""
        try:
            self.logger.info("Inicializando Azure Specialist Agent...")

            if not AZURE_SDK_AVAILABLE:
                self.logger.error("Azure SDK no disponible")
                return False

            self.azure_config = azure_config

            # Configurar credenciales
            self.credentials = ClientSecretCredential(
                tenant_id=azure_config.tenant_id,
                client_id=azure_config.client_id,
                client_secret=azure_config.client_secret
            )

            # Inicializar clientes de management
            await self._initialize_management_clients()

            # Verificar conectividad
            await self._verify_azure_connectivity()

            self.logger.info("Azure Specialist Agent inicializado exitosamente")
            return True

        except Exception as e:
            self.logger.error(f"Error inicializando Azure Specialist: {e}")
            return False

    async def deploy_complete_azure_infrastructure(self, security_tier: SecurityTier = SecurityTier.CONFIDENTIAL) -> Dict[str, AzureDeploymentResult]:
        """Despliega infraestructura completa de Azure para SIAME"""
        try:
            self.logger.info(f"Desplegando infraestructura Azure completa (nivel: {security_tier.value})")

            results = {}

            # 1. Desplegar Form Recognizer
            self.logger.info("Desplegando Azure Form Recognizer...")
            form_recognizer_result = await self.deploy_form_recognizer(
                service_name=f"siame-fr-{self.azure_config.environment}",
                security_tier=security_tier
            )
            results["form_recognizer"] = form_recognizer_result

            if form_recognizer_result.success:
                # 2. Desplegar Blob Storage
                self.logger.info("Desplegando Azure Blob Storage...")
                storage_result = await self.deploy_blob_storage(
                    account_name=f"siamestorage{self.azure_config.environment}",
                    security_tier=security_tier
                )
                results["blob_storage"] = storage_result

                if storage_result.success:
                    # 3. Desplegar Key Vault
                    self.logger.info("Desplegando Azure Key Vault...")
                    keyvault_result = await self.deploy_key_vault(
                        vault_name=f"siame-kv-{self.azure_config.environment}",
                        security_tier=security_tier
                    )
                    results["key_vault"] = keyvault_result

                    if keyvault_result.success:
                        # 4. Configurar modelos personalizados
                        self.logger.info("Configurando modelos personalizados...")
                        await self._setup_custom_models()

                        # 5. Configurar contenedores de almacenamiento
                        self.logger.info("Configurando contenedores de almacenamiento...")
                        await self._setup_storage_containers(security_tier)

                        # 6. Almacenar secretos en Key Vault
                        self.logger.info("Almacenando secretos en Key Vault...")
                        await self._store_secrets_in_keyvault()

                        # 7. Generar código de integración
                        self.logger.info("Generando código de integración...")
                        integration_code = await self.generate_integration_code()
                        results["integration_code"] = AzureDeploymentResult(
                            service_type=AzureServiceType.COGNITIVE_SERVICES,
                            resource_name="integration_code",
                            endpoint="",
                            success=True,
                            generated_code=integration_code
                        )

            self.logger.info("Despliegue de infraestructura Azure completado")
            return results

        except Exception as e:
            self.logger.error(f"Error desplegando infraestructura Azure: {e}")
            return {"error": AzureDeploymentResult(
                service_type=AzureServiceType.COGNITIVE_SERVICES,
                resource_name="infrastructure",
                endpoint="",
                success=False,
                error_message=str(e)
            )}

    async def deploy_form_recognizer(self, service_name: str, security_tier: SecurityTier) -> AzureDeploymentResult:
        """Despliega Azure Form Recognizer con configuración diplomática"""
        try:
            self.logger.info(f"Desplegando Form Recognizer: {service_name}")

            # Determinar SKU basado en nivel de seguridad
            sku = "S0"  # Standard para uso diplomático
            if security_tier in [SecurityTier.SECRET, SecurityTier.TOP_SECRET]:
                sku = "S0"  # Premium no disponible en todas las regiones

            # Crear recurso Form Recognizer
            form_recognizer_resource = {
                "location": self.azure_config.location,
                "sku": {"name": sku},
                "kind": "FormRecognizer",
                "properties": {
                    "customSubDomainName": service_name,
                    "publicNetworkAccess": "Enabled" if security_tier == SecurityTier.PUBLIC else "Disabled"
                }
            }

            # Desplegar usando ARM template
            deployment_result = await self._deploy_arm_template(
                "form_recognizer_template",
                {
                    "serviceName": service_name,
                    "sku": sku,
                    "location": self.azure_config.location
                }
            )

            if deployment_result["success"]:
                # Configurar Form Recognizer
                endpoint = f"https://{service_name}.cognitiveservices.azure.com/"
                api_key = await self._get_service_key(service_name, "CognitiveServices")

                self.form_recognizer_config = FormRecognizerConfig(
                    service_name=service_name,
                    sku=sku,
                    endpoint=endpoint,
                    api_key=api_key
                )

                self.stats["services_deployed"] += 1

                return AzureDeploymentResult(
                    service_type=AzureServiceType.FORM_RECOGNIZER,
                    resource_name=service_name,
                    endpoint=endpoint,
                    success=True,
                    configuration={
                        "endpoint": endpoint,
                        "sku": sku,
                        "security_tier": security_tier.value
                    }
                )

            else:
                return AzureDeploymentResult(
                    service_type=AzureServiceType.FORM_RECOGNIZER,
                    resource_name=service_name,
                    endpoint="",
                    success=False,
                    error_message=deployment_result.get("error", "Unknown deployment error")
                )

        except Exception as e:
            self.logger.error(f"Error desplegando Form Recognizer: {e}")
            return AzureDeploymentResult(
                service_type=AzureServiceType.FORM_RECOGNIZER,
                resource_name=service_name,
                endpoint="",
                success=False,
                error_message=str(e)
            )

    async def deploy_blob_storage(self, account_name: str, security_tier: SecurityTier) -> AzureDeploymentResult:
        """Despliega Azure Blob Storage con configuración de seguridad diplomática"""
        try:
            self.logger.info(f"Desplegando Blob Storage: {account_name}")

            # Configuración de seguridad basada en nivel
            security_settings = self._get_storage_security_settings(security_tier)

            # Crear cuenta de almacenamiento
            storage_account_params = {
                "location": self.azure_config.location,
                "sku": {"name": "Standard_LRS"},
                "kind": "StorageV2",
                "properties": {
                    "supportsHttpsTrafficOnly": True,
                    "minimumTlsVersion": "TLS1_2",
                    "allowBlobPublicAccess": security_tier == SecurityTier.PUBLIC,
                    "publicNetworkAccess": "Enabled" if security_tier in [SecurityTier.PUBLIC, SecurityTier.RESTRICTED] else "Disabled",
                    "encryption": {
                        "services": {
                            "blob": {"enabled": True},
                            "file": {"enabled": True}
                        },
                        "keySource": "Microsoft.Storage"
                    }
                }
            }

            # Agregar configuración de red privada para niveles altos de seguridad
            if security_tier in [SecurityTier.SECRET, SecurityTier.TOP_SECRET]:
                storage_account_params["properties"]["networkAcls"] = {
                    "bypass": "AzureServices",
                    "defaultAction": "Deny",
                    "ipRules": [],
                    "virtualNetworkRules": []
                }

            # Desplegar usando management client
            deployment_result = await self._create_storage_account(account_name, storage_account_params)

            if deployment_result["success"]:
                # Obtener claves de acceso
                connection_string = await self._get_storage_connection_string(account_name)

                self.blob_storage_config = BlobStorageConfig(
                    account_name=account_name,
                    connection_string=connection_string,
                    security_settings=security_settings
                )

                # Configurar contenedores diplomáticos
                await self._create_diplomatic_containers(connection_string, security_tier)

                self.stats["services_deployed"] += 1

                return AzureDeploymentResult(
                    service_type=AzureServiceType.BLOB_STORAGE,
                    resource_name=account_name,
                    endpoint=f"https://{account_name}.blob.core.windows.net",
                    success=True,
                    configuration={
                        "account_name": account_name,
                        "security_tier": security_tier.value,
                        "encryption": "enabled",
                        "https_only": True
                    }
                )

            else:
                return AzureDeploymentResult(
                    service_type=AzureServiceType.BLOB_STORAGE,
                    resource_name=account_name,
                    endpoint="",
                    success=False,
                    error_message=deployment_result.get("error", "Storage deployment failed")
                )

        except Exception as e:
            self.logger.error(f"Error desplegando Blob Storage: {e}")
            return AzureDeploymentResult(
                service_type=AzureServiceType.BLOB_STORAGE,
                resource_name=account_name,
                endpoint="",
                success=False,
                error_message=str(e)
            )

    async def deploy_key_vault(self, vault_name: str, security_tier: SecurityTier) -> AzureDeploymentResult:
        """Despliega Azure Key Vault para gestión segura de secretos"""
        try:
            self.logger.info(f"Desplegando Key Vault: {vault_name}")

            # Configuración de Key Vault basada en seguridad
            vault_properties = {
                "location": self.azure_config.location,
                "properties": {
                    "sku": {"family": "A", "name": "premium" if security_tier in [SecurityTier.SECRET, SecurityTier.TOP_SECRET] else "standard"},
                    "tenantId": self.azure_config.tenant_id,
                    "enabledForDeployment": False,
                    "enabledForDiskEncryption": True,
                    "enabledForTemplateDeployment": True,
                    "enableSoftDelete": True,
                    "softDeleteRetentionInDays": 90,
                    "enablePurgeProtection": security_tier in [SecurityTier.SECRET, SecurityTier.TOP_SECRET],
                    "publicNetworkAccess": "enabled" if security_tier in [SecurityTier.PUBLIC, SecurityTier.RESTRICTED] else "disabled",
                    "accessPolicies": [
                        {
                            "tenantId": self.azure_config.tenant_id,
                            "objectId": await self._get_service_principal_object_id(),
                            "permissions": {
                                "keys": ["get", "list", "create", "delete", "update"],
                                "secrets": ["get", "list", "set", "delete"],
                                "certificates": ["get", "list", "create", "delete", "update"]
                            }
                        }
                    ]
                }
            }

            # Desplegar Key Vault
            deployment_result = await self._create_key_vault(vault_name, vault_properties)

            if deployment_result["success"]:
                vault_url = f"https://{vault_name}.vault.azure.net/"

                self.key_vault_config = KeyVaultConfig(
                    vault_name=vault_name,
                    vault_url=vault_url
                )

                self.stats["services_deployed"] += 1

                return AzureDeploymentResult(
                    service_type=AzureServiceType.KEY_VAULT,
                    resource_name=vault_name,
                    endpoint=vault_url,
                    success=True,
                    configuration={
                        "vault_url": vault_url,
                        "sku": vault_properties["properties"]["sku"]["name"],
                        "security_tier": security_tier.value,
                        "soft_delete": True,
                        "purge_protection": vault_properties["properties"].get("enablePurgeProtection", False)
                    }
                )

            else:
                return AzureDeploymentResult(
                    service_type=AzureServiceType.KEY_VAULT,
                    resource_name=vault_name,
                    endpoint="",
                    success=False,
                    error_message=deployment_result.get("error", "Key Vault deployment failed")
                )

        except Exception as e:
            self.logger.error(f"Error desplegando Key Vault: {e}")
            return AzureDeploymentResult(
                service_type=AzureServiceType.KEY_VAULT,
                resource_name=vault_name,
                endpoint="",
                success=False,
                error_message=str(e)
            )

    async def create_custom_form_recognizer_models(self, training_data_path: Path) -> Dict[str, str]:
        """Crea modelos personalizados de Form Recognizer para documentos diplomáticos"""
        try:
            self.logger.info("Creando modelos personalizados de Form Recognizer...")

            if not self.form_recognizer_config:
                raise Exception("Form Recognizer no configurado")

            # Configurar cliente de administración
            admin_client = DocumentModelAdministrationClient(
                endpoint=self.form_recognizer_config.endpoint,
                credential=self.credentials
            )

            models_created = {}

            # Modelos diplomáticos a crear
            diplomatic_models = {
                DiplomaticDocumentModel.HOJA_OGA: {
                    "description": "Modelo para Hojas de Remisión OGA",
                    "training_path": training_data_path / "hoja_oga"
                },
                DiplomaticDocumentModel.HOJA_PCO: {
                    "description": "Modelo para Hojas de Remisión PCO",
                    "training_path": training_data_path / "hoja_pco"
                },
                DiplomaticDocumentModel.GUIA_ENTRADA_ORD: {
                    "description": "Modelo para Guías de Valija Entrada Ordinaria",
                    "training_path": training_data_path / "guia_entrada_ord"
                },
                DiplomaticDocumentModel.GUIA_SALIDA_EXT: {
                    "description": "Modelo para Guías de Valija Salida Extraordinaria",
                    "training_path": training_data_path / "guia_salida_ext"
                }
            }

            for model_enum, model_info in diplomatic_models.items():
                try:
                    self.logger.info(f"Creando modelo: {model_enum.value}")

                    # Subir datos de entrenamiento a Blob Storage
                    training_blob_url = await self._upload_training_data(
                        model_info["training_path"],
                        f"training-data/{model_enum.value}"
                    )

                    # Crear modelo personalizado
                    model_operation = admin_client.begin_build_document_model(
                        build_mode="template",
                        blob_container_url=training_blob_url,
                        model_id=model_enum.value,
                        description=model_info["description"]
                    )

                    # Esperar a que complete el entrenamiento
                    custom_model = model_operation.result()

                    models_created[model_enum.value] = custom_model.model_id
                    self.form_recognizer_config.custom_models[model_enum.value] = custom_model.model_id

                    self.stats["models_trained"] += 1
                    self.logger.info(f"Modelo {model_enum.value} creado exitosamente")

                except Exception as e:
                    self.logger.error(f"Error creando modelo {model_enum.value}: {e}")

            return models_created

        except Exception as e:
            self.logger.error(f"Error creando modelos personalizados: {e}")
            return {}

    async def generate_integration_code(self) -> str:
        """Genera código Python y TypeScript para integración con Azure"""
        try:
            self.logger.info("Generando código de integración Azure...")

            # Código Python para integración
            python_code = self._generate_python_integration_code()

            # Código TypeScript para frontend
            typescript_code = self._generate_typescript_integration_code()

            # Código de configuración
            config_code = self._generate_configuration_code()

            # Combinar todo el código
            complete_code = f"""
# ============================================================================
# SIAME 2026v3 - Código de Integración Azure Generado Automáticamente
# Generado: {datetime.now().isoformat()}
# ============================================================================

{config_code}

{python_code}

{typescript_code}
"""

            self.stats["code_generated"] += 1
            return complete_code

        except Exception as e:
            self.logger.error(f"Error generando código de integración: {e}")
            return f"# Error generando código: {e}"

    async def get_agent_status(self) -> Dict[str, Any]:
        """Obtiene el estado completo del agente Azure"""
        return {
            "agent_id": self.agent_id,
            "agent_type": "Azure Specialist",
            "azure_connection": self.credentials is not None,
            "services_configured": {
                "form_recognizer": self.form_recognizer_config is not None,
                "blob_storage": self.blob_storage_config is not None,
                "key_vault": self.key_vault_config is not None
            },
            "statistics": self.stats,
            "azure_config": {
                "subscription_id": self.azure_config.subscription_id if self.azure_config else None,
                "resource_group": self.azure_config.resource_group if self.azure_config else None,
                "location": self.azure_config.location if self.azure_config else None,
                "environment": self.azure_config.environment if self.azure_config else None
            }
        }

    # Métodos privados de implementación

    async def _initialize_management_clients(self) -> None:
        """Inicializa clientes de Azure Management"""
        try:
            self.resource_client = ResourceManagementClient(
                self.credentials,
                self.azure_config.subscription_id
            )

            self.storage_client = StorageManagementClient(
                self.credentials,
                self.azure_config.subscription_id
            )

            self.cognitive_client = CognitiveServicesManagementClient(
                self.credentials,
                self.azure_config.subscription_id
            )

            self.keyvault_client = KeyVaultManagementClient(
                self.credentials,
                self.azure_config.subscription_id
            )

            self.logger.info("Clientes de Azure Management inicializados")

        except Exception as e:
            self.logger.error(f"Error inicializando clientes Management: {e}")
            raise

    async def _verify_azure_connectivity(self) -> None:
        """Verifica conectividad con Azure"""
        try:
            # Verificar que el resource group existe
            resource_groups = list(self.resource_client.resource_groups.list())
            rg_exists = any(rg.name == self.azure_config.resource_group for rg in resource_groups)

            if not rg_exists:
                # Crear resource group si no existe
                self.resource_client.resource_groups.create_or_update(
                    self.azure_config.resource_group,
                    {"location": self.azure_config.location}
                )
                self.logger.info(f"Resource group {self.azure_config.resource_group} creado")

            self.logger.info("Conectividad con Azure verificada")

        except Exception as e:
            self.logger.error(f"Error verificando conectividad Azure: {e}")
            raise

    def _get_storage_security_settings(self, security_tier: SecurityTier) -> Dict[str, Any]:
        """Obtiene configuración de seguridad para almacenamiento"""
        settings = {
            "encryption": True,
            "https_only": True,
            "min_tls_version": "TLS1_2",
            "public_access": False,
            "soft_delete_enabled": True,
            "soft_delete_retention_days": 7
        }

        if security_tier in [SecurityTier.CONFIDENTIAL, SecurityTier.SECRET, SecurityTier.TOP_SECRET]:
            settings.update({
                "public_access": False,
                "network_access": "private",
                "soft_delete_retention_days": 30,
                "versioning_enabled": True,
                "change_feed_enabled": True
            })

        if security_tier in [SecurityTier.SECRET, SecurityTier.TOP_SECRET]:
            settings.update({
                "customer_managed_key": True,
                "immutable_storage": True,
                "audit_logs": True
            })

        return settings

    async def _setup_custom_models(self) -> None:
        """Configura modelos personalizados para documentos diplomáticos"""
        try:
            # Crear datos de entrenamiento simulados (en producción usar datos reales)
            training_data_path = Path("training_data_temp")
            training_data_path.mkdir(exist_ok=True)

            # Crear subdirectorios para cada tipo de documento
            for model in DiplomaticDocumentModel:
                model_dir = training_data_path / model.value
                model_dir.mkdir(exist_ok=True)

                # Crear archivos de ejemplo (placeholder)
                sample_file = model_dir / "sample.txt"
                with open(sample_file, 'w') as f:
                    f.write(f"Documento de entrenamiento para {model.value}")

            # Crear modelos personalizados
            await self.create_custom_form_recognizer_models(training_data_path)

            # Limpiar archivos temporales
            import shutil
            shutil.rmtree(training_data_path, ignore_errors=True)

        except Exception as e:
            self.logger.error(f"Error configurando modelos personalizados: {e}")

    async def _setup_storage_containers(self, security_tier: SecurityTier) -> None:
        """Configura contenedores de almacenamiento para documentos diplomáticos"""
        try:
            if not self.blob_storage_config:
                raise Exception("Blob Storage no configurado")

            # Contenedores diplomáticos
            containers = {
                "diplomatic-documents": {
                    "public_access": "none",
                    "metadata": {"document_type": "diplomatic", "security_level": security_tier.value}
                },
                "training-data": {
                    "public_access": "none",
                    "metadata": {"purpose": "model_training"}
                },
                "processed-documents": {
                    "public_access": "none",
                    "metadata": {"status": "processed"}
                },
                "audit-logs": {
                    "public_access": "none",
                    "metadata": {"purpose": "audit", "retention": "7_years"}
                }
            }

            blob_service = BlobServiceClient.from_connection_string(
                self.blob_storage_config.connection_string
            )

            for container_name, container_config in containers.items():
                try:
                    container_client = blob_service.get_container_client(container_name)

                    # Crear contenedor si no existe
                    if not container_client.exists():
                        container_client.create_container(
                            public_access=container_config["public_access"],
                            metadata=container_config["metadata"]
                        )
                        self.logger.info(f"Contenedor {container_name} creado")

                    self.blob_storage_config.containers[container_name] = container_config
                    self.stats["containers_created"] += 1

                except Exception as e:
                    self.logger.error(f"Error creando contenedor {container_name}: {e}")

        except Exception as e:
            self.logger.error(f"Error configurando contenedores: {e}")

    async def _store_secrets_in_keyvault(self) -> None:
        """Almacena secretos importantes en Key Vault"""
        try:
            if not self.key_vault_config:
                raise Exception("Key Vault no configurado")

            secret_client = SecretClient(
                vault_url=self.key_vault_config.vault_url,
                credential=self.credentials
            )

            # Secretos a almacenar
            secrets = {
                "siame-form-recognizer-key": self.form_recognizer_config.api_key if self.form_recognizer_config else "",
                "siame-storage-connection-string": self.blob_storage_config.connection_string if self.blob_storage_config else "",
                "siame-encryption-key": self._generate_encryption_key(),
                "siame-jwt-secret": self._generate_jwt_secret(),
                "siame-database-password": self._generate_secure_password()
            }

            for secret_name, secret_value in secrets.items():
                if secret_value:
                    try:
                        secret_client.set_secret(secret_name, secret_value)
                        self.key_vault_config.secrets[secret_name] = secret_name  # Almacenar nombre, no valor
                        self.stats["secrets_stored"] += 1
                        self.logger.info(f"Secreto {secret_name} almacenado en Key Vault")

                    except Exception as e:
                        self.logger.error(f"Error almacenando secreto {secret_name}: {e}")

        except Exception as e:
            self.logger.error(f"Error almacenando secretos en Key Vault: {e}")

    def _generate_encryption_key(self) -> str:
        """Genera clave de encriptación segura"""
        return base64.b64encode(secrets.token_bytes(32)).decode('utf-8')

    def _generate_jwt_secret(self) -> str:
        """Genera secreto JWT seguro"""
        return secrets.token_urlsafe(64)

    def _generate_secure_password(self) -> str:
        """Genera contraseña segura"""
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        return ''.join(secrets.choice(alphabet) for _ in range(32))

    def _generate_python_integration_code(self) -> str:
        """Genera código Python para integración Azure"""
        return f'''
# ============================================================================
# CÓDIGO PYTHON PARA INTEGRACIÓN AZURE
# ============================================================================

import os
from azure.identity import DefaultAzureCredential
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.storage.blob import BlobServiceClient
from azure.keyvault.secrets import SecretClient

class SiameAzureIntegration:
    """Integración Azure para SIAME 2026v3"""

    def __init__(self):
        self.credential = DefaultAzureCredential()

        # Configuración desde Key Vault
        self.key_vault_url = "{self.key_vault_config.vault_url if self.key_vault_config else 'https://your-keyvault.vault.azure.net/'}"
        self.secret_client = SecretClient(
            vault_url=self.key_vault_url,
            credential=self.credential
        )

        # Form Recognizer
        self.form_recognizer_endpoint = "{self.form_recognizer_config.endpoint if self.form_recognizer_config else 'https://your-form-recognizer.cognitiveservices.azure.com/'}"
        self.form_recognizer_client = DocumentAnalysisClient(
            endpoint=self.form_recognizer_endpoint,
            credential=self.credential
        )

        # Blob Storage
        self.storage_account_name = "{self.blob_storage_config.account_name if self.blob_storage_config else 'your-storage-account'}"
        self.blob_service_client = BlobServiceClient(
            account_url=f"https://{{self.storage_account_name}}.blob.core.windows.net",
            credential=self.credential
        )

    async def process_diplomatic_document(self, file_path: str, document_type: str) -> dict:
        """Procesa documento diplomático con Form Recognizer"""
        try:
            # Determinar modelo basado en tipo de documento
            model_mapping = {{
                "hoja_oga": "{DiplomaticDocumentModel.HOJA_OGA.value}",
                "hoja_pco": "{DiplomaticDocumentModel.HOJA_PCO.value}",
                "guia_entrada_ord": "{DiplomaticDocumentModel.GUIA_ENTRADA_ORD.value}",
                "guia_salida_ext": "{DiplomaticDocumentModel.GUIA_SALIDA_EXT.value}"
            }}

            model_id = model_mapping.get(document_type, "prebuilt-document")

            # Procesar documento
            with open(file_path, "rb") as document:
                poller = self.form_recognizer_client.begin_analyze_document(
                    model_id=model_id,
                    document=document
                )
                result = poller.result()

            # Extraer datos específicos según el tipo de documento
            extracted_data = self._extract_document_data(result, document_type)

            return {{
                "success": True,
                "document_type": document_type,
                "extracted_data": extracted_data,
                "confidence_score": self._calculate_average_confidence(result)
            }}

        except Exception as e:
            return {{
                "success": False,
                "error": str(e)
            }}

    def _extract_document_data(self, result, document_type: str) -> dict:
        """Extrae datos específicos según el tipo de documento"""
        extracted = {{}}

        if document_type == "hoja_oga":
            # Campos específicos para Hoja OGA
            fields_mapping = {{
                "numero_remision": ["Número de Remisión", "Remisión No", "HR-OGA"],
                "fecha": ["Fecha", "Date"],
                "origen": ["Origen", "De", "From"],
                "destino": ["Destino", "Para", "To"],
                "clasificacion": ["Clasificación", "Classification"],
                "asunto": ["Asunto", "Subject"]
            }}
        elif document_type == "guia_valija":
            # Campos específicos para Guía de Valija
            fields_mapping = {{
                "numero_guia": ["Número de Guía", "Guía No", "GV"],
                "fecha_envio": ["Fecha de Envío", "Fecha"],
                "destino": ["Destino", "Destination"],
                "peso_total": ["Peso Total", "Weight"],
                "cantidad_documentos": ["Cantidad", "Documentos"]
            }}
        else:
            fields_mapping = {{}}

        # Extraer campos usando mapeo
        for field_name, possible_labels in fields_mapping.items():
            for document in result.documents:
                for label in possible_labels:
                    if label in document.fields:
                        field = document.fields[label]
                        extracted[field_name] = {{
                            "value": field.value,
                            "confidence": field.confidence
                        }}
                        break
                if field_name in extracted:
                    break

        return extracted

    def _calculate_average_confidence(self, result) -> float:
        """Calcula confianza promedio del resultado"""
        confidences = []
        for document in result.documents:
            for field in document.fields.values():
                if field.confidence:
                    confidences.append(field.confidence)

        return sum(confidences) / len(confidences) if confidences else 0.0

    async def upload_document_to_storage(self, file_path: str, container_name: str = "diplomatic-documents") -> str:
        """Sube documento a Blob Storage"""
        try:
            blob_name = f"{{datetime.now().strftime('%Y/%m/%d')}}/{{os.path.basename(file_path)}}"

            blob_client = self.blob_service_client.get_blob_client(
                container=container_name,
                blob=blob_name
            )

            with open(file_path, "rb") as data:
                blob_client.upload_blob(data, overwrite=True)

            return blob_client.url

        except Exception as e:
            raise Exception(f"Error subiendo archivo: {{e}}")

    async def get_secret(self, secret_name: str) -> str:
        """Obtiene secreto de Key Vault"""
        try:
            secret = self.secret_client.get_secret(secret_name)
            return secret.value
        except Exception as e:
            raise Exception(f"Error obteniendo secreto {{secret_name}}: {{e}}")

# Ejemplo de uso
# azure_integration = SiameAzureIntegration()
# result = await azure_integration.process_diplomatic_document("hoja_oga.pdf", "hoja_oga")
'''

    def _generate_typescript_integration_code(self) -> str:
        """Genera código TypeScript para frontend"""
        return '''
// ============================================================================
// CÓDIGO TYPESCRIPT PARA FRONTEND NEXT.JS
// ============================================================================

import { DefaultAzureCredential } from '@azure/identity';
import { BlobServiceClient } from '@azure/storage-blob';

interface DiplomaticDocument {
  id: string;
  type: 'hoja_oga' | 'hoja_pco' | 'guia_entrada_ord' | 'guia_salida_ext';
  securityLevel: 'public' | 'restricted' | 'confidential' | 'secret' | 'top_secret';
  extractedData: Record<string, any>;
  confidenceScore: number;
  uploadedAt: Date;
}

interface ProcessingResult {
  success: boolean;
  documentId?: string;
  extractedData?: Record<string, any>;
  error?: string;
}

export class SiameAzureFrontendIntegration {
  private blobServiceClient: BlobServiceClient;

  constructor(private storageAccountName: string) {
    // En producción, usar tokens de autenticación apropiados
    this.blobServiceClient = new BlobServiceClient(
      `https://${storageAccountName}.blob.core.windows.net`,
      new DefaultAzureCredential()
    );
  }

  async uploadDiplomaticDocument(
    file: File,
    documentType: string,
    securityLevel: string
  ): Promise<ProcessingResult> {
    try {
      // Validar tipo de archivo
      const allowedTypes = ['application/pdf', 'text/plain', 'image/jpeg', 'image/png'];
      if (!allowedTypes.includes(file.type)) {
        throw new Error('Tipo de archivo no permitido');
      }

      // Validar tamaño (máximo 10MB para documentos diplomáticos)
      if (file.size > 10 * 1024 * 1024) {
        throw new Error('Archivo demasiado grande (máximo 10MB)');
      }

      // Generar nombre único para el blob
      const blobName = `${new Date().toISOString().split('T')[0]}/${Date.now()}-${file.name}`;

      // Subir a contenedor apropiado basado en nivel de seguridad
      const containerName = this.getContainerForSecurityLevel(securityLevel);
      const blockBlobClient = this.blobServiceClient.getBlockBlobClient(containerName, blobName);

      // Metadatos del documento
      const metadata = {
        documentType,
        securityLevel,
        uploadedBy: 'user-id', // En producción, obtener del contexto de autenticación
        originalFileName: file.name,
        fileSize: file.size.toString()
      };

      // Subir archivo
      await blockBlobClient.uploadData(await file.arrayBuffer(), {
        metadata,
        blobHTTPHeaders: {
          blobContentType: file.type
        }
      });

      // Procesar documento con API backend
      const processingResult = await this.processDocumentWithBackend(blobName, documentType);

      return {
        success: true,
        documentId: blobName,
        extractedData: processingResult.extractedData
      };

    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Error desconocido'
      };
    }
  }

  private getContainerForSecurityLevel(securityLevel: string): string {
    const containerMapping: Record<string, string> = {
      'public': 'public-documents',
      'restricted': 'restricted-documents',
      'confidential': 'confidential-documents',
      'secret': 'secret-documents',
      'top_secret': 'top-secret-documents'
    };

    return containerMapping[securityLevel] || 'diplomatic-documents';
  }

  private async processDocumentWithBackend(blobName: string, documentType: string): Promise<any> {
    const response = await fetch('/api/documents/process', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('authToken')}`
      },
      body: JSON.stringify({
        blobName,
        documentType
      })
    });

    if (!response.ok) {
      throw new Error(`Error procesando documento: ${response.statusText}`);
    }

    return response.json();
  }

  async getDiplomaticDocuments(
    documentType?: string,
    securityLevel?: string,
    page: number = 1,
    limit: number = 50
  ): Promise<DiplomaticDocument[]> {
    try {
      const params = new URLSearchParams({
        page: page.toString(),
        limit: limit.toString()
      });

      if (documentType) params.append('type', documentType);
      if (securityLevel) params.append('security', securityLevel);

      const response = await fetch(`/api/documents?${params}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('authToken')}`
        }
      });

      if (!response.ok) {
        throw new Error('Error obteniendo documentos');
      }

      return response.json();

    } catch (error) {
      console.error('Error obteniendo documentos:', error);
      return [];
    }
  }

  async downloadDocument(documentId: string): Promise<Blob | null> {
    try {
      const response = await fetch(`/api/documents/${documentId}/download`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('authToken')}`
        }
      });

      if (!response.ok) {
        throw new Error('Error descargando documento');
      }

      return response.blob();

    } catch (error) {
      console.error('Error descargando documento:', error);
      return null;
    }
  }
}

// Hook de React para usar la integración
export function useSiameAzureIntegration() {
  const integration = new SiameAzureFrontendIntegration(process.env.NEXT_PUBLIC_STORAGE_ACCOUNT_NAME!);

  return {
    uploadDocument: integration.uploadDiplomaticDocument.bind(integration),
    getDocuments: integration.getDiplomaticDocuments.bind(integration),
    downloadDocument: integration.downloadDocument.bind(integration)
  };
}
'''

    def _generate_configuration_code(self) -> str:
        """Genera código de configuración"""
        return f'''
# ============================================================================
# CONFIGURACIÓN AZURE PARA SIAME 2026v3
# ============================================================================

# Variables de entorno requeridas (.env.local)
AZURE_TENANT_ID={self.azure_config.tenant_id if self.azure_config else 'your-tenant-id'}
AZURE_CLIENT_ID={self.azure_config.client_id if self.azure_config else 'your-client-id'}
AZURE_CLIENT_SECRET={self.azure_config.client_secret if self.azure_config else 'your-client-secret'}
AZURE_SUBSCRIPTION_ID={self.azure_config.subscription_id if self.azure_config else 'your-subscription-id'}

# Configuración de servicios
AZURE_FORM_RECOGNIZER_ENDPOINT={self.form_recognizer_config.endpoint if self.form_recognizer_config else 'https://your-form-recognizer.cognitiveservices.azure.com/'}
AZURE_STORAGE_ACCOUNT_NAME={self.blob_storage_config.account_name if self.blob_storage_config else 'your-storage-account'}
AZURE_KEY_VAULT_URL={self.key_vault_config.vault_url if self.key_vault_config else 'https://your-keyvault.vault.azure.net/'}

# Configuración de Next.js (next.config.js)
module.exports = {{
  env: {{
    AZURE_STORAGE_ACCOUNT_NAME: process.env.AZURE_STORAGE_ACCOUNT_NAME,
    AZURE_FORM_RECOGNIZER_ENDPOINT: process.env.AZURE_FORM_RECOGNIZER_ENDPOINT,
  }},
  async headers() {{
    return [
      {{
        source: '/api/:path*',
        headers: [
          {{
            key: 'Access-Control-Allow-Origin',
            value: '*',
          }},
          {{
            key: 'Access-Control-Allow-Methods',
            value: 'GET, POST, PUT, DELETE, OPTIONS',
          }},
          {{
            key: 'Access-Control-Allow-Headers',
            value: 'Content-Type, Authorization',
          }},
        ],
      }},
    ];
  }},
}};

# Configuración de Prisma (schema.prisma)
generator client {{
  provider = "prisma-client-js"
}}

datasource db {{
  provider = "postgresql"
  url      = env("DATABASE_URL")
}}

model DiplomaticDocument {{
  id                String   @id @default(uuid())
  documentType      String
  securityLevel     String
  blobName          String
  extractedData     Json?
  confidenceScore   Float?
  uploadedBy        String
  createdAt         DateTime @default(now())
  updatedAt         DateTime @updatedAt

  @@map("diplomatic_documents")
}}

model AuditLog {{
  id        String   @id @default(uuid())
  action    String
  userId    String
  documentId String?
  details   Json?
  ipAddress String?
  userAgent String?
  createdAt DateTime @default(now())

  @@map("audit_logs")
}}
'''

    def _initialize_arm_templates(self) -> Dict[str, str]:
        """Inicializa templates ARM para despliegue"""
        return {
            "form_recognizer_template": """
{
    "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
    "contentVersion": "1.0.0.0",
    "parameters": {
        "serviceName": {
            "type": "string"
        },
        "sku": {
            "type": "string",
            "defaultValue": "S0"
        },
        "location": {
            "type": "string",
            "defaultValue": "East US"
        }
    },
    "resources": [
        {
            "type": "Microsoft.CognitiveServices/accounts",
            "apiVersion": "2021-04-30",
            "name": "[parameters('serviceName')]",
            "location": "[parameters('location')]",
            "sku": {
                "name": "[parameters('sku')]"
            },
            "kind": "FormRecognizer",
            "properties": {
                "customSubDomainName": "[parameters('serviceName')]",
                "publicNetworkAccess": "Enabled"
            }
        }
    ]
}
""",
            "storage_template": """
{
    "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
    "contentVersion": "1.0.0.0",
    "parameters": {
        "storageAccountName": {
            "type": "string"
        },
        "location": {
            "type": "string",
            "defaultValue": "East US"
        }
    },
    "resources": [
        {
            "type": "Microsoft.Storage/storageAccounts",
            "apiVersion": "2021-04-01",
            "name": "[parameters('storageAccountName')]",
            "location": "[parameters('location')]",
            "sku": {
                "name": "Standard_LRS"
            },
            "kind": "StorageV2",
            "properties": {
                "supportsHttpsTrafficOnly": true,
                "minimumTlsVersion": "TLS1_2",
                "allowBlobPublicAccess": false
            }
        }
    ]
}
"""
        }

    def _initialize_bicep_templates(self) -> Dict[str, str]:
        """Inicializa templates Bicep para despliegue"""
        return {
            "complete_infrastructure": """
@description('SIAME 2026v3 Complete Infrastructure')
param location string = 'East US'
param environment string = 'dev'
param securityTier string = 'confidential'

// Form Recognizer
resource formRecognizer 'Microsoft.CognitiveServices/accounts@2021-04-30' = {
  name: 'siame-fr-${environment}'
  location: location
  sku: {
    name: 'S0'
  }
  kind: 'FormRecognizer'
  properties: {
    customSubDomainName: 'siame-fr-${environment}'
    publicNetworkAccess: securityTier == 'public' ? 'Enabled' : 'Disabled'
  }
}

// Storage Account
resource storageAccount 'Microsoft.Storage/storageAccounts@2021-04-01' = {
  name: 'siamestorage${environment}'
  location: location
  sku: {
    name: 'Standard_LRS'
  }
  kind: 'StorageV2'
  properties: {
    supportsHttpsTrafficOnly: true
    minimumTlsVersion: 'TLS1_2'
    allowBlobPublicAccess: false
    encryption: {
      services: {
        blob: {
          enabled: true
        }
        file: {
          enabled: true
        }
      }
      keySource: 'Microsoft.Storage'
    }
  }
}

// Key Vault
resource keyVault 'Microsoft.KeyVault/vaults@2021-04-01-preview' = {
  name: 'siame-kv-${environment}'
  location: location
  properties: {
    sku: {
      family: 'A'
      name: securityTier == 'secret' || securityTier == 'top_secret' ? 'premium' : 'standard'
    }
    tenantId: subscription().tenantId
    enabledForDeployment: false
    enabledForDiskEncryption: true
    enabledForTemplateDeployment: true
    enableSoftDelete: true
    softDeleteRetentionInDays: 90
    enablePurgeProtection: securityTier == 'secret' || securityTier == 'top_secret'
  }
}
"""
        }

    # Métodos de simulación para cuando Azure SDK no está disponible
    async def _deploy_arm_template(self, template_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Despliega template ARM (simulado si SDK no disponible)"""
        if not AZURE_SDK_AVAILABLE:
            self.logger.warning("Azure SDK no disponible - simulando despliegue")
            return {"success": True, "deployment_id": f"simulated_{uuid.uuid4().hex[:8]}"}

        # Implementación real cuando SDK está disponible
        try:
            # TODO: Implementar despliegue real de ARM template
            return {"success": True, "deployment_id": f"real_{uuid.uuid4().hex[:8]}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _get_service_key(self, service_name: str, service_type: str) -> str:
        """Obtiene clave de servicio (simulado si SDK no disponible)"""
        if not AZURE_SDK_AVAILABLE:
            return f"simulated_key_{service_name}_{secrets.token_hex(16)}"

        # TODO: Implementar obtención real de claves
        return f"real_key_{secrets.token_hex(32)}"

    async def _create_storage_account(self, account_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Crea cuenta de almacenamiento (simulado si SDK no disponible)"""
        if not AZURE_SDK_AVAILABLE:
            return {"success": True, "account_name": account_name}

        # TODO: Implementar creación real
        return {"success": True, "account_name": account_name}

    async def _get_storage_connection_string(self, account_name: str) -> str:
        """Obtiene connection string (simulado si SDK no disponible)"""
        if not AZURE_SDK_AVAILABLE:
            return f"DefaultEndpointsProtocol=https;AccountName={account_name};AccountKey=simulated_key;EndpointSuffix=core.windows.net"

        # TODO: Implementar obtención real
        return f"DefaultEndpointsProtocol=https;AccountName={account_name};AccountKey=real_key;EndpointSuffix=core.windows.net"

    async def _create_diplomatic_containers(self, connection_string: str, security_tier: SecurityTier) -> None:
        """Crea contenedores diplomáticos (simulado si SDK no disponible)"""
        if not AZURE_SDK_AVAILABLE:
            self.logger.info("Simulando creación de contenedores diplomáticos")
            return

        # TODO: Implementar creación real de contenedores

    async def _create_key_vault(self, vault_name: str, properties: Dict[str, Any]) -> Dict[str, Any]:
        """Crea Key Vault (simulado si SDK no disponible)"""
        if not AZURE_SDK_AVAILABLE:
            return {"success": True, "vault_name": vault_name}

        # TODO: Implementar creación real
        return {"success": True, "vault_name": vault_name}

    async def _get_service_principal_object_id(self) -> str:
        """Obtiene Object ID del service principal"""
        # En implementación real, obtener del Azure AD
        return str(uuid.uuid4())

    async def _upload_training_data(self, local_path: Path, blob_path: str) -> str:
        """Sube datos de entrenamiento a Blob Storage"""
        # En implementación real, subir archivos reales
        return f"https://siamestorage.blob.core.windows.net/{blob_path}"


# Función principal para testing
async def main():
    """Función principal para testing del agente Azure"""
    logging.basicConfig(level=logging.INFO)

    # Configuración de ejemplo
    azure_config = AzureConfiguration(
        subscription_id="12345678-1234-1234-1234-123456789012",
        tenant_id="87654321-4321-4321-4321-210987654321",
        client_id="11111111-1111-1111-1111-111111111111",
        client_secret="your_client_secret_here",
        resource_group="siame-rg-dev",
        location="East US",
        environment="development"
    )

    agent = AzureSpecialistAgent()

    try:
        # Inicializar agente
        success = await agent.initialize(azure_config)
        if success:
            print("✅ Azure Specialist Agent inicializado")

            # Desplegar infraestructura completa
            print("\n🚀 Desplegando infraestructura Azure...")
            results = await agent.deploy_complete_azure_infrastructure(SecurityTier.CONFIDENTIAL)

            print("\n📊 Resultados del despliegue:")
            for service, result in results.items():
                status = "✅" if result.success else "❌"
                print(f"  {status} {service}: {result.resource_name}")
                if not result.success and result.error_message:
                    print(f"    Error: {result.error_message}")

            # Mostrar código generado
            if "integration_code" in results and results["integration_code"].generated_code:
                print("\n📝 Código de integración generado:")
                print("Ver archivo: siame_azure_integration.py")

            # Estadísticas del agente
            status = await agent.get_agent_status()
            print(f"\n📈 Estadísticas del agente:")
            for key, value in status["statistics"].items():
                print(f"  • {key}: {value}")

        else:
            print("❌ Error inicializando Azure Specialist Agent")

    except Exception as e:
        print(f"❌ Error en demo: {e}")


if __name__ == "__main__":
    asyncio.run(main())
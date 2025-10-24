"""
Database Specialist Agent - SIAME 2026v3
Agente especializado en base de datos para gestión completa de esquemas,
migraciones, Row Level Security, auditoría y configuración PostgreSQL
para documentos diplomáticos.
"""

import asyncio
import logging
import json
import uuid
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Union, Any, Tuple
from enum import Enum
from dataclasses import dataclass, field
import os
import subprocess

try:
    import asyncpg
    import psycopg2
    from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
    DATABASE_LIBS_AVAILABLE = True
except ImportError:
    DATABASE_LIBS_AVAILABLE = False

from shared.communication.message_bus import MessageBus, Message, MessageType
from shared.storage.config_manager import ConfigManager
from shared.utils.security_levels import SecurityLevel
from shared.utils.metrics_collector import MetricsCollector


class DatabaseOperation(Enum):
    """Tipos de operaciones de base de datos"""
    CREATE_SCHEMA = "create_schema"
    MIGRATE = "migrate"
    SEED = "seed"
    BACKUP = "backup"
    RESTORE = "restore"
    AUDIT = "audit"
    RLS_SETUP = "rls_setup"


class DiplomaticRole(Enum):
    """Roles diplomáticos en el sistema"""
    EMBAJADOR = "embajador"
    MINISTRO_CONSEJERO = "ministro_consejero"
    CONSEJERO = "consejero"
    PRIMER_SECRETARIO = "primer_secretario"
    SEGUNDO_SECRETARIO = "segundo_secretario"
    TERCER_SECRETARIO = "tercer_secretario"
    AGREGADO = "agregado"
    FUNCIONARIO_ADMINISTRATIVO = "funcionario_administrativo"
    CNSULTOR_EXTERNO = "consultor_externo"
    INVITADO = "invitado"


class DocumentClassification(Enum):
    """Clasificaciones de documentos diplomáticos"""
    PUBLICO = "publico"
    RESTRINGIDO = "restringido"
    CONFIDENCIAL = "confidencial"
    SECRETO = "secreto"
    ALTO_SECRETO = "alto_secreto"


class DocumentType(Enum):
    """Tipos de documentos diplomáticos"""
    HOJA_REMISION_OGA = "hoja_remision_oga"
    HOJA_REMISION_PCO = "hoja_remision_pco"
    HOJA_REMISION_PRU = "hoja_remision_pru"
    GUIA_VALIJA_ENTRADA_ORD = "guia_valija_entrada_ordinaria"
    GUIA_VALIJA_ENTRADA_EXT = "guia_valija_entrada_extraordinaria"
    GUIA_VALIJA_SALIDA_ORD = "guia_valija_salida_ordinaria"
    GUIA_VALIJA_SALIDA_EXT = "guia_valija_salida_extraordinaria"
    NOTA_DIPLOMATICA = "nota_diplomatica"
    DESPACHO = "despacho"
    MEMORANDUM = "memorandum"
    CIRCULAR = "circular"
    INFORME = "informe"


@dataclass
class DatabaseConfig:
    """Configuración de base de datos"""
    host: str = "localhost"
    port: int = 5432
    database: str = "siame_db"
    username: str = "siame_user"
    password: str = "siame_password"
    ssl_mode: str = "require"
    connection_string: str = ""
    max_connections: int = 20

    def __post_init__(self):
        if not self.connection_string:
            self.connection_string = f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}?sslmode={self.ssl_mode}"


@dataclass
class MigrationResult:
    """Resultado de migración"""
    success: bool
    migration_name: str
    executed_at: datetime
    error_message: Optional[str] = None
    sql_executed: Optional[str] = None


class DatabaseSpecialist:
    """
    Agente especializado en base de datos para SIAME 2026v3
    Maneja esquemas, migraciones, RLS, auditoría y configuración PostgreSQL
    """

    def __init__(self, config: Optional[DatabaseConfig] = None):
        self.agent_id = "database_specialist"
        self.config = config or DatabaseConfig()
        self.message_bus = MessageBus()
        self.config_manager = ConfigManager()
        self.metrics = MetricsCollector(agent_id=self.agent_id)

        # Estado de conexión
        self.connection_pool = None
        self.is_initialized = False

        # Logging
        self.logger = logging.getLogger(f"siame.agents.{self.agent_id}")

        # Esquemas y migraciones
        self.prisma_schema = self._generate_complete_prisma_schema()
        self.initial_migrations = self._generate_initial_migrations()
        self.audit_triggers = self._generate_audit_triggers()
        self.rls_policies = self._generate_rls_policies()
        self.seeders = self._generate_initial_seeders()

    async def initialize(self) -> bool:
        """Inicializa el agente de base de datos"""
        try:
            self.logger.info("Inicializando Database Specialist Agent...")

            if not DATABASE_LIBS_AVAILABLE:
                self.logger.error("Librerías de base de datos no disponibles")
                return False

            # Crear conexión pool
            await self._create_connection_pool()

            # Verificar conectividad
            await self._verify_database_connectivity()

            # Suscribirse al message bus
            await self.message_bus.subscribe("database.*", self._handle_message)

            self.is_initialized = True
            self.logger.info("Database Specialist Agent inicializado exitosamente")

            await self.metrics.record_event("agent_initialized", {
                "agent_id": self.agent_id,
                "timestamp": datetime.utcnow().isoformat()
            })

            return True

        except Exception as e:
            self.logger.error(f"Error inicializando Database Specialist: {str(e)}")
            return False

    async def _create_connection_pool(self):
        """Crea el pool de conexiones"""
        try:
            self.connection_pool = await asyncpg.create_pool(
                self.config.connection_string,
                max_size=self.config.max_connections,
                command_timeout=60
            )
            self.logger.info("Pool de conexiones creado exitosamente")

        except Exception as e:
            self.logger.error(f"Error creando pool de conexiones: {str(e)}")
            raise

    async def _verify_database_connectivity(self):
        """Verifica conectividad con la base de datos"""
        try:
            async with self.connection_pool.acquire() as connection:
                result = await connection.fetchval("SELECT version()")
                self.logger.info(f"Conectado a PostgreSQL: {result}")

        except Exception as e:
            self.logger.error(f"Error verificando conectividad: {str(e)}")
            raise

    async def deploy_complete_database_schema(self) -> Dict[str, Any]:
        """Despliega el esquema completo de base de datos para SIAME"""
        try:
            self.logger.info("Desplegando esquema completo de base de datos...")

            results = {
                "schema_deployment": None,
                "migrations": [],
                "rls_setup": None,
                "audit_setup": None,
                "seeders": [],
                "indexes": None,
                "triggers": None
            }

            # 1. Crear esquema inicial
            self.logger.info("Creando esquema inicial...")
            schema_result = await self._create_initial_schema()
            results["schema_deployment"] = schema_result

            if schema_result["success"]:
                # 2. Ejecutar migraciones
                self.logger.info("Ejecutando migraciones...")
                migration_results = await self._execute_migrations()
                results["migrations"] = migration_results

                # 3. Configurar Row Level Security
                self.logger.info("Configurando Row Level Security...")
                rls_result = await self._setup_row_level_security()
                results["rls_setup"] = rls_result

                # 4. Configurar auditoría automática
                self.logger.info("Configurando auditoría automática...")
                audit_result = await self._setup_audit_system()
                results["audit_setup"] = audit_result

                # 5. Crear índices optimizados
                self.logger.info("Creando índices optimizados...")
                indexes_result = await self._create_optimized_indexes()
                results["indexes"] = indexes_result

                # 6. Configurar triggers
                self.logger.info("Configurando triggers...")
                triggers_result = await self._setup_triggers()
                results["triggers"] = triggers_result

                # 7. Ejecutar seeders iniciales
                self.logger.info("Ejecutando seeders iniciales...")
                seeders_results = await self._execute_seeders()
                results["seeders"] = seeders_results

                # 8. Crear vistas de consulta
                self.logger.info("Creando vistas de consulta...")
                await self._create_diplomatic_views()

            self.logger.info("Despliegue de esquema completado")
            return results

        except Exception as e:
            self.logger.error(f"Error desplegando esquema: {str(e)}")
            return {"error": str(e), "success": False}

    def _generate_complete_prisma_schema(self) -> str:
        """Genera el esquema Prisma completo para SIAME"""
        return '''
// ============================================================================
// SIAME 2026v3 - Esquema Prisma Completo para Documentos Diplomáticos
// ============================================================================

generator client {
  provider = "prisma-client-js"
  binaryTargets = ["native", "linux-musl"]
}

datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

// ============================================================================
// USUARIOS Y AUTENTICACIÓN
// ============================================================================

model User {
  id                String              @id @default(uuid())
  email             String              @unique
  username          String              @unique
  firstName         String
  lastName          String
  phoneNumber       String?
  isActive          Boolean             @default(true)
  lastLoginAt       DateTime?
  passwordHash      String
  passwordSalt      String
  mfaEnabled        Boolean             @default(false)
  mfaSecret         String?

  // Información diplomática
  diplomaticId      String?             @unique
  position          String?
  department        String?
  embassy           String?
  country           String?

  // Configuración de seguridad
  securityClearance SecurityClearance   @default(PUBLICO)
  maxClassification DocumentClassification @default(PUBLICO)

  // Relaciones
  roles             UserRole[]
  permissions       UserPermission[]
  documents         DiplomaticDocument[]
  auditLogs         AuditLog[]
  sessions          UserSession[]

  // Metadatos
  createdAt         DateTime            @default(now())
  updatedAt         DateTime            @updatedAt
  createdBy         String?
  deletedAt         DateTime?

  @@map("users")
}

model Role {
  id          String       @id @default(uuid())
  name        String       @unique
  description String?
  level       Int          @default(0)

  // Permisos del rol
  permissions RolePermission[]
  users       UserRole[]

  createdAt   DateTime     @default(now())
  updatedAt   DateTime     @updatedAt

  @@map("roles")
}

model Permission {
  id          String           @id @default(uuid())
  name        String           @unique
  description String?
  resource    String
  action      String

  roles       RolePermission[]
  users       UserPermission[]

  createdAt   DateTime         @default(now())

  @@map("permissions")
}

model UserRole {
  id        String   @id @default(uuid())
  userId    String
  roleId    String
  grantedBy String?
  grantedAt DateTime @default(now())
  expiresAt DateTime?

  user      User     @relation(fields: [userId], references: [id])
  role      Role     @relation(fields: [roleId], references: [id])

  @@unique([userId, roleId])
  @@map("user_roles")
}

model UserPermission {
  id           String     @id @default(uuid())
  userId       String
  permissionId String
  grantedBy    String?
  grantedAt    DateTime   @default(now())
  expiresAt    DateTime?

  user         User       @relation(fields: [userId], references: [id])
  permission   Permission @relation(fields: [permissionId], references: [id])

  @@unique([userId, permissionId])
  @@map("user_permissions")
}

model RolePermission {
  id           String     @id @default(uuid())
  roleId       String
  permissionId String

  role         Role       @relation(fields: [roleId], references: [id])
  permission   Permission @relation(fields: [permissionId], references: [id])

  @@unique([roleId, permissionId])
  @@map("role_permissions")
}

model UserSession {
  id          String    @id @default(uuid())
  userId      String
  token       String    @unique
  ipAddress   String?
  userAgent   String?
  expiresAt   DateTime
  isActive    Boolean   @default(true)

  user        User      @relation(fields: [userId], references: [id])

  createdAt   DateTime  @default(now())
  updatedAt   DateTime  @updatedAt

  @@map("user_sessions")
}

// ============================================================================
// DOCUMENTOS DIPLOMÁTICOS
// ============================================================================

model DiplomaticDocument {
  id                    String                @id @default(uuid())
  documentNumber        String                @unique
  documentType          DocumentType
  classification        DocumentClassification
  title                 String
  description           String?

  // Metadatos del documento
  originalFileName      String?
  fileSize              Int?
  mimeType              String?
  azureBlobPath         String?
  azureFormRecognizerId String?

  // Datos extraídos del documento
  extractedData         Json?
  confidenceScore       Float?

  // Información diplomática
  originEmbassy         String?
  destinationEmbassy    String?
  diplomaticSeries      String?
  diplomaticNumber      String?
  subject               String?
  reference             String?

  // Fechas importantes
  documentDate          DateTime?
  receivedDate          DateTime?
  processedDate         DateTime?

  // Estado y workflow
  status                DocumentStatus        @default(PENDING)
  workflowStage         String?
  priority              DocumentPriority      @default(NORMAL)

  // Seguridad y acceso
  accessLevel           Int                   @default(1)
  isClassified          Boolean               @default(false)
  declassificationDate  DateTime?

  // Relaciones
  authorId              String
  author                User                  @relation(fields: [authorId], references: [id])

  tags                  DocumentTag[]
  attachments           DocumentAttachment[]
  versions              DocumentVersion[]
  authorizations        DocumentAuthorization[]

  // Metadatos de sistema
  createdAt             DateTime              @default(now())
  updatedAt             DateTime              @updatedAt
  deletedAt             DateTime?

  @@index([documentType])
  @@index([classification])
  @@index([status])
  @@index([documentDate])
  @@index([authorId])
  @@map("diplomatic_documents")
}

model DocumentVersion {
  id         String             @id @default(uuid())
  documentId String
  version    Int
  changes    String?
  changeType String

  document   DiplomaticDocument @relation(fields: [documentId], references: [id])

  createdAt  DateTime           @default(now())
  createdBy  String

  @@unique([documentId, version])
  @@map("document_versions")
}

model DocumentTag {
  id         String             @id @default(uuid())
  documentId String
  tag        String

  document   DiplomaticDocument @relation(fields: [documentId], references: [id])

  @@unique([documentId, tag])
  @@map("document_tags")
}

model DocumentAttachment {
  id           String             @id @default(uuid())
  documentId   String
  fileName     String
  fileSize     Int
  mimeType     String
  azureBlobPath String

  document     DiplomaticDocument @relation(fields: [documentId], references: [id])

  createdAt    DateTime           @default(now())

  @@map("document_attachments")
}

model DocumentAuthorization {
  id           String             @id @default(uuid())
  documentId   String
  userId       String
  accessType   AccessType
  grantedBy    String
  grantedAt    DateTime           @default(now())
  expiresAt    DateTime?
  reason       String?

  document     DiplomaticDocument @relation(fields: [documentId], references: [id])

  @@unique([documentId, userId])
  @@map("document_authorizations")
}

// ============================================================================
// AUDITORÍA Y LOGGING
// ============================================================================

model AuditLog {
  id            String          @id @default(uuid())
  tableName     String
  recordId      String
  action        AuditAction
  oldValues     Json?
  newValues     Json?

  // Información del usuario
  userId        String?
  user          User?           @relation(fields: [userId], references: [id])
  ipAddress     String?
  userAgent     String?

  // Metadatos
  timestamp     DateTime        @default(now())
  sessionId     String?

  @@index([tableName])
  @@index([recordId])
  @@index([action])
  @@index([timestamp])
  @@index([userId])
  @@map("audit_logs")
}

model SystemLog {
  id        String      @id @default(uuid())
  level     LogLevel
  message   String
  details   Json?
  source    String?

  timestamp DateTime    @default(now())

  @@index([level])
  @@index([timestamp])
  @@map("system_logs")
}

// ============================================================================
// CONFIGURACIÓN DEL SISTEMA
// ============================================================================

model SystemConfiguration {
  id          String   @id @default(uuid())
  category    String
  key         String   @unique
  value       String
  description String?
  isEncrypted Boolean  @default(false)

  createdAt   DateTime @default(now())
  updatedAt   DateTime @updatedAt

  @@map("system_configuration")
}

model Embassy {
  id          String   @id @default(uuid())
  name        String   @unique
  country     String
  code        String   @unique
  address     String?
  timezone    String?
  isActive    Boolean  @default(true)

  createdAt   DateTime @default(now())
  updatedAt   DateTime @updatedAt

  @@map("embassies")
}

// ============================================================================
// ENUMS
// ============================================================================

enum SecurityClearance {
  PUBLICO
  RESTRINGIDO
  CONFIDENCIAL
  SECRETO
  ALTO_SECRETO
}

enum DocumentClassification {
  PUBLICO
  RESTRINGIDO
  CONFIDENCIAL
  SECRETO
  ALTO_SECRETO
}

enum DocumentType {
  HOJA_REMISION_OGA
  HOJA_REMISION_PCO
  HOJA_REMISION_PRU
  GUIA_VALIJA_ENTRADA_ORD
  GUIA_VALIJA_ENTRADA_EXT
  GUIA_VALIJA_SALIDA_ORD
  GUIA_VALIJA_SALIDA_EXT
  NOTA_DIPLOMATICA
  DESPACHO
  MEMORANDUM
  CIRCULAR
  INFORME
}

enum DocumentStatus {
  PENDING
  PROCESSING
  PROCESSED
  APPROVED
  REJECTED
  ARCHIVED
  DELETED
}

enum DocumentPriority {
  LOW
  NORMAL
  HIGH
  URGENT
  CRITICAL
}

enum AccessType {
  READ
  WRITE
  DELETE
  SHARE
  ADMIN
}

enum AuditAction {
  CREATE
  READ
  UPDATE
  DELETE
  LOGIN
  LOGOUT
  EXPORT
  PRINT
  SHARE
}

enum LogLevel {
  DEBUG
  INFO
  WARN
  ERROR
  FATAL
}
'''

    def _generate_initial_migrations(self) -> List[str]:
        """Genera migraciones iniciales"""
        migrations = []

        # Migración 1: Crear extensiones PostgreSQL
        migrations.append('''
-- Migration: 001_create_extensions.sql
-- Crear extensiones necesarias para PostgreSQL

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "unaccent";

-- Función para generar UUID v4
CREATE OR REPLACE FUNCTION generate_uuid_v4()
RETURNS UUID AS $$
BEGIN
    RETURN uuid_generate_v4();
END;
$$ LANGUAGE plpgsql;

-- Función para hash de passwords
CREATE OR REPLACE FUNCTION hash_password(password TEXT)
RETURNS TEXT AS $$
BEGIN
    RETURN crypt(password, gen_salt('bf', 10));
END;
$$ LANGUAGE plpgsql;

-- Función para verificar passwords
CREATE OR REPLACE FUNCTION verify_password(password TEXT, hash TEXT)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN hash = crypt(password, hash);
END;
$$ LANGUAGE plpgsql;
''')

        # Migración 2: Configurar Row Level Security
        migrations.append('''
-- Migration: 002_setup_rls.sql
-- Configurar Row Level Security para todos los modelos

-- Habilitar RLS en tablas principales
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE diplomatic_documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE document_authorizations ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;

-- Crear función para obtener el usuario actual
CREATE OR REPLACE FUNCTION current_user_id()
RETURNS UUID AS $$
BEGIN
    RETURN COALESCE(
        NULLIF(current_setting('app.user_id', true), '')::UUID,
        '00000000-0000-0000-0000-000000000000'::UUID
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Crear función para verificar clearance de seguridad
CREATE OR REPLACE FUNCTION has_security_clearance(required_level TEXT)
RETURNS BOOLEAN AS $$
DECLARE
    user_clearance TEXT;
    clearance_levels TEXT[] := ARRAY['PUBLICO', 'RESTRINGIDO', 'CONFIDENCIAL', 'SECRETO', 'ALTO_SECRETO'];
    user_level_index INT;
    required_level_index INT;
BEGIN
    -- Obtener clearance del usuario actual
    SELECT security_clearance INTO user_clearance
    FROM users
    WHERE id = current_user_id();

    -- Si no se encuentra usuario, denegar acceso
    IF user_clearance IS NULL THEN
        RETURN FALSE;
    END IF;

    -- Obtener índices de niveles
    SELECT array_position(clearance_levels, user_clearance) INTO user_level_index;
    SELECT array_position(clearance_levels, required_level) INTO required_level_index;

    -- Verificar si el usuario tiene clearance suficiente
    RETURN user_level_index >= required_level_index;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
''')

        # Migración 3: Crear políticas RLS
        migrations.append('''
-- Migration: 003_create_rls_policies.sql
-- Crear políticas Row Level Security

-- Políticas para usuarios
CREATE POLICY user_select_policy ON users
    FOR SELECT
    USING (
        id = current_user_id() OR
        has_security_clearance('RESTRINGIDO')
    );

CREATE POLICY user_update_policy ON users
    FOR UPDATE
    USING (
        id = current_user_id() OR
        has_security_clearance('CONFIDENCIAL')
    );

-- Políticas para documentos diplomáticos
CREATE POLICY document_select_policy ON diplomatic_documents
    FOR SELECT
    USING (
        -- El autor puede ver sus documentos
        author_id = current_user_id() OR
        -- Usuario tiene clearance para la clasificación
        has_security_clearance(classification::TEXT) OR
        -- Usuario tiene autorización específica
        EXISTS (
            SELECT 1 FROM document_authorizations da
            WHERE da.document_id = id
            AND da.user_id = current_user_id()
            AND (da.expires_at IS NULL OR da.expires_at > NOW())
        )
    );

CREATE POLICY document_insert_policy ON diplomatic_documents
    FOR INSERT
    WITH CHECK (
        author_id = current_user_id() AND
        has_security_clearance(classification::TEXT)
    );

CREATE POLICY document_update_policy ON diplomatic_documents
    FOR UPDATE
    USING (
        author_id = current_user_id() OR
        EXISTS (
            SELECT 1 FROM document_authorizations da
            WHERE da.document_id = id
            AND da.user_id = current_user_id()
            AND da.access_type IN ('WRITE', 'ADMIN')
            AND (da.expires_at IS NULL OR da.expires_at > NOW())
        )
    );

-- Políticas para autorizaciones de documentos
CREATE POLICY authorization_select_policy ON document_authorizations
    FOR SELECT
    USING (
        user_id = current_user_id() OR
        granted_by = current_user_id() OR
        has_security_clearance('CONFIDENCIAL')
    );

-- Políticas para logs de auditoría
CREATE POLICY audit_select_policy ON audit_logs
    FOR SELECT
    USING (
        user_id = current_user_id() OR
        has_security_clearance('SECRETO')
    );

CREATE POLICY audit_insert_policy ON audit_logs
    FOR INSERT
    WITH CHECK (true); -- Los triggers pueden insertar libremente
''')

        return migrations

    def _generate_audit_triggers(self) -> List[str]:
        """Genera triggers de auditoría automática"""
        triggers = []

        # Función de auditoría genérica
        triggers.append('''
-- Trigger function para auditoría automática
CREATE OR REPLACE FUNCTION audit_trigger_function()
RETURNS TRIGGER AS $$
DECLARE
    audit_action TEXT;
    old_values JSONB;
    new_values JSONB;
BEGIN
    -- Determinar acción
    IF TG_OP = 'DELETE' THEN
        audit_action := 'DELETE';
        old_values := to_jsonb(OLD);
        new_values := NULL;
    ELSIF TG_OP = 'UPDATE' THEN
        audit_action := 'UPDATE';
        old_values := to_jsonb(OLD);
        new_values := to_jsonb(NEW);
    ELSIF TG_OP = 'INSERT' THEN
        audit_action := 'CREATE';
        old_values := NULL;
        new_values := to_jsonb(NEW);
    END IF;

    -- Insertar registro de auditoría
    INSERT INTO audit_logs (
        table_name,
        record_id,
        action,
        old_values,
        new_values,
        user_id,
        ip_address,
        user_agent,
        session_id
    ) VALUES (
        TG_TABLE_NAME,
        COALESCE(NEW.id, OLD.id),
        audit_action::audit_action,
        old_values,
        new_values,
        current_user_id(),
        current_setting('app.client_ip', true),
        current_setting('app.user_agent', true),
        current_setting('app.session_id', true)
    );

    -- Retornar el registro apropiado
    IF TG_OP = 'DELETE' THEN
        RETURN OLD;
    ELSE
        RETURN NEW;
    END IF;
END;
$$ LANGUAGE plpgsql;
''')

        # Triggers específicos para cada tabla
        triggers.append('''
-- Triggers de auditoría para todas las tablas importantes
CREATE TRIGGER users_audit_trigger
    AFTER INSERT OR UPDATE OR DELETE ON users
    FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();

CREATE TRIGGER diplomatic_documents_audit_trigger
    AFTER INSERT OR UPDATE OR DELETE ON diplomatic_documents
    FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();

CREATE TRIGGER document_authorizations_audit_trigger
    AFTER INSERT OR UPDATE OR DELETE ON document_authorizations
    FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();

CREATE TRIGGER user_roles_audit_trigger
    AFTER INSERT OR UPDATE OR DELETE ON user_roles
    FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();

CREATE TRIGGER user_permissions_audit_trigger
    AFTER INSERT OR UPDATE OR DELETE ON user_permissions
    FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();
''')

        # Trigger para actualizar timestamps
        triggers.append('''
-- Función para actualizar updated_at automáticamente
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Aplicar trigger a todas las tablas con updated_at
CREATE TRIGGER users_update_timestamp
    BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER diplomatic_documents_update_timestamp
    BEFORE UPDATE ON diplomatic_documents
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER roles_update_timestamp
    BEFORE UPDATE ON roles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER system_configuration_update_timestamp
    BEFORE UPDATE ON system_configuration
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER embassies_update_timestamp
    BEFORE UPDATE ON embassies
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();
''')

        return triggers

    def _generate_rls_policies(self) -> List[str]:
        """Genera políticas RLS adicionales"""
        policies = []

        # Políticas avanzadas para documentos
        policies.append('''
-- Políticas RLS avanzadas para documentos diplomáticos

-- Política para documentos por nivel de acceso temporal
CREATE POLICY document_temporal_access ON diplomatic_documents
    FOR SELECT
    USING (
        -- Documentos públicos siempre visibles
        classification = 'PUBLICO' OR
        -- Documentos con fecha de declasificación pasada
        (declassification_date IS NOT NULL AND declassification_date <= NOW()) OR
        -- Acceso normal por clearance
        has_security_clearance(classification::TEXT)
    );

-- Política para prevenir escalación de privilegios
CREATE POLICY document_classification_limit ON diplomatic_documents
    FOR INSERT
    WITH CHECK (
        -- Solo puede crear documentos con clasificación <= a su clearance
        has_security_clearance(classification::TEXT)
    );

-- Política para attachments basada en documento padre
CREATE POLICY attachment_access_policy ON document_attachments
    FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM diplomatic_documents dd
            WHERE dd.id = document_id
            AND (
                dd.author_id = current_user_id() OR
                has_security_clearance(dd.classification::TEXT) OR
                EXISTS (
                    SELECT 1 FROM document_authorizations da
                    WHERE da.document_id = dd.id
                    AND da.user_id = current_user_id()
                    AND (da.expires_at IS NULL OR da.expires_at > NOW())
                )
            )
        )
    );
''')

        # Políticas para sessiones y autenticación
        policies.append('''
-- Políticas para sesiones de usuario
CREATE POLICY session_owner_policy ON user_sessions
    FOR ALL
    USING (user_id = current_user_id());

-- Política para logs del sistema (solo administradores)
CREATE POLICY system_log_admin_policy ON system_logs
    FOR SELECT
    USING (has_security_clearance('SECRETO'));

-- Política para configuración del sistema (solo administradores)
CREATE POLICY system_config_admin_policy ON system_configuration
    FOR ALL
    USING (has_security_clearance('ALTO_SECRETO'));
''')

        return policies

    def _generate_initial_seeders(self) -> List[str]:
        """Genera seeders iniciales"""
        seeders = []

        # Seeder para roles diplomáticos
        seeders.append('''
-- Seeder: Roles diplomáticos iniciales
INSERT INTO roles (id, name, description, level) VALUES
    ('00000000-0000-0000-0000-000000000001', 'EMBAJADOR', 'Embajador - Máximo nivel diplomático', 10),
    ('00000000-0000-0000-0000-000000000002', 'MINISTRO_CONSEJERO', 'Ministro Consejero', 9),
    ('00000000-0000-0000-0000-000000000003', 'CONSEJERO', 'Consejero', 8),
    ('00000000-0000-0000-0000-000000000004', 'PRIMER_SECRETARIO', 'Primer Secretario', 7),
    ('00000000-0000-0000-0000-000000000005', 'SEGUNDO_SECRETARIO', 'Segundo Secretario', 6),
    ('00000000-0000-0000-0000-000000000006', 'TERCER_SECRETARIO', 'Tercer Secretario', 5),
    ('00000000-0000-0000-0000-000000000007', 'AGREGADO', 'Agregado', 4),
    ('00000000-0000-0000-0000-000000000008', 'FUNCIONARIO_ADMINISTRATIVO', 'Funcionario Administrativo', 3),
    ('00000000-0000-0000-0000-000000000009', 'CONSULTOR_EXTERNO', 'Consultor Externo', 2),
    ('00000000-0000-0000-0000-000000000010', 'INVITADO', 'Invitado', 1)
ON CONFLICT (id) DO NOTHING;
''')

        # Seeder para permisos
        seeders.append('''
-- Seeder: Permisos del sistema
INSERT INTO permissions (id, name, description, resource, action) VALUES
    ('10000000-0000-0000-0000-000000000001', 'DOCUMENT_READ', 'Leer documentos', 'document', 'read'),
    ('10000000-0000-0000-0000-000000000002', 'DOCUMENT_WRITE', 'Escribir documentos', 'document', 'write'),
    ('10000000-0000-0000-0000-000000000003', 'DOCUMENT_DELETE', 'Eliminar documentos', 'document', 'delete'),
    ('10000000-0000-0000-0000-000000000004', 'DOCUMENT_SHARE', 'Compartir documentos', 'document', 'share'),
    ('10000000-0000-0000-0000-000000000005', 'DOCUMENT_ADMIN', 'Administrar documentos', 'document', 'admin'),
    ('10000000-0000-0000-0000-000000000006', 'USER_READ', 'Leer usuarios', 'user', 'read'),
    ('10000000-0000-0000-0000-000000000007', 'USER_WRITE', 'Escribir usuarios', 'user', 'write'),
    ('10000000-0000-0000-0000-000000000008', 'USER_DELETE', 'Eliminar usuarios', 'user', 'delete'),
    ('10000000-0000-0000-0000-000000000009', 'USER_ADMIN', 'Administrar usuarios', 'user', 'admin'),
    ('10000000-0000-0000-0000-000000000010', 'SYSTEM_ADMIN', 'Administrar sistema', 'system', 'admin'),
    ('10000000-0000-0000-0000-000000000011', 'AUDIT_READ', 'Leer auditoría', 'audit', 'read'),
    ('10000000-0000-0000-0000-000000000012', 'CLASSIFICATION_DECLASSIFY', 'Declasificar documentos', 'classification', 'declassify')
ON CONFLICT (id) DO NOTHING;
''')

        # Seeder para asignación de permisos a roles
        seeders.append('''
-- Seeder: Asignación de permisos a roles
INSERT INTO role_permissions (id, role_id, permission_id) VALUES
    -- Embajador: Todos los permisos
    ('20000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000001', '10000000-0000-0000-0000-000000000001'),
    ('20000000-0000-0000-0000-000000000002', '00000000-0000-0000-0000-000000000001', '10000000-0000-0000-0000-000000000002'),
    ('20000000-0000-0000-0000-000000000003', '00000000-0000-0000-0000-000000000001', '10000000-0000-0000-0000-000000000003'),
    ('20000000-0000-0000-0000-000000000004', '00000000-0000-0000-0000-000000000001', '10000000-0000-0000-0000-000000000004'),
    ('20000000-0000-0000-0000-000000000005', '00000000-0000-0000-0000-000000000001', '10000000-0000-0000-0000-000000000005'),
    ('20000000-0000-0000-0000-000000000006', '00000000-0000-0000-0000-000000000001', '10000000-0000-0000-0000-000000000006'),
    ('20000000-0000-0000-0000-000000000007', '00000000-0000-0000-0000-000000000001', '10000000-0000-0000-0000-000000000007'),
    ('20000000-0000-0000-0000-000000000008', '00000000-0000-0000-0000-000000000001', '10000000-0000-0000-0000-000000000008'),
    ('20000000-0000-0000-0000-000000000009', '00000000-0000-0000-0000-000000000001', '10000000-0000-0000-0000-000000000009'),
    ('20000000-0000-0000-0000-000000000010', '00000000-0000-0000-0000-000000000001', '10000000-0000-0000-0000-000000000010'),
    ('20000000-0000-0000-0000-000000000011', '00000000-0000-0000-0000-000000000001', '10000000-0000-0000-0000-000000000011'),
    ('20000000-0000-0000-0000-000000000012', '00000000-0000-0000-0000-000000000001', '10000000-0000-0000-0000-000000000012'),

    -- Ministro Consejero: Permisos administrativos
    ('20000000-0000-0000-0000-000000000013', '00000000-0000-0000-0000-000000000002', '10000000-0000-0000-0000-000000000001'),
    ('20000000-0000-0000-0000-000000000014', '00000000-0000-0000-0000-000000000002', '10000000-0000-0000-0000-000000000002'),
    ('20000000-0000-0000-0000-000000000015', '00000000-0000-0000-0000-000000000002', '10000000-0000-0000-0000-000000000004'),
    ('20000000-0000-0000-0000-000000000016', '00000000-0000-0000-0000-000000000002', '10000000-0000-0000-0000-000000000005'),
    ('20000000-0000-0000-0000-000000000017', '00000000-0000-0000-0000-000000000002', '10000000-0000-0000-0000-000000000006'),
    ('20000000-0000-0000-0000-000000000018', '00000000-0000-0000-0000-000000000002', '10000000-0000-0000-0000-000000000011'),

    -- Consejero: Permisos de gestión documental
    ('20000000-0000-0000-0000-000000000019', '00000000-0000-0000-0000-000000000003', '10000000-0000-0000-0000-000000000001'),
    ('20000000-0000-0000-0000-000000000020', '00000000-0000-0000-0000-000000000003', '10000000-0000-0000-0000-000000000002'),
    ('20000000-0000-0000-0000-000000000021', '00000000-0000-0000-0000-000000000003', '10000000-0000-0000-0000-000000000004'),
    ('20000000-0000-0000-0000-000000000022', '00000000-0000-0000-0000-000000000003', '10000000-0000-0000-0000-000000000006'),

    -- Secretarios: Permisos básicos
    ('20000000-0000-0000-0000-000000000023', '00000000-0000-0000-0000-000000000004', '10000000-0000-0000-0000-000000000001'),
    ('20000000-0000-0000-0000-000000000024', '00000000-0000-0000-0000-000000000004', '10000000-0000-0000-0000-000000000002'),
    ('20000000-0000-0000-0000-000000000025', '00000000-0000-0000-0000-000000000005', '10000000-0000-0000-0000-000000000001'),
    ('20000000-0000-0000-0000-000000000026', '00000000-0000-0000-0000-000000000005', '10000000-0000-0000-0000-000000000002'),
    ('20000000-0000-0000-0000-000000000027', '00000000-0000-0000-0000-000000000006', '10000000-0000-0000-0000-000000000001'),
    ('20000000-0000-0000-0000-000000000028', '00000000-0000-0000-0000-000000000006', '10000000-0000-0000-0000-000000000002'),

    -- Invitado: Solo lectura de documentos públicos
    ('20000000-0000-0000-0000-000000000029', '00000000-0000-0000-0000-000000000010', '10000000-0000-0000-0000-000000000001')
ON CONFLICT (id) DO NOTHING;
''')

        # Seeder para embajadas
        seeders.append('''
-- Seeder: Embajadas iniciales
INSERT INTO embassies (id, name, country, code, address, timezone, is_active) VALUES
    ('30000000-0000-0000-0000-000000000001', 'Embajada de España en Francia', 'Francia', 'ESP-FR', '22 Avenue Marceau, 75008 París', 'Europe/Paris', true),
    ('30000000-0000-0000-0000-000000000002', 'Embajada de España en Estados Unidos', 'Estados Unidos', 'ESP-US', '2375 Pennsylvania Avenue NW, Washington DC', 'America/New_York', true),
    ('30000000-0000-0000-0000-000000000003', 'Embajada de España en Reino Unido', 'Reino Unido', 'ESP-UK', '39 Chesham Place, Londres SW1X 8SB', 'Europe/London', true),
    ('30000000-0000-0000-0000-000000000004', 'Embajada de España en Alemania', 'Alemania', 'ESP-DE', 'Lichtensteinallee 1, 10787 Berlín', 'Europe/Berlin', true),
    ('30000000-0000-0000-0000-000000000005', 'Embajada de España en Italia', 'Italia', 'ESP-IT', 'Palazzo di Spagna, Piazza di Spagna 57, Roma', 'Europe/Rome', true)
ON CONFLICT (id) DO NOTHING;
''')

        # Seeder para usuario administrador inicial
        seeders.append('''
-- Seeder: Usuario administrador inicial
INSERT INTO users (
    id, email, username, first_name, last_name, phone_number,
    is_active, password_hash, password_salt, mfa_enabled,
    diplomatic_id, position, department, embassy, country,
    security_clearance, max_classification
) VALUES (
    '40000000-0000-0000-0000-000000000001',
    'admin@siame.gov.es',
    'admin',
    'Administrador',
    'Sistema',
    '+34-900-000-000',
    true,
    hash_password('Admin123!'),
    gen_salt('bf', 10),
    false,
    'ADM-001',
    'Administrador del Sistema',
    'Tecnología',
    'Ministerio de Asuntos Exteriores',
    'España',
    'ALTO_SECRETO',
    'ALTO_SECRETO'
) ON CONFLICT (id) DO NOTHING;

-- Asignar rol de embajador al administrador
INSERT INTO user_roles (id, user_id, role_id, granted_by, granted_at) VALUES (
    '50000000-0000-0000-0000-000000000001',
    '40000000-0000-0000-0000-000000000001',
    '00000000-0000-0000-0000-000000000001',
    '40000000-0000-0000-0000-000000000001',
    NOW()
) ON CONFLICT (user_id, role_id) DO NOTHING;
''')

        # Seeder para configuración del sistema
        seeders.append('''
-- Seeder: Configuración inicial del sistema
INSERT INTO system_configuration (id, category, key, value, description, is_encrypted) VALUES
    ('60000000-0000-0000-0000-000000000001', 'SECURITY', 'PASSWORD_MIN_LENGTH', '8', 'Longitud mínima de contraseña', false),
    ('60000000-0000-0000-0000-000000000002', 'SECURITY', 'PASSWORD_REQUIRE_UPPERCASE', 'true', 'Requerir mayúsculas en contraseña', false),
    ('60000000-0000-0000-0000-000000000003', 'SECURITY', 'PASSWORD_REQUIRE_LOWERCASE', 'true', 'Requerir minúsculas en contraseña', false),
    ('60000000-0000-0000-0000-000000000004', 'SECURITY', 'PASSWORD_REQUIRE_NUMBERS', 'true', 'Requerir números en contraseña', false),
    ('60000000-0000-0000-0000-000000000005', 'SECURITY', 'PASSWORD_REQUIRE_SPECIAL', 'true', 'Requerir caracteres especiales en contraseña', false),
    ('60000000-0000-0000-0000-000000000006', 'SECURITY', 'SESSION_TIMEOUT_MINUTES', '60', 'Tiempo de expiración de sesión en minutos', false),
    ('60000000-0000-0000-0000-000000000007', 'SECURITY', 'MAX_LOGIN_ATTEMPTS', '5', 'Máximo número de intentos de login', false),
    ('60000000-0000-0000-0000-000000000008', 'SECURITY', 'LOCKOUT_DURATION_MINUTES', '30', 'Duración de bloqueo tras intentos fallidos', false),
    ('60000000-0000-0000-0000-000000000009', 'DOCUMENTS', 'MAX_FILE_SIZE_MB', '50', 'Tamaño máximo de archivo en MB', false),
    ('60000000-0000-0000-0000-000000000010', 'DOCUMENTS', 'ALLOWED_FILE_TYPES', 'pdf,doc,docx,txt,jpg,png', 'Tipos de archivo permitidos', false),
    ('60000000-0000-0000-0000-000000000011', 'DOCUMENTS', 'AUTO_CLASSIFICATION', 'true', 'Clasificación automática habilitada', false),
    ('60000000-0000-0000-0000-000000000012', 'DOCUMENTS', 'RETENTION_YEARS', '25', 'Años de retención de documentos', false),
    ('60000000-0000-0000-0000-000000000013', 'AZURE', 'FORM_RECOGNIZER_ENDPOINT', '', 'Endpoint de Azure Form Recognizer', true),
    ('60000000-0000-0000-0000-000000000014', 'AZURE', 'STORAGE_ACCOUNT_NAME', '', 'Nombre de cuenta de Azure Storage', false),
    ('60000000-0000-0000-0000-000000000015', 'AZURE', 'KEY_VAULT_URL', '', 'URL de Azure Key Vault', false)
ON CONFLICT (key) DO NOTHING;
''')

        return seeders

    async def _create_initial_schema(self) -> Dict[str, Any]:
        """Crea el esquema inicial de base de datos"""
        try:
            async with self.connection_pool.acquire() as connection:
                # Escribir esquema Prisma a archivo
                schema_file = Path("prisma/schema.prisma")
                schema_file.parent.mkdir(exist_ok=True)
                schema_file.write_text(self.prisma_schema)

                self.logger.info("Esquema Prisma generado en prisma/schema.prisma")

                return {
                    "success": True,
                    "schema_file": str(schema_file),
                    "tables_created": "via_prisma_migration"
                }

        except Exception as e:
            self.logger.error(f"Error creando esquema inicial: {str(e)}")
            return {"success": False, "error": str(e)}

    async def _execute_migrations(self) -> List[MigrationResult]:
        """Ejecuta las migraciones de base de datos"""
        results = []

        try:
            async with self.connection_pool.acquire() as connection:
                for i, migration_sql in enumerate(self.initial_migrations, 1):
                    try:
                        migration_name = f"00{i}_initial_migration"

                        await connection.execute(migration_sql)

                        result = MigrationResult(
                            success=True,
                            migration_name=migration_name,
                            executed_at=datetime.utcnow(),
                            sql_executed=migration_sql[:500] + "..." if len(migration_sql) > 500 else migration_sql
                        )
                        results.append(result)

                        self.logger.info(f"Migración {migration_name} ejecutada exitosamente")

                    except Exception as e:
                        result = MigrationResult(
                            success=False,
                            migration_name=f"00{i}_initial_migration",
                            executed_at=datetime.utcnow(),
                            error_message=str(e)
                        )
                        results.append(result)
                        self.logger.error(f"Error en migración {i}: {str(e)}")

        except Exception as e:
            self.logger.error(f"Error ejecutando migraciones: {str(e)}")

        return results

    async def _setup_row_level_security(self) -> Dict[str, Any]:
        """Configura Row Level Security"""
        try:
            async with self.connection_pool.acquire() as connection:
                policies_created = 0

                for policy_sql in self.rls_policies:
                    try:
                        await connection.execute(policy_sql)
                        policies_created += 1
                    except Exception as e:
                        self.logger.error(f"Error creando política RLS: {str(e)}")

                return {
                    "success": True,
                    "policies_created": policies_created,
                    "rls_enabled": True
                }

        except Exception as e:
            self.logger.error(f"Error configurando RLS: {str(e)}")
            return {"success": False, "error": str(e)}

    async def _setup_audit_system(self) -> Dict[str, Any]:
        """Configura el sistema de auditoría automática"""
        try:
            async with self.connection_pool.acquire() as connection:
                triggers_created = 0

                for trigger_sql in self.audit_triggers:
                    try:
                        await connection.execute(trigger_sql)
                        triggers_created += 1
                    except Exception as e:
                        self.logger.error(f"Error creando trigger de auditoría: {str(e)}")

                return {
                    "success": True,
                    "triggers_created": triggers_created,
                    "audit_enabled": True
                }

        except Exception as e:
            self.logger.error(f"Error configurando auditoría: {str(e)}")
            return {"success": False, "error": str(e)}

    async def _create_optimized_indexes(self) -> Dict[str, Any]:
        """Crea índices optimizados para consultas diplomáticas"""
        indexes = [
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_documents_classification_date ON diplomatic_documents(classification, document_date);",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_documents_embassy_type ON diplomatic_documents(origin_embassy, document_type);",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_documents_status_priority ON diplomatic_documents(status, priority);",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_documents_extracted_data_gin ON diplomatic_documents USING gin(extracted_data);",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_audit_logs_timestamp_user ON audit_logs(timestamp, user_id);",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_audit_logs_table_record ON audit_logs(table_name, record_id);",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_diplomatic_id ON users(diplomatic_id);",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_security_clearance ON users(security_clearance);",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_authorizations_expires ON document_authorizations(expires_at) WHERE expires_at IS NOT NULL;",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_sessions_expires ON user_sessions(expires_at);",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_documents_fulltext ON diplomatic_documents USING gin(to_tsvector('spanish', title || ' ' || COALESCE(description, '') || ' ' || COALESCE(subject, '')));"
        ]

        try:
            async with self.connection_pool.acquire() as connection:
                indexes_created = 0

                for index_sql in indexes:
                    try:
                        await connection.execute(index_sql)
                        indexes_created += 1
                        self.logger.info(f"Índice creado: {index_sql.split()[5]}")
                    except Exception as e:
                        self.logger.error(f"Error creando índice: {str(e)}")

                return {
                    "success": True,
                    "indexes_created": indexes_created
                }

        except Exception as e:
            self.logger.error(f"Error creando índices: {str(e)}")
            return {"success": False, "error": str(e)}

    async def _setup_triggers(self) -> Dict[str, Any]:
        """Configura triggers adicionales del sistema"""
        try:
            # Los triggers ya se configuraron en _setup_audit_system
            return {
                "success": True,
                "message": "Triggers configurados en setup_audit_system"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _execute_seeders(self) -> List[Dict[str, Any]]:
        """Ejecuta los seeders iniciales"""
        results = []

        try:
            async with self.connection_pool.acquire() as connection:
                for i, seeder_sql in enumerate(self.seeders, 1):
                    try:
                        seeder_name = f"seeder_{i:03d}"

                        await connection.execute(seeder_sql)

                        results.append({
                            "success": True,
                            "seeder_name": seeder_name,
                            "executed_at": datetime.utcnow().isoformat()
                        })

                        self.logger.info(f"Seeder {seeder_name} ejecutado exitosamente")

                    except Exception as e:
                        results.append({
                            "success": False,
                            "seeder_name": f"seeder_{i:03d}",
                            "error": str(e)
                        })
                        self.logger.error(f"Error en seeder {i}: {str(e)}")

        except Exception as e:
            self.logger.error(f"Error ejecutando seeders: {str(e)}")

        return results

    async def _create_diplomatic_views(self) -> Dict[str, Any]:
        """Crea vistas especializadas para consultas diplomáticas"""
        views = [
            '''
            CREATE OR REPLACE VIEW v_document_summary AS
            SELECT
                dd.id,
                dd.document_number,
                dd.document_type,
                dd.classification,
                dd.title,
                dd.document_date,
                dd.status,
                dd.priority,
                u.first_name || ' ' || u.last_name as author_name,
                u.diplomatic_id as author_diplomatic_id,
                dd.origin_embassy,
                dd.destination_embassy
            FROM diplomatic_documents dd
            JOIN users u ON dd.author_id = u.id
            WHERE dd.deleted_at IS NULL;
            ''',
            '''
            CREATE OR REPLACE VIEW v_user_permissions AS
            SELECT
                u.id as user_id,
                u.email,
                u.first_name || ' ' || u.last_name as full_name,
                u.security_clearance,
                r.name as role_name,
                r.level as role_level,
                p.name as permission_name,
                p.resource,
                p.action
            FROM users u
            LEFT JOIN user_roles ur ON u.id = ur.user_id
            LEFT JOIN roles r ON ur.role_id = r.id
            LEFT JOIN role_permissions rp ON r.id = rp.role_id
            LEFT JOIN permissions p ON rp.permission_id = p.id
            WHERE u.is_active = true;
            ''',
            '''
            CREATE OR REPLACE VIEW v_audit_summary AS
            SELECT
                al.id,
                al.table_name,
                al.record_id,
                al.action,
                al.timestamp,
                u.first_name || ' ' || u.last_name as user_name,
                u.email as user_email,
                al.ip_address
            FROM audit_logs al
            LEFT JOIN users u ON al.user_id = u.id
            ORDER BY al.timestamp DESC;
            '''
        ]

        try:
            async with self.connection_pool.acquire() as connection:
                views_created = 0

                for view_sql in views:
                    try:
                        await connection.execute(view_sql)
                        views_created += 1
                    except Exception as e:
                        self.logger.error(f"Error creando vista: {str(e)}")

                return {
                    "success": True,
                    "views_created": views_created
                }

        except Exception as e:
            self.logger.error(f"Error creando vistas: {str(e)}")
            return {"success": False, "error": str(e)}

    async def generate_prisma_client(self) -> Dict[str, Any]:
        """Genera el cliente Prisma para la aplicación"""
        try:
            # Crear directorio prisma si no existe
            prisma_dir = Path("prisma")
            prisma_dir.mkdir(exist_ok=True)

            # Escribir archivo schema.prisma
            schema_file = prisma_dir / "schema.prisma"
            schema_file.write_text(self.prisma_schema)

            # Generar cliente Prisma
            result = subprocess.run(
                ["npx", "prisma", "generate"],
                capture_output=True,
                text=True,
                cwd="."
            )

            if result.returncode == 0:
                return {
                    "success": True,
                    "schema_file": str(schema_file),
                    "client_generated": True,
                    "output": result.stdout
                }
            else:
                return {
                    "success": False,
                    "error": result.stderr,
                    "schema_file": str(schema_file)
                }

        except Exception as e:
            self.logger.error(f"Error generando cliente Prisma: {str(e)}")
            return {"success": False, "error": str(e)}

    async def backup_database(self, backup_name: Optional[str] = None) -> Dict[str, Any]:
        """Crea un backup de la base de datos"""
        try:
            if not backup_name:
                backup_name = f"siame_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            backup_file = Path(f"backups/{backup_name}.sql")
            backup_file.parent.mkdir(exist_ok=True)

            # Usar pg_dump para crear backup
            result = subprocess.run([
                "pg_dump",
                self.config.connection_string,
                "-f", str(backup_file),
                "--verbose"
            ], capture_output=True, text=True)

            if result.returncode == 0:
                return {
                    "success": True,
                    "backup_file": str(backup_file),
                    "backup_size": backup_file.stat().st_size if backup_file.exists() else 0
                }
            else:
                return {
                    "success": False,
                    "error": result.stderr
                }

        except Exception as e:
            self.logger.error(f"Error creando backup: {str(e)}")
            return {"success": False, "error": str(e)}

    async def _handle_message(self, message: Message):
        """Maneja mensajes del message bus"""
        try:
            if message.type == MessageType.TASK:
                await self._process_task(message)
            elif message.type == MessageType.REQUEST:
                await self._process_request(message)

        except Exception as e:
            self.logger.error(f"Error procesando mensaje: {str(e)}")
            await self._send_error_response(message, str(e))

    async def _process_task(self, message: Message):
        """Procesa tareas específicas de base de datos"""
        task_type = message.data.get("task_type")

        task_handlers = {
            "deploy_schema": self.deploy_complete_database_schema,
            "generate_client": self.generate_prisma_client,
            "backup": self.backup_database,
            "migrate": self._execute_migrations,
            "seed": self._execute_seeders
        }

        handler = task_handlers.get(task_type)
        if handler:
            result = await handler()
            await self._send_response(message, result)
        else:
            await self._send_error_response(message, f"Tipo de tarea no soportado: {task_type}")

    async def _send_response(self, original_message: Message, result: Any):
        """Envía respuesta exitosa"""
        response = Message(
            id=str(uuid.uuid4()),
            type=MessageType.RESPONSE,
            sender=self.agent_id,
            recipient=original_message.sender,
            data={
                "status": "success",
                "result": result,
                "original_message_id": original_message.id
            }
        )
        await self.message_bus.publish("responses", response)

    async def _send_error_response(self, original_message: Message, error: str):
        """Envía respuesta de error"""
        response = Message(
            id=str(uuid.uuid4()),
            type=MessageType.ERROR,
            sender=self.agent_id,
            recipient=original_message.sender,
            data={
                "status": "error",
                "error": error,
                "original_message_id": original_message.id
            }
        )
        await self.message_bus.publish("responses", response)

    async def get_agent_status(self) -> Dict[str, Any]:
        """Obtiene el estado del agente"""
        return {
            "agent_id": self.agent_id,
            "agent_type": "Database Specialist",
            "is_initialized": self.is_initialized,
            "database_connected": self.connection_pool is not None,
            "config": {
                "host": self.config.host,
                "port": self.config.port,
                "database": self.config.database,
                "max_connections": self.config.max_connections
            },
            "features": {
                "row_level_security": True,
                "audit_triggers": True,
                "diplomatic_schema": True,
                "prisma_integration": True
            }
        }

    async def shutdown(self):
        """Cierra conexiones y limpia recursos"""
        try:
            if self.connection_pool:
                await self.connection_pool.close()

            await self.message_bus.unsubscribe("database.*")
            self.logger.info("Database Specialist Agent cerrado exitosamente")

        except Exception as e:
            self.logger.error(f"Error cerrando Database Specialist: {str(e)}")


# Función de utilidad para crear una instancia del agente
async def create_database_specialist(config: Optional[DatabaseConfig] = None) -> DatabaseSpecialist:
    """Crea y inicializa una instancia de Database Specialist"""
    agent = DatabaseSpecialist(config)

    if await agent.initialize():
        return agent
    else:
        raise RuntimeError("No se pudo inicializar Database Specialist Agent")


# Ejemplo de uso
if __name__ == "__main__":
    async def main():
        logging.basicConfig(level=logging.INFO)

        # Configuración de base de datos
        db_config = DatabaseConfig(
            host="localhost",
            port=5432,
            database="siame_dev",
            username="siame_user",
            password="siame_password"
        )

        try:
            # Crear agente
            agent = await create_database_specialist(db_config)

            # Desplegar esquema completo
            print("🚀 Desplegando esquema completo de base de datos...")
            deployment_result = await agent.deploy_complete_database_schema()

            print("📊 Resultados del despliegue:")
            for component, result in deployment_result.items():
                if isinstance(result, dict) and "success" in result:
                    status = "✅" if result["success"] else "❌"
                    print(f"  {status} {component}")
                elif isinstance(result, list):
                    success_count = sum(1 for r in result if isinstance(r, dict) and r.get("success", False))
                    print(f"  📝 {component}: {success_count}/{len(result)} exitosos")

            # Generar cliente Prisma
            print("\n🔧 Generando cliente Prisma...")
            prisma_result = await agent.generate_prisma_client()
            status = "✅" if prisma_result["success"] else "❌"
            print(f"  {status} Cliente Prisma generado")

            # Crear backup
            print("\n💾 Creando backup inicial...")
            backup_result = await agent.backup_database("initial_schema")
            status = "✅" if backup_result["success"] else "❌"
            print(f"  {status} Backup creado")

            # Mostrar estado del agente
            agent_status = await agent.get_agent_status()
            print(f"\n📈 Estado del agente:")
            print(f"  • Inicializado: {agent_status['is_initialized']}")
            print(f"  • Base de datos conectada: {agent_status['database_connected']}")
            print(f"  • Host: {agent_status['config']['host']}")
            print(f"  • Base de datos: {agent_status['config']['database']}")

        except Exception as e:
            print(f"❌ Error en demo: {e}")

        finally:
            if 'agent' in locals():
                await agent.shutdown()

    asyncio.run(main())
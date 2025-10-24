#!/usr/bin/env python3
"""
SIAME 2026v3 - Authentication & Security Specialist Agent
Agente especializado en autenticación y clasificación de seguridad para sistemas diplomáticos

Este agente maneja:
- Implementación de sistemas de autenticación multi-nivel
- Gestión de clasificaciones de seguridad (Público, Restringido, Confidencial, Secreto, Alto Secreto)
- Integración con Azure AD y sistemas de autenticación externos
- Control de acceso basado en roles (RBAC)
- Auditoría y logging de seguridad
- Encriptación y protección de datos sensibles
"""

import asyncio
import logging
import hashlib
import hmac
import secrets
import jwt
import bcrypt
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum
import json
import base64

# Importaciones para Azure AD
try:
    from msal import ConfidentialClientApplication, PublicClientApplication
    from azure.identity import DefaultAzureCredential
    AZURE_AD_AVAILABLE = True
except ImportError:
    AZURE_AD_AVAILABLE = False


class SecurityLevel(Enum):
    """Niveles de clasificación de seguridad diplomática"""
    PUBLIC = "public"
    RESTRICTED = "restricted"
    CONFIDENTIAL = "confidential"
    SECRET = "secret"
    TOP_SECRET = "top_secret"


class AuthenticationMethod(Enum):
    """Métodos de autenticación soportados"""
    PASSWORD = "password"
    MFA = "mfa"
    AZURE_AD = "azure_ad"
    CERTIFICATE = "certificate"
    SMART_CARD = "smart_card"
    BIOMETRIC = "biometric"


class UserRole(Enum):
    """Roles de usuario en el sistema diplomático"""
    GUEST = "guest"
    OFFICER = "officer"
    DIPLOMAT = "diplomat"
    SENIOR_DIPLOMAT = "senior_diplomat"
    AMBASSADOR = "ambassador"
    ADMINISTRATOR = "administrator"
    SECURITY_OFFICER = "security_officer"
    SYSTEM_ADMIN = "system_admin"


@dataclass
class SecurityClearance:
    """Información de autorización de seguridad"""
    level: SecurityLevel
    granted_by: str
    granted_date: datetime
    expiry_date: Optional[datetime]
    restrictions: List[str] = field(default_factory=list)
    audit_trail: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class User:
    """Usuario del sistema diplomático"""
    id: str
    username: str
    email: str
    password_hash: Optional[str]
    role: UserRole
    security_clearance: SecurityClearance
    department: Optional[str] = None
    country: Optional[str] = None
    embassy: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    last_login: Optional[datetime] = None
    failed_login_attempts: int = 0
    is_active: bool = True
    is_locked: bool = False
    mfa_enabled: bool = False
    mfa_secret: Optional[str] = None
    azure_ad_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AuthenticationToken:
    """Token de autenticación JWT"""
    token: str
    user_id: str
    username: str
    role: UserRole
    security_clearance: SecurityLevel
    permissions: List[str]
    issued_at: datetime
    expires_at: datetime
    refresh_token: Optional[str] = None


@dataclass
class SecurityAuditLog:
    """Registro de auditoría de seguridad"""
    id: str
    user_id: str
    action: str
    resource: str
    security_level: SecurityLevel
    result: str  # success, failure, denied
    ip_address: str
    user_agent: str
    timestamp: datetime = field(default_factory=datetime.now)
    details: Dict[str, Any] = field(default_factory=dict)


class AuthenticationSecurityAgent:
    """Agente especializado en autenticación y seguridad"""

    def __init__(self, agent_id: str = None):
        self.agent_id = agent_id or f"auth_sec_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.logger = logging.getLogger(__name__)

        # Configuración de seguridad
        self.security_config = {
            "jwt_secret": secrets.token_urlsafe(32),
            "jwt_algorithm": "HS256",
            "token_expiry_hours": 8,
            "refresh_token_expiry_days": 30,
            "max_failed_login_attempts": 5,
            "account_lockout_duration_minutes": 30,
            "password_min_length": 12,
            "password_require_complex": True,
            "mfa_required_for_secret": True,
            "audit_all_access": True
        }

        # Matriz de permisos por nivel de seguridad
        self.security_matrix = {
            SecurityLevel.PUBLIC: {
                "can_access": [SecurityLevel.PUBLIC],
                "required_roles": [UserRole.GUEST, UserRole.OFFICER, UserRole.DIPLOMAT,
                                 UserRole.SENIOR_DIPLOMAT, UserRole.AMBASSADOR,
                                 UserRole.ADMINISTRATOR, UserRole.SECURITY_OFFICER,
                                 UserRole.SYSTEM_ADMIN]
            },
            SecurityLevel.RESTRICTED: {
                "can_access": [SecurityLevel.PUBLIC, SecurityLevel.RESTRICTED],
                "required_roles": [UserRole.OFFICER, UserRole.DIPLOMAT,
                                 UserRole.SENIOR_DIPLOMAT, UserRole.AMBASSADOR,
                                 UserRole.ADMINISTRATOR, UserRole.SECURITY_OFFICER,
                                 UserRole.SYSTEM_ADMIN]
            },
            SecurityLevel.CONFIDENTIAL: {
                "can_access": [SecurityLevel.PUBLIC, SecurityLevel.RESTRICTED,
                             SecurityLevel.CONFIDENTIAL],
                "required_roles": [UserRole.DIPLOMAT, UserRole.SENIOR_DIPLOMAT,
                                 UserRole.AMBASSADOR, UserRole.ADMINISTRATOR,
                                 UserRole.SECURITY_OFFICER, UserRole.SYSTEM_ADMIN]
            },
            SecurityLevel.SECRET: {
                "can_access": [SecurityLevel.PUBLIC, SecurityLevel.RESTRICTED,
                             SecurityLevel.CONFIDENTIAL, SecurityLevel.SECRET],
                "required_roles": [UserRole.SENIOR_DIPLOMAT, UserRole.AMBASSADOR,
                                 UserRole.ADMINISTRATOR, UserRole.SECURITY_OFFICER,
                                 UserRole.SYSTEM_ADMIN]
            },
            SecurityLevel.TOP_SECRET: {
                "can_access": [SecurityLevel.PUBLIC, SecurityLevel.RESTRICTED,
                             SecurityLevel.CONFIDENTIAL, SecurityLevel.SECRET,
                             SecurityLevel.TOP_SECRET],
                "required_roles": [UserRole.AMBASSADOR, UserRole.ADMINISTRATOR,
                                 UserRole.SECURITY_OFFICER, UserRole.SYSTEM_ADMIN]
            }
        }

        # Almacenamiento temporal (en producción usar base de datos)
        self.users: Dict[str, User] = {}
        self.active_tokens: Dict[str, AuthenticationToken] = {}
        self.audit_logs: List[SecurityAuditLog] = []

        # Configuración Azure AD
        self.azure_ad_config = {
            "client_id": "",
            "client_secret": "",
            "tenant_id": "",
            "authority": "",
            "redirect_uri": "http://localhost:3000/auth/callback"
        }

        # Estadísticas del agente
        self.stats = {
            "users_registered": 0,
            "successful_logins": 0,
            "failed_logins": 0,
            "tokens_issued": 0,
            "security_violations": 0,
            "audit_logs_created": 0
        }

    async def initialize(self) -> bool:
        """Inicializa el agente de autenticación y seguridad"""
        try:
            self.logger.info("Inicializando Authentication & Security Agent")

            # Crear usuario administrador por defecto
            await self._create_default_admin_user()

            # Configurar Azure AD si está disponible
            if AZURE_AD_AVAILABLE and self.azure_ad_config["client_id"]:
                await self._configure_azure_ad()

            # Inicializar sistema de auditoría
            await self._initialize_audit_system()

            self.logger.info("Authentication & Security Agent inicializado exitosamente")
            return True

        except Exception as e:
            self.logger.error(f"Error inicializando Authentication & Security Agent: {e}")
            return False

    async def authenticate_user(self, username: str, password: str,
                              mfa_code: Optional[str] = None,
                              ip_address: str = "unknown",
                              user_agent: str = "unknown") -> Dict[str, Any]:
        """Autentica un usuario con credenciales"""
        try:
            self.logger.info(f"Intento de autenticación para usuario: {username}")

            # Buscar usuario
            user = await self._find_user_by_username(username)
            if not user:
                await self._log_security_event(
                    user_id="unknown",
                    action="authentication_attempt",
                    resource="login",
                    security_level=SecurityLevel.PUBLIC,
                    result="failure",
                    ip_address=ip_address,
                    user_agent=user_agent,
                    details={"reason": "user_not_found", "username": username}
                )
                return {"success": False, "error": "Credenciales inválidas"}

            # Verificar si la cuenta está bloqueada
            if user.is_locked:
                await self._log_security_event(
                    user_id=user.id,
                    action="authentication_attempt",
                    resource="login",
                    security_level=SecurityLevel.PUBLIC,
                    result="denied",
                    ip_address=ip_address,
                    user_agent=user_agent,
                    details={"reason": "account_locked"}
                )
                return {"success": False, "error": "Cuenta bloqueada"}

            # Verificar contraseña
            if not await self._verify_password(password, user.password_hash):
                user.failed_login_attempts += 1

                # Bloquear cuenta si excede intentos máximos
                if user.failed_login_attempts >= self.security_config["max_failed_login_attempts"]:
                    user.is_locked = True
                    await self._schedule_account_unlock(user.id)

                await self._log_security_event(
                    user_id=user.id,
                    action="authentication_attempt",
                    resource="login",
                    security_level=SecurityLevel.PUBLIC,
                    result="failure",
                    ip_address=ip_address,
                    user_agent=user_agent,
                    details={"reason": "invalid_password", "failed_attempts": user.failed_login_attempts}
                )

                self.stats["failed_logins"] += 1
                return {"success": False, "error": "Credenciales inválidas"}

            # Verificar MFA si está habilitado
            if user.mfa_enabled:
                if not mfa_code:
                    return {"success": False, "error": "Código MFA requerido", "mfa_required": True}

                if not await self._verify_mfa_code(user.mfa_secret, mfa_code):
                    await self._log_security_event(
                        user_id=user.id,
                        action="mfa_verification",
                        resource="login",
                        security_level=SecurityLevel.PUBLIC,
                        result="failure",
                        ip_address=ip_address,
                        user_agent=user_agent,
                        details={"reason": "invalid_mfa_code"}
                    )
                    return {"success": False, "error": "Código MFA inválido"}

            # Autenticación exitosa
            user.failed_login_attempts = 0
            user.last_login = datetime.now()

            # Generar token
            token = await self._generate_jwt_token(user)

            await self._log_security_event(
                user_id=user.id,
                action="authentication_success",
                resource="login",
                security_level=SecurityLevel.PUBLIC,
                result="success",
                ip_address=ip_address,
                user_agent=user_agent,
                details={"role": user.role.value, "security_clearance": user.security_clearance.level.value}
            )

            self.stats["successful_logins"] += 1
            self.stats["tokens_issued"] += 1

            return {
                "success": True,
                "token": token.token,
                "refresh_token": token.refresh_token,
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "role": user.role.value,
                    "security_clearance": user.security_clearance.level.value,
                    "department": user.department,
                    "country": user.country
                },
                "expires_at": token.expires_at.isoformat(),
                "permissions": token.permissions
            }

        except Exception as e:
            self.logger.error(f"Error en autenticación: {e}")
            return {"success": False, "error": "Error interno del servidor"}

    async def authenticate_with_azure_ad(self, azure_token: str,
                                       ip_address: str = "unknown",
                                       user_agent: str = "unknown") -> Dict[str, Any]:
        """Autentica usuario usando Azure AD"""
        try:
            if not AZURE_AD_AVAILABLE:
                return {"success": False, "error": "Azure AD no disponible"}

            # Verificar token de Azure AD
            azure_user_info = await self._verify_azure_ad_token(azure_token)
            if not azure_user_info:
                return {"success": False, "error": "Token de Azure AD inválido"}

            # Buscar o crear usuario
            user = await self._find_or_create_azure_user(azure_user_info)

            # Generar token interno
            token = await self._generate_jwt_token(user)

            await self._log_security_event(
                user_id=user.id,
                action="azure_ad_authentication",
                resource="login",
                security_level=SecurityLevel.PUBLIC,
                result="success",
                ip_address=ip_address,
                user_agent=user_agent,
                details={"azure_ad_id": user.azure_ad_id}
            )

            self.stats["successful_logins"] += 1
            self.stats["tokens_issued"] += 1

            return {
                "success": True,
                "token": token.token,
                "refresh_token": token.refresh_token,
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "role": user.role.value,
                    "security_clearance": user.security_clearance.level.value
                },
                "expires_at": token.expires_at.isoformat(),
                "permissions": token.permissions
            }

        except Exception as e:
            self.logger.error(f"Error en autenticación Azure AD: {e}")
            return {"success": False, "error": "Error en autenticación Azure AD"}

    async def verify_token(self, token: str) -> Dict[str, Any]:
        """Verifica y decodifica un token JWT"""
        try:
            # Decodificar token
            payload = jwt.decode(
                token,
                self.security_config["jwt_secret"],
                algorithms=[self.security_config["jwt_algorithm"]]
            )

            # Verificar expiración
            exp_timestamp = payload.get("exp")
            if exp_timestamp and datetime.fromtimestamp(exp_timestamp) < datetime.now():
                return {"success": False, "error": "Token expirado"}

            # Buscar usuario
            user_id = payload.get("user_id")
            user = self.users.get(user_id)

            if not user or not user.is_active:
                return {"success": False, "error": "Usuario no válido"}

            return {
                "success": True,
                "user_id": user_id,
                "username": payload.get("username"),
                "role": payload.get("role"),
                "security_clearance": payload.get("security_clearance"),
                "permissions": payload.get("permissions", []),
                "user": user
            }

        except jwt.ExpiredSignatureError:
            return {"success": False, "error": "Token expirado"}
        except jwt.InvalidTokenError:
            return {"success": False, "error": "Token inválido"}
        except Exception as e:
            self.logger.error(f"Error verificando token: {e}")
            return {"success": False, "error": "Error verificando token"}

    async def check_access_permission(self, user_id: str, resource_security_level: SecurityLevel,
                                    action: str = "read") -> Dict[str, Any]:
        """Verifica si un usuario tiene permisos para acceder a un recurso"""
        try:
            user = self.users.get(user_id)
            if not user:
                return {"success": False, "error": "Usuario no encontrado"}

            if not user.is_active:
                return {"success": False, "error": "Usuario inactivo"}

            # Verificar nivel de seguridad
            user_clearance = user.security_clearance.level
            allowed_levels = self.security_matrix[user_clearance]["can_access"]

            if resource_security_level not in allowed_levels:
                await self._log_security_event(
                    user_id=user_id,
                    action="access_denied",
                    resource=f"{resource_security_level.value}_resource",
                    security_level=resource_security_level,
                    result="denied",
                    ip_address="unknown",
                    user_agent="unknown",
                    details={
                        "reason": "insufficient_security_clearance",
                        "user_clearance": user_clearance.value,
                        "required_clearance": resource_security_level.value,
                        "action": action
                    }
                )

                self.stats["security_violations"] += 1
                return {"success": False, "error": "Autorización de seguridad insuficiente"}

            # Verificar rol
            required_roles = self.security_matrix[resource_security_level]["required_roles"]
            if user.role not in required_roles:
                await self._log_security_event(
                    user_id=user_id,
                    action="access_denied",
                    resource=f"{resource_security_level.value}_resource",
                    security_level=resource_security_level,
                    result="denied",
                    ip_address="unknown",
                    user_agent="unknown",
                    details={
                        "reason": "insufficient_role",
                        "user_role": user.role.value,
                        "required_roles": [r.value for r in required_roles],
                        "action": action
                    }
                )

                self.stats["security_violations"] += 1
                return {"success": False, "error": "Rol insuficiente"}

            # Verificar si la autorización ha expirado
            if user.security_clearance.expiry_date and user.security_clearance.expiry_date < datetime.now():
                return {"success": False, "error": "Autorización de seguridad expirada"}

            # Registrar acceso autorizado
            await self._log_security_event(
                user_id=user_id,
                action="access_granted",
                resource=f"{resource_security_level.value}_resource",
                security_level=resource_security_level,
                result="success",
                ip_address="unknown",
                user_agent="unknown",
                details={"action": action}
            )

            return {
                "success": True,
                "user_clearance": user_clearance.value,
                "user_role": user.role.value,
                "access_granted": True
            }

        except Exception as e:
            self.logger.error(f"Error verificando permisos: {e}")
            return {"success": False, "error": "Error verificando permisos"}

    async def create_user(self, username: str, email: str, password: str,
                        role: UserRole, security_level: SecurityLevel,
                        department: str = None, country: str = None) -> Dict[str, Any]:
        """Crea un nuevo usuario en el sistema"""
        try:
            # Verificar si el usuario ya existe
            if await self._find_user_by_username(username):
                return {"success": False, "error": "El usuario ya existe"}

            if await self._find_user_by_email(email):
                return {"success": False, "error": "El email ya está registrado"}

            # Validar contraseña
            password_validation = await self._validate_password(password)
            if not password_validation["valid"]:
                return {"success": False, "error": password_validation["error"]}

            # Crear usuario
            user_id = f"user_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{secrets.token_hex(4)}"
            password_hash = await self._hash_password(password)

            security_clearance = SecurityClearance(
                level=security_level,
                granted_by="system",
                granted_date=datetime.now(),
                expiry_date=datetime.now() + timedelta(days=365)  # 1 año por defecto
            )

            user = User(
                id=user_id,
                username=username,
                email=email,
                password_hash=password_hash,
                role=role,
                security_clearance=security_clearance,
                department=department,
                country=country
            )

            self.users[user_id] = user
            self.stats["users_registered"] += 1

            await self._log_security_event(
                user_id=user_id,
                action="user_created",
                resource="user_management",
                security_level=SecurityLevel.RESTRICTED,
                result="success",
                ip_address="system",
                user_agent="system",
                details={
                    "username": username,
                    "role": role.value,
                    "security_clearance": security_level.value,
                    "department": department,
                    "country": country
                }
            )

            return {
                "success": True,
                "user_id": user_id,
                "message": "Usuario creado exitosamente"
            }

        except Exception as e:
            self.logger.error(f"Error creando usuario: {e}")
            return {"success": False, "error": "Error creando usuario"}

    async def enable_mfa(self, user_id: str) -> Dict[str, Any]:
        """Habilita autenticación de múltiples factores para un usuario"""
        try:
            user = self.users.get(user_id)
            if not user:
                return {"success": False, "error": "Usuario no encontrado"}

            # Generar secreto MFA
            mfa_secret = secrets.token_urlsafe(32)
            user.mfa_secret = mfa_secret
            user.mfa_enabled = True

            # Generar QR code URL (para apps como Google Authenticator)
            app_name = "SIAME 2026v3"
            qr_url = f"otpauth://totp/{app_name}:{user.username}?secret={mfa_secret}&issuer={app_name}"

            await self._log_security_event(
                user_id=user_id,
                action="mfa_enabled",
                resource="user_security",
                security_level=SecurityLevel.RESTRICTED,
                result="success",
                ip_address="system",
                user_agent="system",
                details={"username": user.username}
            )

            return {
                "success": True,
                "mfa_secret": mfa_secret,
                "qr_url": qr_url,
                "message": "MFA habilitado exitosamente"
            }

        except Exception as e:
            self.logger.error(f"Error habilitando MFA: {e}")
            return {"success": False, "error": "Error habilitando MFA"}

    async def get_security_audit_logs(self, user_id: Optional[str] = None,
                                    security_level: Optional[SecurityLevel] = None,
                                    action: Optional[str] = None,
                                    limit: int = 100) -> List[Dict[str, Any]]:
        """Obtiene logs de auditoría de seguridad"""
        try:
            filtered_logs = self.audit_logs

            # Filtrar por usuario
            if user_id:
                filtered_logs = [log for log in filtered_logs if log.user_id == user_id]

            # Filtrar por nivel de seguridad
            if security_level:
                filtered_logs = [log for log in filtered_logs if log.security_level == security_level]

            # Filtrar por acción
            if action:
                filtered_logs = [log for log in filtered_logs if log.action == action]

            # Limitar resultados
            filtered_logs = filtered_logs[-limit:]

            # Convertir a diccionarios
            log_dicts = []
            for log in filtered_logs:
                log_dict = {
                    "id": log.id,
                    "user_id": log.user_id,
                    "action": log.action,
                    "resource": log.resource,
                    "security_level": log.security_level.value,
                    "result": log.result,
                    "ip_address": log.ip_address,
                    "user_agent": log.user_agent,
                    "timestamp": log.timestamp.isoformat(),
                    "details": log.details
                }
                log_dicts.append(log_dict)

            return log_dicts

        except Exception as e:
            self.logger.error(f"Error obteniendo logs de auditoría: {e}")
            return []

    async def get_agent_statistics(self) -> Dict[str, Any]:
        """Obtiene estadísticas del agente"""
        return {
            "agent_id": self.agent_id,
            "agent_type": "Authentication & Security Specialist",
            "statistics": self.stats,
            "security_levels": [level.value for level in SecurityLevel],
            "user_roles": [role.value for role in UserRole],
            "authentication_methods": [method.value for method in AuthenticationMethod],
            "total_users": len(self.users),
            "active_tokens": len(self.active_tokens),
            "audit_logs_count": len(self.audit_logs),
            "azure_ad_enabled": AZURE_AD_AVAILABLE and bool(self.azure_ad_config["client_id"])
        }

    # Métodos privados

    async def _create_default_admin_user(self) -> None:
        """Crea usuario administrador por defecto"""
        admin_result = await self.create_user(
            username="admin",
            email="admin@siame.gov",
            password="AdminSIAME2026!",
            role=UserRole.SYSTEM_ADMIN,
            security_level=SecurityLevel.TOP_SECRET,
            department="Sistemas",
            country="Sistema"
        )

        if admin_result["success"]:
            self.logger.info("Usuario administrador por defecto creado")
        else:
            self.logger.warning(f"No se pudo crear usuario admin: {admin_result['error']}")

    async def _find_user_by_username(self, username: str) -> Optional[User]:
        """Busca usuario por nombre de usuario"""
        for user in self.users.values():
            if user.username.lower() == username.lower():
                return user
        return None

    async def _find_user_by_email(self, email: str) -> Optional[User]:
        """Busca usuario por email"""
        for user in self.users.values():
            if user.email.lower() == email.lower():
                return user
        return None

    async def _hash_password(self, password: str) -> str:
        """Genera hash de contraseña usando bcrypt"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')

    async def _verify_password(self, password: str, password_hash: str) -> bool:
        """Verifica contraseña contra hash"""
        if not password_hash:
            return False
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))

    async def _validate_password(self, password: str) -> Dict[str, Any]:
        """Valida fortaleza de contraseña"""
        if len(password) < self.security_config["password_min_length"]:
            return {
                "valid": False,
                "error": f"La contraseña debe tener al menos {self.security_config['password_min_length']} caracteres"
            }

        if self.security_config["password_require_complex"]:
            has_upper = any(c.isupper() for c in password)
            has_lower = any(c.islower() for c in password)
            has_digit = any(c.isdigit() for c in password)
            has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)

            if not all([has_upper, has_lower, has_digit, has_special]):
                return {
                    "valid": False,
                    "error": "La contraseña debe contener mayúsculas, minúsculas, números y caracteres especiales"
                }

        return {"valid": True}

    async def _generate_jwt_token(self, user: User) -> AuthenticationToken:
        """Genera token JWT para usuario"""
        now = datetime.now()
        expiry = now + timedelta(hours=self.security_config["token_expiry_hours"])

        # Determinar permisos basados en rol y autorización
        permissions = await self._get_user_permissions(user)

        payload = {
            "user_id": user.id,
            "username": user.username,
            "role": user.role.value,
            "security_clearance": user.security_clearance.level.value,
            "permissions": permissions,
            "iat": int(now.timestamp()),
            "exp": int(expiry.timestamp())
        }

        token = jwt.encode(
            payload,
            self.security_config["jwt_secret"],
            algorithm=self.security_config["jwt_algorithm"]
        )

        # Generar refresh token
        refresh_token = secrets.token_urlsafe(32)

        auth_token = AuthenticationToken(
            token=token,
            user_id=user.id,
            username=user.username,
            role=user.role,
            security_clearance=user.security_clearance.level,
            permissions=permissions,
            issued_at=now,
            expires_at=expiry,
            refresh_token=refresh_token
        )

        self.active_tokens[token] = auth_token
        return auth_token

    async def _get_user_permissions(self, user: User) -> List[str]:
        """Obtiene permisos del usuario basados en rol y autorización"""
        permissions = []

        # Permisos básicos por nivel de seguridad
        security_permissions = {
            SecurityLevel.PUBLIC: ["read:public"],
            SecurityLevel.RESTRICTED: ["read:public", "read:restricted"],
            SecurityLevel.CONFIDENTIAL: ["read:public", "read:restricted", "read:confidential"],
            SecurityLevel.SECRET: ["read:public", "read:restricted", "read:confidential", "read:secret"],
            SecurityLevel.TOP_SECRET: ["read:public", "read:restricted", "read:confidential", "read:secret", "read:top_secret"]
        }

        permissions.extend(security_permissions.get(user.security_clearance.level, []))

        # Permisos adicionales por rol
        role_permissions = {
            UserRole.GUEST: [],
            UserRole.OFFICER: ["create:restricted"],
            UserRole.DIPLOMAT: ["create:restricted", "create:confidential"],
            UserRole.SENIOR_DIPLOMAT: ["create:restricted", "create:confidential", "create:secret"],
            UserRole.AMBASSADOR: ["create:restricted", "create:confidential", "create:secret", "create:top_secret"],
            UserRole.ADMINISTRATOR: ["admin:system", "manage:users"],
            UserRole.SECURITY_OFFICER: ["admin:security", "audit:logs"],
            UserRole.SYSTEM_ADMIN: ["admin:system", "admin:security", "manage:users", "audit:logs"]
        }

        permissions.extend(role_permissions.get(user.role, []))

        return list(set(permissions))  # Eliminar duplicados

    async def _verify_mfa_code(self, secret: str, code: str) -> bool:
        """Verifica código MFA/TOTP"""
        try:
            # Implementación básica - en producción usar biblioteca TOTP completa
            import time
            import hmac
            import struct

            # Obtener timestamp actual en intervalos de 30 segundos
            timestamp = int(time.time() // 30)

            # Generar código esperado
            expected_code = self._generate_totp_code(secret, timestamp)

            # Verificar también códigos de ventanas adyacentes (±1 intervalo)
            for offset in [-1, 0, 1]:
                test_code = self._generate_totp_code(secret, timestamp + offset)
                if test_code == code:
                    return True

            return False

        except Exception as e:
            self.logger.error(f"Error verificando código MFA: {e}")
            return False

    def _generate_totp_code(self, secret: str, timestamp: int) -> str:
        """Genera código TOTP"""
        try:
            # Convertir secreto y timestamp a bytes
            key = base64.b32decode(secret.upper() + '=' * (-len(secret) % 8))
            timestamp_bytes = struct.pack('>Q', timestamp)

            # Generar HMAC
            digest = hmac.new(key, timestamp_bytes, hashlib.sha1).digest()

            # Extraer código de 6 dígitos
            offset = digest[-1] & 0x0f
            code_bytes = digest[offset:offset + 4]
            code = struct.unpack('>I', code_bytes)[0] & 0x7fffffff
            totp_code = f"{code % 1000000:06d}"

            return totp_code

        except Exception:
            return "000000"

    async def _log_security_event(self, user_id: str, action: str, resource: str,
                                security_level: SecurityLevel, result: str,
                                ip_address: str, user_agent: str,
                                details: Dict[str, Any]) -> None:
        """Registra evento de seguridad en auditoría"""
        try:
            log_id = f"audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{secrets.token_hex(4)}"

            audit_log = SecurityAuditLog(
                id=log_id,
                user_id=user_id,
                action=action,
                resource=resource,
                security_level=security_level,
                result=result,
                ip_address=ip_address,
                user_agent=user_agent,
                details=details
            )

            self.audit_logs.append(audit_log)
            self.stats["audit_logs_created"] += 1

            # Log crítico para eventos de seguridad importantes
            if result in ["failure", "denied"] or security_level in [SecurityLevel.SECRET, SecurityLevel.TOP_SECRET]:
                self.logger.warning(
                    f"Evento de seguridad: {action} | Usuario: {user_id} | "
                    f"Resultado: {result} | Nivel: {security_level.value}"
                )

        except Exception as e:
            self.logger.error(f"Error registrando evento de auditoría: {e}")

    async def _schedule_account_unlock(self, user_id: str) -> None:
        """Programa desbloqueo automático de cuenta"""
        async def unlock_account():
            await asyncio.sleep(self.security_config["account_lockout_duration_minutes"] * 60)
            user = self.users.get(user_id)
            if user:
                user.is_locked = False
                user.failed_login_attempts = 0
                self.logger.info(f"Cuenta desbloqueada automáticamente: {user.username}")

        # Ejecutar en background
        asyncio.create_task(unlock_account())

    async def _configure_azure_ad(self) -> None:
        """Configura integración con Azure AD"""
        self.logger.info("Configurando integración con Azure AD")
        # TODO: Implementar configuración completa de Azure AD

    async def _initialize_audit_system(self) -> None:
        """Inicializa sistema de auditoría"""
        self.logger.info("Sistema de auditoría inicializado")

    async def _verify_azure_ad_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verifica token de Azure AD"""
        # TODO: Implementar verificación real de token Azure AD
        return None

    async def _find_or_create_azure_user(self, azure_user_info: Dict[str, Any]) -> User:
        """Encuentra o crea usuario basado en información de Azure AD"""
        # TODO: Implementar lógica de usuario Azure AD
        pass


# Función principal para testing
async def main():
    """Función principal para testing del agente"""
    logging.basicConfig(level=logging.INFO)

    agent = AuthenticationSecurityAgent()
    await agent.initialize()

    # Crear usuario de prueba
    result = await agent.create_user(
        username="diplomatico1",
        email="diplomatico1@embajada.gov",
        password="DiploSecure2026!",
        role=UserRole.DIPLOMAT,
        security_level=SecurityLevel.CONFIDENTIAL,
        department="Relaciones Exteriores",
        country="Colombia"
    )
    print(f"Usuario creado: {result}")

    # Autenticar usuario
    auth_result = await agent.authenticate_user("diplomatico1", "DiploSecure2026!")
    print(f"Autenticación: {auth_result}")

    # Verificar permisos
    if auth_result["success"]:
        access_result = await agent.check_access_permission(
            auth_result["user"]["id"],
            SecurityLevel.CONFIDENTIAL
        )
        print(f"Verificación de acceso: {access_result}")

    # Obtener estadísticas
    stats = await agent.get_agent_statistics()
    print(f"Estadísticas: {stats}")


if __name__ == "__main__":
    asyncio.run(main())
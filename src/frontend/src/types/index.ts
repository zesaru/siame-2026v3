/**
 * SIAME 2026v3 - Tipos TypeScript
 * Definiciones de tipos para el sistema diplomático
 */

// Niveles de clasificación de seguridad
export enum SecurityClassification {
  PUBLICO = "PUBLICO",
  RESTRINGIDO = "RESTRINGIDO",
  CONFIDENCIAL = "CONFIDENCIAL",
  SECRETO = "SECRETO",
  ALTO_SECRETO = "ALTO_SECRETO"
}

// Roles diplomáticos
export enum DiplomaticRole {
  EMBAJADOR = "EMBAJADOR",
  MINISTRO_CONSEJERO = "MINISTRO_CONSEJERO",
  CONSEJERO = "CONSEJERO",
  PRIMER_SECRETARIO = "PRIMER_SECRETARIO",
  SEGUNDO_SECRETARIO = "SEGUNDO_SECRETARIO",
  TERCER_SECRETARIO = "TERCER_SECRETARIO",
  AGREGADO = "AGREGADO",
  FUNCIONARIO_ADMINISTRATIVO = "FUNCIONARIO_ADMINISTRATIVO",
  CONSULTOR_EXTERNO = "CONSULTOR_EXTERNO",
  INVITADO = "INVITADO"
}

// Tipos de documentos diplomáticos
export enum DocumentType {
  HOJA_REMISION_OGA = "HOJA_REMISION_OGA",
  HOJA_REMISION_PCO = "HOJA_REMISION_PCO",
  HOJA_REMISION_PRU = "HOJA_REMISION_PRU",
  GUIA_VALIJA_ENTRADA_ORD = "GUIA_VALIJA_ENTRADA_ORD",
  GUIA_VALIJA_ENTRADA_EXT = "GUIA_VALIJA_ENTRADA_EXT",
  GUIA_VALIJA_SALIDA_ORD = "GUIA_VALIJA_SALIDA_ORD",
  GUIA_VALIJA_SALIDA_EXT = "GUIA_VALIJA_SALIDA_EXT",
  NOTA_DIPLOMATICA = "NOTA_DIPLOMATICA",
  DESPACHO = "DESPACHO",
  MEMORANDUM = "MEMORANDUM"
}

// Estado del documento
export enum DocumentStatus {
  PENDING = "PENDING",
  PROCESSING = "PROCESSING",
  PROCESSED = "PROCESSED",
  APPROVED = "APPROVED",
  REJECTED = "REJECTED",
  ARCHIVED = "ARCHIVED"
}

// Prioridad del documento
export enum DocumentPriority {
  LOW = "LOW",
  NORMAL = "NORMAL",
  HIGH = "HIGH",
  URGENT = "URGENT",
  CRITICAL = "CRITICAL"
}

// Usuario del sistema
export interface User {
  id: string;
  email: string;
  username: string;
  firstName: string;
  lastName: string;
  phoneNumber?: string;
  isActive: boolean;
  lastLoginAt?: Date;

  // Información diplomática
  diplomaticId?: string;
  position?: string;
  department?: string;
  embassy?: string;
  country?: string;

  // Configuración de seguridad
  securityClearance: SecurityClassification;
  maxClassification: SecurityClassification;

  // Metadatos
  createdAt: Date;
  updatedAt: Date;
}

// Documento diplomático
export interface DiplomaticDocument {
  id: string;
  documentNumber: string;
  documentType: DocumentType;
  classification: SecurityClassification;
  title: string;
  description?: string;

  // Metadatos del archivo
  originalFileName?: string;
  fileSize?: number;
  mimeType?: string;
  azureBlobPath?: string;

  // Datos extraídos
  extractedData?: Record<string, any>;
  confidenceScore?: number;

  // Información diplomática
  originEmbassy?: string;
  destinationEmbassy?: string;
  diplomaticSeries?: string;
  diplomaticNumber?: string;
  subject?: string;
  reference?: string;

  // Fechas
  documentDate?: Date;
  receivedDate?: Date;
  processedDate?: Date;

  // Estado
  status: DocumentStatus;
  priority: DocumentPriority;

  // Seguridad
  accessLevel: number;
  isClassified: boolean;
  declassificationDate?: Date;

  // Relaciones
  authorId: string;
  author?: User;

  // Metadatos del sistema
  createdAt: Date;
  updatedAt: Date;
}

// Permisos de usuario
export interface Permission {
  id: string;
  name: string;
  description?: string;
  resource: string;
  action: string;
}

// Rol del sistema
export interface Role {
  id: string;
  name: string;
  description?: string;
  level: number;
  permissions: Permission[];
}

// Sesión de usuario
export interface UserSession {
  id: string;
  userId: string;
  token: string;
  ipAddress?: string;
  userAgent?: string;
  expiresAt: Date;
  isActive: boolean;
  user?: User;
}

// Autorización de documento
export interface DocumentAuthorization {
  id: string;
  documentId: string;
  userId: string;
  accessType: "READ" | "WRITE" | "DELETE" | "SHARE" | "ADMIN";
  grantedBy: string;
  grantedAt: Date;
  expiresAt?: Date;
  reason?: string;
}

// Log de auditoría
export interface AuditLog {
  id: string;
  tableName: string;
  recordId: string;
  action: "CREATE" | "READ" | "UPDATE" | "DELETE" | "LOGIN" | "LOGOUT";
  oldValues?: Record<string, any>;
  newValues?: Record<string, any>;
  userId?: string;
  user?: User;
  ipAddress?: string;
  userAgent?: string;
  timestamp: Date;
}

// Embajada
export interface Embassy {
  id: string;
  name: string;
  country: string;
  code: string;
  address?: string;
  timezone?: string;
  isActive: boolean;
}

// Navegación de la aplicación
export interface NavItem {
  title: string;
  href: string;
  icon?: string;
  disabled?: boolean;
  external?: boolean;
  requiredRole?: DiplomaticRole;
  requiredClearance?: SecurityClassification;
  children?: NavItem[];
}

// Configuración de la aplicación
export interface AppConfig {
  name: string;
  version: string;
  ministryName: string;
  maxFileSizeMB: number;
  allowedFileTypes: string[];
  defaultClassification: SecurityClassification;
  maxClassificationLevel: SecurityClassification;
  enableAnalytics: boolean;
  debugMode: boolean;
}

// Resultados de procesamiento de documentos
export interface DocumentProcessingResult {
  success: boolean;
  documentId?: string;
  extractedData?: Record<string, any>;
  confidenceScore?: number;
  classification?: SecurityClassification;
  error?: string;
}

// Estadísticas del dashboard
export interface DashboardStats {
  totalDocuments: number;
  documentsThisMonth: number;
  pendingApprovals: number;
  highPriorityDocuments: number;
  documentsByClassification: Record<SecurityClassification, number>;
  documentsByType: Record<DocumentType, number>;
  recentActivity: AuditLog[];
}

// Filtros de búsqueda
export interface DocumentFilters {
  documentType?: DocumentType;
  classification?: SecurityClassification;
  status?: DocumentStatus;
  priority?: DocumentPriority;
  dateFrom?: Date;
  dateTo?: Date;
  embassy?: string;
  author?: string;
  searchText?: string;
}

// Respuesta de API genérica
export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
  total?: number;
  page?: number;
  limit?: number;
}

// Configuración de paginación
export interface PaginationConfig {
  page: number;
  limit: number;
  total: number;
  totalPages: number;
}

// Notificación del sistema
export interface SystemNotification {
  id: string;
  type: "info" | "warning" | "error" | "success";
  title: string;
  message: string;
  userId?: string;
  isRead: boolean;
  createdAt: Date;
  expiresAt?: Date;
}

// Estado de carga de la aplicación
export interface LoadingState {
  isLoading: boolean;
  operation?: string;
  progress?: number;
}

// Error de la aplicación
export interface AppError {
  code: string;
  message: string;
  details?: any;
  timestamp: Date;
}

// Configuración de tema
export interface ThemeConfig {
  mode: "light" | "dark" | "system";
  primaryColor: string;
  accentColor: string;
}

export default {
  SecurityClassification,
  DiplomaticRole,
  DocumentType,
  DocumentStatus,
  DocumentPriority
};
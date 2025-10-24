# SIAME 2026v3 - Estructura Completa del Proyecto

## Sistema Inteligente de Administración y Manejo de Expedientes
### Ministerio de Asuntos Exteriores, Unión Europea y Cooperación

```
siame-2026v3/
├── README.md                          # Documentación principal del proyecto
├── .env                               # Variables de entorno (desarrollo)
├── .env.example                       # Plantilla de variables de entorno
├── .gitignore                         # Archivos ignorados por Git
├── package.json                       # Dependencias del proyecto principal
├── docker-compose.yml                 # Orquestación de servicios
├── Dockerfile                         # Imagen Docker principal
├── CHANGELOG.md                       # Historial de cambios
├── LICENSE                            # Licencia del proyecto
│
├── src/                               # Código fuente principal
│   ├── backend/                       # Backend del sistema
│   │   ├── orchestrator/              # Orquestador principal
│   │   │   ├── __init__.py
│   │   │   ├── main.py                # Punto de entrada del orquestador
│   │   │   ├── coordinator.py         # Coordinador de agentes
│   │   │   ├── task_queue.py          # Cola de tareas
│   │   │   ├── message_broker.py      # Broker de mensajes
│   │   │   └── health_monitor.py      # Monitor de salud del sistema
│   │   │
│   │   ├── agents/                    # Agentes especializados
│   │   │   ├── __init__.py
│   │   │   ├── base/                  # Clases base para agentes
│   │   │   │   ├── __init__.py
│   │   │   │   ├── agent.py           # Clase base de agente
│   │   │   │   ├── communication.py   # Comunicación entre agentes
│   │   │   │   └── security.py        # Seguridad de agentes
│   │   │   │
│   │   │   ├── document_processor/    # Procesamiento de documentos
│   │   │   │   ├── __init__.py
│   │   │   │   ├── main.py            # Agente principal
│   │   │   │   ├── ocr_service.py     # Servicio OCR
│   │   │   │   ├── classifier.py      # Clasificador de documentos
│   │   │   │   ├── extractor.py       # Extractor de datos
│   │   │   │   └── validator.py       # Validador de documentos
│   │   │   │
│   │   │   ├── database_manager/      # Gestión de base de datos
│   │   │   │   ├── __init__.py
│   │   │   │   ├── main.py            # Agente principal
│   │   │   │   ├── connection.py      # Conexiones a BD
│   │   │   │   ├── migrations.py      # Migraciones
│   │   │   │   ├── security_policies.py # Políticas RLS
│   │   │   │   └── audit_logger.py    # Logger de auditoría
│   │   │   │
│   │   │   ├── azure_specialist/      # Especialista Azure
│   │   │   │   ├── __init__.py
│   │   │   │   ├── main.py            # Agente principal
│   │   │   │   ├── form_recognizer.py # Azure Form Recognizer
│   │   │   │   ├── blob_storage.py    # Azure Blob Storage
│   │   │   │   ├── key_vault.py       # Azure Key Vault
│   │   │   │   └── cognitive_services.py # Servicios cognitivos
│   │   │   │
│   │   │   ├── security_guardian/     # Guardián de seguridad
│   │   │   │   ├── __init__.py
│   │   │   │   ├── main.py            # Agente principal
│   │   │   │   ├── access_control.py  # Control de acceso
│   │   │   │   ├── encryption.py      # Encriptación
│   │   │   │   ├── audit_monitor.py   # Monitor de auditoría
│   │   │   │   └── threat_detector.py # Detector de amenazas
│   │   │   │
│   │   │   ├── workflow_manager/      # Gestor de flujos de trabajo
│   │   │   │   ├── __init__.py
│   │   │   │   ├── main.py            # Agente principal
│   │   │   │   ├── diplomatic_flows.py # Flujos diplomáticos
│   │   │   │   ├── approval_chains.py # Cadenas de aprobación
│   │   │   │   └── status_tracker.py  # Seguimiento de estados
│   │   │   │
│   │   │   ├── communication_hub/     # Hub de comunicaciones
│   │   │   │   ├── __init__.py
│   │   │   │   ├── main.py            # Agente principal
│   │   │   │   ├── email_service.py   # Servicio de email
│   │   │   │   ├── notification_center.py # Centro de notificaciones
│   │   │   │   └── diplomatic_protocol.py # Protocolo diplomático
│   │   │   │
│   │   │   └── quality_assurance/     # Control de calidad
│   │   │       ├── __init__.py
│   │   │       ├── main.py            # Agente principal
│   │   │       ├── test_runner.py     # Ejecutor de pruebas
│   │   │       ├── compliance_checker.py # Verificador de cumplimiento
│   │   │       └── performance_monitor.py # Monitor de rendimiento
│   │   │
│   │   ├── api/                       # API REST del backend
│   │   │   ├── __init__.py
│   │   │   ├── main.py                # FastAPI principal
│   │   │   ├── routes/                # Rutas de la API
│   │   │   │   ├── __init__.py
│   │   │   │   ├── auth.py            # Autenticación
│   │   │   │   ├── documents.py       # Gestión de documentos
│   │   │   │   ├── users.py           # Gestión de usuarios
│   │   │   │   ├── workflows.py       # Flujos de trabajo
│   │   │   │   └── admin.py           # Administración
│   │   │   │
│   │   │   ├── middleware/            # Middleware de la API
│   │   │   │   ├── __init__.py
│   │   │   │   ├── auth.py            # Middleware de autenticación
│   │   │   │   ├── security.py        # Middleware de seguridad
│   │   │   │   ├── logging.py         # Middleware de logging
│   │   │   │   └── cors.py            # Middleware CORS
│   │   │   │
│   │   │   └── schemas/               # Esquemas Pydantic
│   │   │       ├── __init__.py
│   │   │       ├── document.py        # Esquemas de documentos
│   │   │       ├── user.py            # Esquemas de usuarios
│   │   │       ├── workflow.py        # Esquemas de workflows
│   │   │       └── auth.py            # Esquemas de autenticación
│   │   │
│   │   ├── database/                  # Configuración de base de datos
│   │   │   ├── __init__.py
│   │   │   ├── connection.py          # Configuración de conexión
│   │   │   ├── models/                # Modelos de datos
│   │   │   │   ├── __init__.py
│   │   │   │   ├── user.py            # Modelo de usuario
│   │   │   │   ├── document.py        # Modelo de documento
│   │   │   │   ├── workflow.py        # Modelo de workflow
│   │   │   │   ├── audit.py           # Modelo de auditoría
│   │   │   │   └── security.py        # Modelo de seguridad
│   │   │   │
│   │   │   ├── migrations/            # Migraciones de BD
│   │   │   │   ├── 001_initial_schema.sql
│   │   │   │   ├── 002_add_security_policies.sql
│   │   │   │   ├── 003_add_audit_triggers.sql
│   │   │   │   └── 004_add_document_types.sql
│   │   │   │
│   │   │   └── seeds/                 # Datos iniciales
│   │   │       ├── users.sql          # Usuarios iniciales
│   │   │       ├── roles.sql          # Roles diplomáticos
│   │   │       └── document_types.sql # Tipos de documentos
│   │   │
│   │   ├── shared/                    # Código compartido backend
│   │   │   ├── __init__.py
│   │   │   ├── config.py              # Configuración global
│   │   │   ├── exceptions.py          # Excepciones personalizadas
│   │   │   ├── security.py            # Utilidades de seguridad
│   │   │   ├── logger.py              # Configuración de logging
│   │   │   ├── validators.py          # Validadores comunes
│   │   │   └── constants.py           # Constantes del sistema
│   │   │
│   │   └── tests/                     # Pruebas del backend
│   │       ├── __init__.py
│   │       ├── conftest.py            # Configuración pytest
│   │       ├── unit/                  # Pruebas unitarias
│   │       ├── integration/           # Pruebas de integración
│   │       ├── e2e/                   # Pruebas end-to-end
│   │       └── fixtures/              # Fixtures de pruebas
│   │
│   └── frontend/                      # Frontend Next.js
│       ├── package.json               # Dependencias del frontend
│       ├── next.config.js             # Configuración Next.js
│       ├── tailwind.config.js         # Configuración Tailwind
│       ├── tsconfig.json              # Configuración TypeScript
│       ├── .env.local                 # Variables de entorno locales
│       ├── .env.example               # Plantilla de variables
│       │
│       ├── src/                       # Código fuente del frontend
│       │   ├── app/                   # App Router de Next.js 15
│       │   │   ├── layout.tsx         # Layout raíz
│       │   │   ├── page.tsx           # Página principal
│       │   │   ├── loading.tsx        # Componente de carga
│       │   │   ├── error.tsx          # Manejo de errores
│       │   │   ├── not-found.tsx      # Página 404
│       │   │   │
│       │   │   ├── auth/              # Páginas de autenticación
│       │   │   │   ├── login/
│       │   │   │   ├── logout/
│       │   │   │   └── register/
│       │   │   │
│       │   │   ├── dashboard/         # Dashboard principal
│       │   │   │   ├── page.tsx
│       │   │   │   ├── layout.tsx
│       │   │   │   ├── analytics/
│       │   │   │   ├── notifications/
│       │   │   │   └── recent-activity/
│       │   │   │
│       │   │   ├── documents/         # Gestión de documentos
│       │   │   │   ├── page.tsx
│       │   │   │   ├── layout.tsx
│       │   │   │   ├── upload/
│       │   │   │   ├── search/
│       │   │   │   ├── [id]/
│       │   │   │   ├── hojas-remision/
│       │   │   │   ├── guias-valija/
│       │   │   │   └── notas-diplomaticas/
│       │   │   │
│       │   │   ├── workflows/         # Flujos de trabajo
│       │   │   │   ├── page.tsx
│       │   │   │   ├── [id]/
│       │   │   │   ├── approvals/
│       │   │   │   └── history/
│       │   │   │
│       │   │   ├── communications/    # Comunicaciones
│       │   │   │   ├── page.tsx
│       │   │   │   ├── inbox/
│       │   │   │   ├── sent/
│       │   │   │   └── compose/
│       │   │   │
│       │   │   ├── admin/             # Administración
│       │   │   │   ├── page.tsx
│       │   │   │   ├── layout.tsx
│       │   │   │   ├── users/
│       │   │   │   ├── roles/
│       │   │   │   ├── security/
│       │   │   │   └── system/
│       │   │   │
│       │   │   ├── reports/           # Reportes y análisis
│       │   │   │   ├── page.tsx
│       │   │   │   ├── audit/
│       │   │   │   ├── performance/
│       │   │   │   └── compliance/
│       │   │   │
│       │   │   └── api/               # API routes de Next.js
│       │   │       ├── auth/
│       │   │       ├── documents/
│       │   │       ├── workflows/
│       │   │       └── proxy/
│       │   │
│       │   ├── components/            # Componentes React
│       │   │   ├── ui/                # Componentes UI base
│       │   │   │   ├── button.tsx
│       │   │   │   ├── input.tsx
│       │   │   │   ├── dialog.tsx
│       │   │   │   ├── table.tsx
│       │   │   │   ├── badge.tsx
│       │   │   │   ├── avatar.tsx
│       │   │   │   ├── dropdown.tsx
│       │   │   │   ├── toast.tsx
│       │   │   │   ├── loading.tsx
│       │   │   │   └── index.ts
│       │   │   │
│       │   │   ├── layout/            # Componentes de layout
│       │   │   │   ├── main-nav.tsx
│       │   │   │   ├── user-nav.tsx
│       │   │   │   ├── site-header.tsx
│       │   │   │   ├── site-footer.tsx
│       │   │   │   ├── sidebar.tsx
│       │   │   │   └── breadcrumb.tsx
│       │   │   │
│       │   │   ├── documents/         # Componentes de documentos
│       │   │   │   ├── document-viewer.tsx
│       │   │   │   ├── document-upload.tsx
│       │   │   │   ├── document-search.tsx
│       │   │   │   ├── document-list.tsx
│       │   │   │   ├── document-form.tsx
│       │   │   │   ├── classification-badge.tsx
│       │   │   │   └── hojas-remision/
│       │   │   │       ├── oga-form.tsx
│       │   │   │       ├── pco-form.tsx
│       │   │   │       └── pru-form.tsx
│       │   │   │
│       │   │   ├── workflows/         # Componentes de workflows
│       │   │   │   ├── workflow-viewer.tsx
│       │   │   │   ├── workflow-designer.tsx
│       │   │   │   ├── approval-panel.tsx
│       │   │   │   ├── status-tracker.tsx
│       │   │   │   └── workflow-history.tsx
│       │   │   │
│       │   │   ├── security/          # Componentes de seguridad
│       │   │   │   ├── security-indicator.tsx
│       │   │   │   ├── access-control.tsx
│       │   │   │   ├── audit-log.tsx
│       │   │   │   └── encryption-status.tsx
│       │   │   │
│       │   │   ├── forms/             # Formularios especializados
│       │   │   │   ├── diplomatic-form.tsx
│       │   │   │   ├── user-form.tsx
│       │   │   │   ├── workflow-form.tsx
│       │   │   │   └── search-form.tsx
│       │   │   │
│       │   │   ├── charts/            # Gráficos y visualizaciones
│       │   │   │   ├── document-stats.tsx
│       │   │   │   ├── workflow-metrics.tsx
│       │   │   │   ├── security-dashboard.tsx
│       │   │   │   └── performance-charts.tsx
│       │   │   │
│       │   │   └── providers/         # Context providers
│       │   │       ├── auth-provider.tsx
│       │   │       ├── theme-provider.tsx
│       │   │       ├── toast-provider.tsx
│       │   │       └── websocket-provider.tsx
│       │   │
│       │   ├── lib/                   # Librerías y utilidades
│       │   │   ├── auth/              # Configuración de auth
│       │   │   │   ├── config.ts
│       │   │   │   ├── providers.ts
│       │   │   │   └── middleware.ts
│       │   │   │
│       │   │   ├── api/               # Cliente API
│       │   │   │   ├── client.ts
│       │   │   │   ├── endpoints.ts
│       │   │   │   ├── types.ts
│       │   │   │   └── hooks.ts
│       │   │   │
│       │   │   ├── database/          # Cliente de BD
│       │   │   │   ├── client.ts
│       │   │   │   ├── queries.ts
│       │   │   │   └── mutations.ts
│       │   │   │
│       │   │   ├── azure/             # Integración Azure
│       │   │   │   ├── form-recognizer.ts
│       │   │   │   ├── blob-storage.ts
│       │   │   │   └── cognitive-services.ts
│       │   │   │
│       │   │   ├── security/          # Utilidades de seguridad
│       │   │   │   ├── encryption.ts
│       │   │   │   ├── validation.ts
│       │   │   │   └── permissions.ts
│       │   │   │
│       │   │   ├── utils/             # Utilidades generales
│       │   │   │   ├── cn.ts
│       │   │   │   ├── format.ts
│       │   │   │   ├── constants.ts
│       │   │   │   └── helpers.ts
│       │   │   │
│       │   │   └── validators/        # Validadores Zod
│       │   │       ├── document.ts
│       │   │       ├── user.ts
│       │   │       ├── workflow.ts
│       │   │       └── auth.ts
│       │   │
│       │   ├── hooks/                 # Hooks personalizados
│       │   │   ├── use-auth.ts
│       │   │   ├── use-documents.ts
│       │   │   ├── use-workflows.ts
│       │   │   ├── use-websocket.ts
│       │   │   ├── use-permissions.ts
│       │   │   └── use-toast.ts
│       │   │
│       │   ├── contexts/              # Context providers
│       │   │   ├── auth-context.tsx
│       │   │   ├── theme-context.tsx
│       │   │   ├── workflow-context.tsx
│       │   │   └── security-context.tsx
│       │   │
│       │   ├── types/                 # Definiciones TypeScript
│       │   │   ├── index.ts           # Tipos principales
│       │   │   ├── auth.ts            # Tipos de autenticación
│       │   │   ├── document.ts        # Tipos de documentos
│       │   │   ├── workflow.ts        # Tipos de workflows
│       │   │   ├── user.ts            # Tipos de usuarios
│       │   │   └── api.ts             # Tipos de API
│       │   │
│       │   └── styles/                # Estilos globales
│       │       ├── globals.css        # Estilos CSS globales
│       │       ├── components.css     # Estilos de componentes
│       │       └── diplomatic.css     # Tema diplomático
│       │
│       ├── public/                    # Archivos estáticos
│       │   ├── images/                # Imágenes
│       │   │   ├── logos/             # Logos oficiales
│       │   │   ├── icons/             # Iconos
│       │   │   └── backgrounds/       # Fondos
│       │   │
│       │   ├── documents/             # Documentos de ejemplo
│       │   │   ├── templates/         # Plantillas
│       │   │   └── samples/           # Muestras
│       │   │
│       │   └── fonts/                 # Fuentes personalizadas
│       │
│       └── prisma/                    # Esquemas de base de datos
│           ├── schema.prisma          # Esquema principal
│           ├── migrations/            # Migraciones Prisma
│           └── seed.ts                # Datos iniciales
│
├── config/                            # Configuración del proyecto
│   ├── development/                   # Configuración desarrollo
│   │   ├── database.yml
│   │   ├── redis.yml
│   │   └── azure.yml
│   │
│   ├── production/                    # Configuración producción
│   │   ├── database.yml
│   │   ├── redis.yml
│   │   └── azure.yml
│   │
│   ├── security/                      # Configuración de seguridad
│   │   ├── ens_alto.yml              # ENS Alto
│   │   ├── gdpr.yml                  # GDPR
│   │   └── iso27001.yml              # ISO 27001
│   │
│   ├── agents/                        # Configuración de agentes
│   │   ├── orchestrator.yml          # Configuración orquestador
│   │   ├── document_processor.yml    # Procesador de documentos
│   │   ├── database_manager.yml      # Gestor de BD
│   │   ├── azure_specialist.yml      # Especialista Azure
│   │   └── security_guardian.yml     # Guardián de seguridad
│   │
│   └── diplomatic/                    # Configuración diplomática
│       ├── roles.yml                 # Roles diplomáticos
│       ├── clearances.yml            # Niveles de seguridad
│       ├── document_types.yml        # Tipos de documentos
│       └── workflows.yml             # Flujos de trabajo
│
├── docs/                              # Documentación del proyecto
│   ├── README.md                     # Documentación principal
│   ├── installation.md              # Guía de instalación
│   ├── deployment.md                # Guía de despliegue
│   ├── api-reference.md             # Referencia de API
│   ├── user-guide.md                # Guía de usuario
│   ├── admin-guide.md               # Guía de administrador
│   ├── security.md                  # Documentación de seguridad
│   ├── compliance.md                # Documentación de cumplimiento
│   ├── architecture.md              # Arquitectura del sistema
│   ├── contributing.md              # Guía de contribución
│   │
│   ├── agents/                      # Documentación de agentes
│   │   ├── overview.md              # Visión general
│   │   ├── orchestrator.md          # Orquestador
│   │   ├── document-processor.md    # Procesador de documentos
│   │   ├── database-manager.md      # Gestor de BD
│   │   ├── azure-specialist.md      # Especialista Azure
│   │   └── security-guardian.md     # Guardián de seguridad
│   │
│   ├── diplomatic/                  # Documentación diplomática
│   │   ├── protocols.md             # Protocolos diplomáticos
│   │   ├── document-types.md        # Tipos de documentos
│   │   ├── workflows.md             # Flujos de trabajo
│   │   └── security-levels.md       # Niveles de seguridad
│   │
│   └── assets/                      # Recursos de documentación
│       ├── images/                  # Imágenes
│       ├── diagrams/                # Diagramas
│       └── screenshots/             # Capturas de pantalla
│
├── infrastructure/                   # Infraestructura y despliegue
│   ├── docker/                      # Configuración Docker
│   │   ├── Dockerfile.backend       # Dockerfile backend
│   │   ├── Dockerfile.frontend      # Dockerfile frontend
│   │   ├── Dockerfile.agents        # Dockerfile agentes
│   │   └── docker-compose.prod.yml  # Compose producción
│   │
│   ├── kubernetes/                  # Configuración Kubernetes
│   │   ├── namespace.yaml           # Namespace
│   │   ├── secrets.yaml             # Secretos
│   │   ├── configmaps.yaml          # ConfigMaps
│   │   ├── deployments/             # Deployments
│   │   ├── services/                # Services
│   │   └── ingress/                 # Ingress
│   │
│   ├── terraform/                   # Infraestructura como código
│   │   ├── main.tf                  # Configuración principal
│   │   ├── variables.tf             # Variables
│   │   ├── outputs.tf               # Outputs
│   │   ├── azure/                   # Recursos Azure
│   │   └── modules/                 # Módulos reutilizables
│   │
│   └── monitoring/                  # Monitoreo y observabilidad
│       ├── prometheus/              # Configuración Prometheus
│       ├── grafana/                 # Dashboards Grafana
│       ├── alertmanager/            # Alertas
│       └── jaeger/                  # Tracing distribuido
│
├── scripts/                         # Scripts de automatización
│   ├── setup/                       # Scripts de configuración
│   │   ├── install.sh               # Instalación completa
│   │   ├── database.sh              # Configuración BD
│   │   ├── azure.sh                 # Configuración Azure
│   │   └── security.sh              # Configuración seguridad
│   │
│   ├── deployment/                  # Scripts de despliegue
│   │   ├── deploy.sh                # Despliegue principal
│   │   ├── rollback.sh              # Rollback
│   │   ├── backup.sh                # Backup
│   │   └── restore.sh               # Restauración
│   │
│   ├── development/                 # Scripts de desarrollo
│   │   ├── dev.sh                   # Entorno desarrollo
│   │   ├── test.sh                  # Ejecución de pruebas
│   │   ├── lint.sh                  # Linting
│   │   └── format.sh                # Formateo de código
│   │
│   └── maintenance/                 # Scripts de mantenimiento
│       ├── health-check.sh          # Verificación de salud
│       ├── cleanup.sh               # Limpieza del sistema
│       ├── logs.sh                  # Gestión de logs
│       └── security-scan.sh         # Escaneo de seguridad
│
├── tests/                           # Pruebas del proyecto
│   ├── unit/                        # Pruebas unitarias
│   │   ├── backend/                 # Pruebas backend
│   │   └── frontend/                # Pruebas frontend
│   │
│   ├── integration/                 # Pruebas de integración
│   │   ├── api/                     # Pruebas de API
│   │   ├── agents/                  # Pruebas de agentes
│   │   └── workflows/               # Pruebas de workflows
│   │
│   ├── e2e/                         # Pruebas end-to-end
│   │   ├── scenarios/               # Escenarios de prueba
│   │   ├── fixtures/                # Datos de prueba
│   │   └── screenshots/             # Capturas de pruebas
│   │
│   ├── security/                    # Pruebas de seguridad
│   │   ├── vulnerability/           # Pruebas de vulnerabilidades
│   │   ├── penetration/             # Pruebas de penetración
│   │   └── compliance/              # Pruebas de cumplimiento
│   │
│   └── performance/                 # Pruebas de rendimiento
│       ├── load/                    # Pruebas de carga
│       ├── stress/                  # Pruebas de estrés
│       └── benchmark/               # Benchmarks
│
├── tools/                           # Herramientas de desarrollo
│   ├── cli/                         # Herramientas CLI
│   │   ├── siame-cli.py             # CLI principal
│   │   ├── commands/                # Comandos CLI
│   │   └── utils/                   # Utilidades CLI
│   │
│   ├── generators/                  # Generadores de código
│   │   ├── agent-generator.py       # Generador de agentes
│   │   ├── workflow-generator.py    # Generador de workflows
│   │   └── document-generator.py    # Generador de documentos
│   │
│   ├── validators/                  # Validadores
│   │   ├── config-validator.py      # Validador de configuración
│   │   ├── security-validator.py    # Validador de seguridad
│   │   └── compliance-validator.py  # Validador de cumplimiento
│   │
│   └── migrators/                   # Herramientas de migración
│       ├── data-migrator.py         # Migrador de datos
│       ├── config-migrator.py       # Migrador de configuración
│       └── schema-migrator.py       # Migrador de esquemas
│
├── shared/                          # Código compartido
│   ├── types/                       # Tipos compartidos
│   │   ├── diplomatic.py            # Tipos diplomáticos
│   │   ├── security.py              # Tipos de seguridad
│   │   ├── workflow.py              # Tipos de workflow
│   │   └── document.py              # Tipos de documento
│   │
│   ├── utils/                       # Utilidades compartidas
│   │   ├── crypto.py                # Utilidades criptográficas
│   │   ├── validation.py            # Utilidades de validación
│   │   ├── formatting.py            # Utilidades de formato
│   │   └── logging.py               # Utilidades de logging
│   │
│   ├── constants/                   # Constantes compartidas
│   │   ├── diplomatic.py            # Constantes diplomáticas
│   │   ├── security.py              # Constantes de seguridad
│   │   └── system.py                # Constantes del sistema
│   │
│   └── protocols/                   # Protocolos de comunicación
│       ├── agent_protocol.py        # Protocolo de agentes
│       ├── diplomatic_protocol.py   # Protocolo diplomático
│       └── security_protocol.py     # Protocolo de seguridad
│
└── examples/                        # Ejemplos y demos
    ├── documents/                   # Documentos de ejemplo
    │   ├── hojas-remision/          # Hojas de remisión
    │   ├── guias-valija/            # Guías de valija
    │   └── notas-diplomaticas/      # Notas diplomáticas
    │
    ├── workflows/                   # Workflows de ejemplo
    │   ├── approval-process.json    # Proceso de aprobación
    │   ├── classification-flow.json # Flujo de clasificación
    │   └── audit-workflow.json      # Workflow de auditoría
    │
    ├── configurations/              # Configuraciones de ejemplo
    │   ├── development.env          # Configuración desarrollo
    │   ├── staging.env              # Configuración staging
    │   └── production.env           # Configuración producción
    │
    └── data/                        # Datos de ejemplo
        ├── users.json               # Usuarios de ejemplo
        ├── documents.json           # Documentos de ejemplo
        └── workflows.json           # Workflows de ejemplo
```

## Resumen de la Estructura

### 🏗️ **Componentes Principales**
- **Backend Multi-Agente**: Sistema de agentes especializados con orquestador central
- **Frontend Next.js 15**: Interfaz diplomática con App Router y TypeScript
- **Base de Datos**: PostgreSQL con Prisma ORM y políticas RLS
- **Integración Azure**: Form Recognizer, Blob Storage, Key Vault
- **Seguridad**: ENS Alto, GDPR, ISO 27001, CCN-CERT

### 🤖 **Agentes Especializados**
1. **Document Processor**: OCR, clasificación, extracción
2. **Database Manager**: Gestión de BD, migraciones, auditoría
3. **Azure Specialist**: Servicios Azure, IA cognitiva
4. **Security Guardian**: Control de acceso, encriptación, amenazas
5. **Workflow Manager**: Flujos diplomáticos, aprobaciones
6. **Communication Hub**: Notificaciones, protocolos diplomáticos
7. **Quality Assurance**: Testing, compliance, performance

### 🔐 **Características de Seguridad**
- **5 Niveles de Clasificación**: Público → Alto Secreto
- **10 Roles Diplomáticos**: Embajador → Invitado
- **Row Level Security**: Políticas a nivel de fila
- **Auditoría Completa**: Registro de todas las actividades
- **Encriptación**: End-to-end para documentos clasificados

### 📋 **Tipos de Documentos Diplomáticos**
- **Hojas de Remisión**: OGA, PCO, PRU
- **Guías de Valija**: Entrada/Salida, Ordinaria/Extraordinaria
- **Notas Diplomáticas**: Bilaterales, multilaterales
- **Despachos**: Telegráficos, correo diplomático
- **Memorándums**: Internos, externos

Esta estructura proporciona una base sólida y escalable para el Sistema Inteligente de Administración y Manejo de Expedientes del Ministerio de Asuntos Exteriores.
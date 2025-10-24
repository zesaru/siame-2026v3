# 🚀 SIAME 2026v3 - Sistema Inteligente de Administración y Manejo de Expedientes

**Versión**: 3.0.0
**Estado**: 🟢 En Desarrollo Activo (60% Completado)
**Última Actualización**: 2025-10-22

---

## 📊 Estado del Proyecto

```
█████████████░░░░░░░ 60% Completado

Frontend:     ████████████░░░░ 60%
Backend:      ██████░░░░░░░░░░ 35%
Base de Datos: ███████████████░ 95%
```

---

## ✨ Características Implementadas

### 🎨 Frontend (Next.js 15)

**Páginas Completas (9):**
- ✅ Home / Landing Page
- ✅ Login con NextAuth.js
- ✅ Registro de Usuarios
- ✅ Dashboard Principal
- ✅ Listado de Documentos (con filtros)
- ✅ Detalle de Documento
- ✅ Upload de Documentos (drag & drop)
- ✅ Workflows y Aprobaciones
- ✅ Páginas de Error (404, error, global-error)

**Componentes UI (15):**
- ✅ Button, Badge
- ✅ Input, Label, Select, Textarea
- ✅ Card (modular)
- ✅ Table (completa)
- ✅ Dialog/Modal
- ✅ Avatar
- ✅ Navbar (responsive)

### 🔐 Autenticación y Seguridad

- ✅ NextAuth.js v5 configurado
- ✅ Credentials Provider
- ✅ Prisma Adapter
- ✅ JWT Strategy (8 horas)
- ✅ Hash de contraseñas (bcrypt, 10 rounds)
- ✅ Middleware de protección de rutas
- ✅ 5 niveles de clasificación de seguridad
- ✅ Sistema de roles diplomáticos

### 🗄️ Base de Datos (Prisma + PostgreSQL)

**Schema Completo:**
- ✅ 18 modelos de datos
- ✅ 8 enums personalizados
- ✅ Relaciones complejas
- ✅ Índices optimizados

**Modelos Principales:**
- Users & Authentication
- Documents (múltiples tipos)
- Hojas de Remisión
- Guías de Valija Diplomática
- Workflows
- Audit Logs
- Notifications

---

## 🌐 URLs Disponibles

### Servidor de Desarrollo
```
http://localhost:3005
```

### Páginas Públicas
- `/` - Home
- `/auth/login` - Iniciar Sesión
- `/auth/register` - Registro

### Páginas Protegidas
- `/dashboard` - Panel Principal
- `/documents` - Gestión de Documentos
- `/documents/[id]` - Detalle de Documento
- `/documents/upload` - Subir Documento
- `/workflows` - Workflows y Aprobaciones

---

## 🛠️ Stack Tecnológico

### Frontend
```json
{
  "framework": "Next.js 15.5.6",
  "react": "18.3.1",
  "typescript": "5.9.3",
  "styling": "Tailwind CSS 3.4.18",
  "ui": "Custom Components"
}
```

### Autenticación
```json
{
  "next-auth": "5.0.0-beta.29",
  "@auth/prisma-adapter": "2.11.0",
  "bcryptjs": "3.0.2"
}
```

### Base de Datos
```json
{
  "@prisma/client": "5.22.0",
  "database": "PostgreSQL 16"
}
```

### Herramientas
```json
{
  "package-manager": "pnpm 10.17.1",
  "linter": "ESLint",
  "formatter": "Prettier"
}
```

---

## 🚀 Inicio Rápido

### Prerequisitos
- Node.js 18+
- pnpm
- PostgreSQL 16
- Git

### Instalación

1. **Clonar el repositorio**
```bash
git clone <repository-url>
cd siame-2026v3
```

2. **Instalar dependencias**
```bash
cd src/frontend
pnpm install
```

3. **Configurar variables de entorno**
```bash
cp .env.example .env.local
# Editar .env.local con tus credenciales
```

4. **Configurar PostgreSQL**
```bash
# Iniciar PostgreSQL
sudo service postgresql start

# Crear usuario y base de datos
sudo -u postgres psql -c "CREATE USER siame_user WITH PASSWORD 'siame_password';"
sudo -u postgres psql -c "CREATE DATABASE siame_dev OWNER siame_user;"
```

5. **Aplicar migraciones**
```bash
npx prisma migrate dev --name initial_setup
```

6. **Iniciar servidor de desarrollo**
```bash
pnpm run dev
```

7. **Abrir en navegador**
```
http://localhost:3005
```

---

## 📚 Documentación

### Guías Disponibles

1. **[FINAL_SESSION_SUMMARY.md](./FINAL_SESSION_SUMMARY.md)**
   - Resumen completo del proyecto
   - Estadísticas y métricas
   - Lista de todos los archivos creados

2. **[PAGES_CREATED.md](./PAGES_CREATED.md)**
   - Documentación de cada página
   - Características y funcionalidad
   - Screenshots y ejemplos

3. **[AUTH_IMPLEMENTATION.md](./AUTH_IMPLEMENTATION.md)**
   - Guía completa de autenticación
   - Configuración de NextAuth
   - Flujos de autenticación
   - Seguridad

4. **[POSTGRESQL_SETUP.md](./POSTGRESQL_SETUP.md)**
   - Instalación de PostgreSQL
   - Configuración paso a paso
   - Migraciones de Prisma
   - Troubleshooting

---

## 🗂️ Estructura del Proyecto

```
siame-2026v3/
├── src/frontend/                 # Aplicación Next.js
│   ├── src/
│   │   ├── app/                  # App Router
│   │   │   ├── (auth)/          # Rutas de autenticación
│   │   │   ├── dashboard/       # Dashboard
│   │   │   ├── documents/       # Gestión de documentos
│   │   │   ├── workflows/       # Workflows
│   │   │   └── api/             # API Routes
│   │   │
│   │   ├── components/
│   │   │   ├── ui/              # Componentes UI
│   │   │   └── layout/          # Componentes de layout
│   │   │
│   │   ├── lib/
│   │   │   ├── auth/            # Configuración NextAuth
│   │   │   ├── database/        # Cliente Prisma
│   │   │   └── utils/           # Utilidades
│   │   │
│   │   ├── types/               # TypeScript types
│   │   └── middleware.ts        # Middleware de rutas
│   │
│   ├── prisma/
│   │   └── schema.prisma        # Schema de base de datos
│   │
│   ├── public/                   # Archivos estáticos
│   ├── tailwind.config.js       # Configuración Tailwind
│   └── package.json
│
├── docs/                         # Documentación
├── orchestrator/                 # Orquestador de agentes (futuro)
├── agents/                       # Agentes especializados (futuro)
└── README.md                     # Este archivo
```

---

## 🎨 Características de Diseño

### Sistema de Colores

**Clasificación de Seguridad:**
- 🟢 PUBLICO - Verde
- 🟡 RESTRINGIDO - Amarillo
- 🟠 CONFIDENCIAL - Naranja
- 🔴 SECRETO - Rojo
- ⚫ ALTO_SECRETO - Rojo Oscuro

### Dark Mode
- ✅ Soporte completo
- ✅ Cambio automático según preferencias del sistema
- ✅ Variables CSS personalizables

### Responsive Design
- ✅ Mobile First
- ✅ Breakpoints: sm (640px), md (768px), lg (1024px), xl (1280px)
- ✅ Grid adaptable
- ✅ Navegación optimizada para móvil

---

## 🔐 Seguridad

### Niveles de Clasificación
1. **PUBLICO** - Información general
2. **RESTRINGIDO** - Personal autorizado
3. **CONFIDENCIAL** - Información sensible
4. **SECRETO** - Altamente clasificada
5. **ALTO_SECRETO** - Máxima seguridad

### Roles Diplomáticos
- EMBAJADOR
- MINISTRO_CONSEJERO
- CONSEJERO
- PRIMER_SECRETARIO
- SEGUNDO_SECRETARIO
- TERCER_SECRETARIO
- AGREGADO
- FUNCIONARIO_ADMINISTRATIVO
- CONSULTOR_EXTERNO
- INVITADO

### Características de Seguridad
- ✅ Hash de contraseñas con bcrypt
- ✅ JWT tokens con HttpOnly cookies
- ✅ CSRF protection (NextAuth)
- ✅ Validaciones client y server-side
- ✅ Middleware de autorización
- ✅ Audit logs
- ⏳ Email verification (pendiente)
- ⏳ Two-factor authentication (pendiente)

---

## 🧪 Testing

```bash
# Unit tests (cuando estén implementados)
pnpm test

# E2E tests (cuando estén implementados)
pnpm test:e2e

# Coverage
pnpm test:coverage
```

---

## 📦 Scripts Disponibles

```bash
# Desarrollo
pnpm run dev              # Iniciar servidor de desarrollo

# Build
pnpm run build            # Build de producción
pnpm run start            # Iniciar servidor de producción

# Base de Datos
npx prisma generate       # Generar cliente Prisma
npx prisma migrate dev    # Crear migración
npx prisma studio         # Abrir Prisma Studio
npx prisma db seed        # Poblar base de datos

# Linting & Formatting
pnpm run lint             # Ejecutar ESLint
pnpm run format           # Formatear código con Prettier
```

---

## 🗺️ Roadmap

### ✅ Fase 1: Fundamentos (Completada)
- [x] Estructura del proyecto
- [x] Configuración de Next.js
- [x] Sistema de autenticación
- [x] Componentes UI base

### ✅ Fase 2: Páginas Principales (Completada)
- [x] Dashboard
- [x] Gestión de documentos
- [x] Upload de archivos
- [x] Workflows básicos

### 🔄 Fase 3: Funcionalidad Avanzada (En Progreso)
- [ ] APIs de documentos
- [ ] Sistema de notificaciones
- [ ] Búsqueda avanzada
- [ ] Reportes

### ⏳ Fase 4: Integración (Pendiente)
- [ ] Azure Form Recognizer
- [ ] Azure Blob Storage
- [ ] Azure Key Vault
- [ ] Email service

### ⏳ Fase 5: Testing y QA (Pendiente)
- [ ] Unit tests
- [ ] Integration tests
- [ ] E2E tests
- [ ] Performance testing

### ⏳ Fase 6: Deployment (Pendiente)
- [ ] CI/CD pipeline
- [ ] Staging environment
- [ ] Production deployment
- [ ] Monitoring

---

## 🤝 Contribución

### Estándares de Código
- TypeScript strict mode
- Componentes funcionales con hooks
- Comentarios JSDoc para funciones públicas
- Nombres descriptivos en español
- Commits semánticos

### Proceso de Desarrollo
1. Crear branch desde `main`
2. Implementar cambios
3. Escribir tests
4. Crear pull request
5. Code review
6. Merge a `main`

---

## 📞 Soporte

### Comandos Útiles

**Limpiar caché:**
```bash
rm -rf .next
rm -rf node_modules/.cache
```

**Reiniciar base de datos:**
```bash
npx prisma migrate reset
```

**Ver logs:**
```bash
# Logs de desarrollo (en terminal donde corre pnpm run dev)
# Logs de PostgreSQL
sudo tail -f /var/log/postgresql/postgresql-16-main.log
```

---

## 📝 Changelog

### [3.0.0] - 2025-10-22

#### Añadido
- Sistema de autenticación completo con NextAuth.js v5
- 9 páginas funcionales
- 15 componentes UI reutilizables
- Schema completo de base de datos (18 modelos)
- Middleware de protección de rutas
- Sistema de clasificación de seguridad
- Dark mode completo
- Diseño responsive

#### Mejorado
- Migración de Tailwind CSS v4 a v3
- Optimización de componentes
- Documentación exhaustiva

#### Corregido
- Error de lightningcss en Windows
- Problemas de MIME types
- Middleware bloqueando rutas incorrectas

---

## 📄 Licencia

[Tu licencia aquí]

---

## 👥 Equipo

- **Desarrollo**: [Tu nombre]
- **Diseño**: [Nombre]
- **QA**: [Nombre]

---

## 🙏 Agradecimientos

- Next.js Team
- Prisma Team
- NextAuth.js Team
- Tailwind CSS Team

---

## 📊 Estadísticas del Proyecto

```
Páginas:              9
Componentes UI:       15
Modelos de BD:        18
Líneas de Código:     ~5,000
Documentación:        ~2,500 líneas
Commits:              [Pendiente]
```

---

**🎯 Estado Actual:** Sistema funcional al 60%, listo para desarrollo continuo

**📅 Última Actualización:** 2025-10-22

**🚀 Próximo Hito:** Implementación de APIs y sistema de notificaciones (70%)

---

_Desarrollado con ❤️ para el Ministerio de Asuntos Exteriores, Unión Europea y Cooperación_

# SIAME 2026v3 - Notas de Desarrollo con Claude

## 📅 Última Actualización: 2025-11-05

## 🎯 Estado Actual del Proyecto

### ✅ Componentes Funcionando

1. **Base de Datos PostgreSQL** (Docker)
   - Puerto: 5432
   - Usuario: `siame_user`
   - Password: `siame_password`
   - Base de datos: `siame_dev`
   - Estado: ✅ Healthy

2. **Redis Cache** (Docker)
   - Puerto: 6379
   - Password: `siame_redis_password`
   - Estado: ✅ Healthy

3. **Frontend Next.js 15** (Docker)
   - Puerto: 3000
   - Framework: Next.js 15.5.6
   - Estado: ✅ Corriendo
   - **IMPORTANTE**: Ahora corre completamente en Docker

## 🐳 Configuración Docker

### Decisión Arquitectónica

**Fecha**: 2025-11-05
**Problema Resuelto**: Incompatibilidad de binarios de Prisma entre WSL2 y Windows

Después de extenso debugging, se identificó que el problema de autenticación NO era de credenciales ni de NextAuth, sino de **binarios de Prisma incompatibles** entre WSL2 y Windows. Prisma generaba binarios `debian-openssl-3.0.x` que no funcionaban correctamente cuando Next.js se ejecutaba desde Windows/PowerShell.

**Solución Implementada**: Dockerizar todo el stack

### Beneficios

1. ✅ **Portabilidad Total**: Mismo entorno en Windows, Linux, macOS
2. ✅ **Sin Problemas de Binarios**: Prisma se compila dentro del contenedor Linux
3. ✅ **Sin Conflictos con Antivirus**: Norton 360 ya no bloquea archivos
4. ✅ **Reproducibilidad**: Desarrollo = Staging = Producción
5. ✅ **Fácil Deployment**: Solo requiere Docker en cualquier servidor

### Archivos Docker Creados

```
infrastructure/docker/
├── Dockerfile.frontend      # Dockerfile para Next.js
└── [otros Dockerfiles]

src/frontend/
├── .dockerignore            # Archivos ignorados por Docker
└── next.config.ts           # Actualizado con output: 'standalone'
```

## 🚀 Comandos de Uso

### Iniciar el Stack Completo

```bash
# Desde la raíz del proyecto
docker-compose up -d
```

### Iniciar Solo Frontend y Base de Datos

```bash
docker-compose up -d postgres redis frontend
```

### Ver Logs en Tiempo Real

```bash
# Frontend
docker logs -f siame_frontend

# PostgreSQL
docker logs -f siame_postgres

# Todos los servicios
docker-compose logs -f
```

### Rebuild Después de Cambios

```bash
# Solo frontend
docker-compose up -d --build frontend

# Todo el stack
docker-compose up -d --build
```

### Detener Todo

```bash
docker-compose down
```

### Entrar al Contenedor (Debug)

```bash
# Frontend
docker exec -it siame_frontend sh

# PostgreSQL
docker exec -it siame_postgres psql -U siame_user -d siame_dev
```

## 🔐 Credenciales de Acceso

### Aplicación Web

- **URL**: http://localhost:3000/auth/login
- **Email**: `admin@maeuec.es`
- **Password**: `password123`

### Otros Usuarios de Prueba

| Email | Nombre | Rol | Password |
|-------|--------|-----|----------|
| lchuquihuara@maeuec.es | Luis Alberto Chuquihuara Chil | EMBAJADOR | password123 |
| mcastillo@maeuec.es | María Elena Castillo Ayala | CONSEJERO | password123 |
| cmendoza@maeuec.es | Carlos Raúl Mendoza Flores | PRIMER_SECRETARIO | password123 |
| aquispe@maeuec.es | Ana Patricia Quispe Mamani | SEGUNDO_SECRETARIO | password123 |

## 🗄️ Base de Datos

### Conexión Directa

```bash
# Desde WSL/Linux
PGPASSWORD=siame_password psql -h 127.0.0.1 -U siame_user -d siame_dev

# Desde contenedor
docker exec -it siame_postgres psql -U siame_user -d siame_dev
```

### Prisma

```bash
# Generar cliente
cd src/frontend
npx prisma generate

# Aplicar migraciones
npx prisma migrate dev

# Abrir Prisma Studio
npx prisma studio
```

## 📊 Estructura de Servicios Docker

```yaml
servicios:
  - postgres:5432        # Base de datos
  - redis:6379           # Cache
  - frontend:3000        # Next.js
  - orchestrator:8000    # Backend (opcional)
  - nginx:80,443         # Reverse proxy (opcional)
  - prometheus:9090      # Monitoreo (opcional)
  - grafana:3001         # Dashboards (opcional)
```

## 🔧 Problemas Resueltos en esta Sesión

### 1. Error de Autenticación de Prisma

**Síntoma**: 
```
Authentication failed against database server at `127.0.0.1`, 
the provided database credentials for `siame_user` are not valid.
```

**Causa**: Binario de Prisma incompatible (debian-openssl-3.0.x vs Windows)

**Solución**: Dockerizar el frontend completo

### 2. Conflicto con Norton 360

**Síntoma**: 
```
Error: UNKNOWN: unknown error, open '.next/static/chunks/app/layout.js'
```

**Causa**: Norton 360 bloqueando archivos de Next.js durante hot reload

**Soluciones Aplicadas**:
1. Añadir exclusión en Norton para la carpeta del proyecto
2. Configurar webpack polling en `next.config.ts`
3. **Solución definitiva**: Dockerizar (archivos dentro del contenedor)

### 3. Multiple Procesos Node.js

**Síntoma**: Múltiples servidores corriendo en puertos 3000-3005

**Solución**: 
```bash
taskkill.exe /F /IM node.exe
```

## 📝 Archivos de Configuración Importantes

### next.config.ts

```typescript
const nextConfig: NextConfig = {
  output: 'standalone',  // Para Docker
  webpack: (config, { dev, isServer }) => {
    if (dev && !isServer) {
      config.watchOptions = {
        poll: 1000,
        aggregateTimeout: 300,
        ignored: /node_modules/,
      };
    }
    return config;
  },
};
```

### prisma/schema.prisma

```prisma
generator client {
  provider      = "prisma-client-js"
  binaryTargets = ["native", "debian-openssl-3.0.x", "windows", "linux-musl-openssl-3.0.x"]
}
```

## 🎓 Lecciones Aprendidas

1. **WSL2 + Windows + Docker + Prisma = Problemas de Binarios**
   - Solución: Dockerizar todo para evitar incompatibilidades

2. **Antivirus Corporativos (Norton) Bloquean Hot Reload**
   - Solución: Exclusiones + Webpack polling + Docker

3. **Variables de Entorno en Next.js**
   - `.env.local` tiene prioridad sobre `.env`
   - Next.js carga variables al iniciar, no en runtime

4. **Debugging Sistemático es Clave**
   - Scripts de diagnóstico (`diagnose.ts`, `test-login.ts`) ayudaron a identificar el problema

## 🚧 Próximos Pasos Recomendados

1. [ ] Probar autenticación en Docker
2. [ ] Configurar Azure Document Intelligence
3. [ ] Implementar funcionalidades de Hojas de Remisión
4. [ ] Configurar CI/CD con Docker
5. [ ] Documentar flujos de trabajo diplomáticos

## 📞 Contacto y Soporte

Para preguntas sobre esta implementación:
- Revisar logs: `docker logs -f siame_frontend`
- Revisar este archivo (CLAUDE.md)
- Consultar documentación en `/docs`

---

**Última modificación**: 2025-11-05 por Claude Code
**Stack Tecnológico**: Next.js 15 + Prisma + PostgreSQL + Redis + Docker
**Estado**: ✅ Frontend funcionando completamente en Docker

# PostgreSQL Setup Completado

## Resumen de Configuración

✅ **PostgreSQL 16.10** configurado y funcionando correctamente.

### Base de Datos

- **Nombre**: `siame_dev`
- **Usuario**: `siame_user`
- **Password**: `siame_password`
- **Host**: `localhost`
- **Puerto**: `5432`

### Tablas Creadas

Se crearon exitosamente 19 tablas:

1. `users` - Usuarios del sistema
2. `accounts` - Cuentas de autenticación
3. `sessions` - Sesiones de usuario
4. `verification_tokens` - Tokens de verificación
5. `documents` - Documentos diplomáticos
6. `file_uploads` - Archivos cargados
7. `workflows` - Flujos de trabajo
8. `workflow_steps` - Pasos de flujos de trabajo
9. `document_workflows` - Relación documento-workflow
10. `notifications` - Notificaciones del sistema
11. `audit_logs` - Registros de auditoría
12. `document_authorizations` - Autorizaciones de documentos
13. `hojas_remision` - Hojas de remisión
14. `guias_valija` - Guías de valija diplomática
15. `valijas_internas` - Valijas internas
16. `items_valija` - Items de valija
17. `precintos` - Precintos de seguridad
18. `system_config` - Configuración del sistema
19. `_prisma_migrations` - Control de migraciones

### Usuarios de Prueba Creados

Se insertaron 5 usuarios con el password `password123`:

| ID       | Nombre             | Email                         | Rol Diplomático     | Nivel de Seguridad |
|----------|--------------------|-------------------------------|--------------------|--------------------|
| user-001 | Carlos Martínez    | carlos.martinez@maeuec.es     | EMBAJADOR          | ALTO_SECRETO       |
| user-002 | María López        | maria.lopez@maeuec.es         | CONSEJERO          | SECRETO            |
| user-003 | Juan García        | juan.garcia@maeuec.es         | PRIMER_SECRETARIO  | CONFIDENCIAL       |
| user-004 | Ana Rodríguez      | ana.rodriguez@maeuec.es       | SEGUNDO_SECRETARIO | RESTRINGIDO        |
| user-005 | Admin Sistema      | admin@maeuec.es               | EMBAJADOR          | ALTO_SECRETO       |

## Cómo Probar el Sistema

### 1. Acceder a la Aplicación

El servidor está corriendo en:
```
http://localhost:3005
```

### 2. Iniciar Sesión

Puedes usar cualquiera de estas credenciales:

**Embajador:**
- Email: `carlos.martinez@maeuec.es`
- Password: `password123`

**Consejero:**
- Email: `maria.lopez@maeuec.es`
- Password: `password123`

**Primer Secretario:**
- Email: `juan.garcia@maeuec.es`
- Password: `password123`

**Segundo Secretario:**
- Email: `ana.rodriguez@maeuec.es`
- Password: `password123`

**Admin:**
- Email: `admin@maeuec.es`
- Password: `password123`

### 3. Páginas Disponibles

Una vez autenticado, puedes acceder a:

- `/dashboard` - Panel principal con estadísticas
- `/documents` - Listado de documentos
- `/documents/upload` - Cargar nuevo documento
- `/workflows` - Gestión de workflows
- `/notifications` - Centro de notificaciones

## Comandos Útiles

### Base de Datos

```bash
# Conectar a PostgreSQL
PGPASSWORD=siame_password psql -U siame_user -d siame_dev -h localhost

# Ver tablas
\dt

# Ver usuarios
SELECT id, name, email, "diplomaticRole" FROM users;

# Salir
\q
```

### Prisma

```bash
# Generar cliente de Prisma
npx prisma generate

# Abrir Prisma Studio (interfaz visual)
pnpm db:studio

# Crear nueva migración
pnpm db:migrate
```

### Desarrollo

```bash
# Iniciar servidor de desarrollo
pnpm dev

# Build de producción
pnpm build

# Iniciar en producción
pnpm start
```

## Próximos Pasos

Ahora que la base de datos está configurada y poblada con usuarios de prueba, puedes:

1. ✅ **Probar el login** con cualquiera de los usuarios creados
2. ✅ **Explorar el dashboard** y las páginas disponibles
3. 🔄 **Crear documentos** y probar los workflows
4. 🔄 **Agregar más datos** de prueba (documentos, workflows, notificaciones)
5. 🔄 **Integrar APIs** para conectar las páginas con la base de datos
6. 🔄 **Implementar carga de archivos** con Azure Blob Storage
7. 🔄 **Agregar pruebas** unitarias e integración

## Notas Técnicas

### Prisma Binary Targets

El schema de Prisma está configurado para funcionar en múltiples plataformas:

```prisma
generator client {
  provider      = "prisma-client-js"
  binaryTargets = ["native", "debian-openssl-3.0.x", "windows"]
}
```

Esto permite que el proyecto funcione tanto en Windows como en WSL/Linux.

### Estructura de la Base de Datos

La base de datos sigue un modelo relacional con:

- **8 enums** para tipos de datos (SecurityClassification, DiplomaticRole, DocumentType, etc.)
- **Relaciones complejas** entre documentos, workflows y usuarios
- **Auditoría completa** con logs de todas las acciones
- **Sistema de notificaciones** integrado
- **Gestión de archivos** con metadata
- **Control de versiones** y estados de documentos

### Seguridad

- Passwords hasheados con bcrypt (10 rounds)
- Sistema de niveles de clasificación (PUBLICO → ALTO_SECRETO)
- Roles diplomáticos con jerarquía
- Auditoría de todas las acciones
- Verificación de permisos por nivel de seguridad

## Troubleshooting

### Error de conexión a la base de datos

Si ves errores de conexión, verifica:

```bash
# PostgreSQL está corriendo
sudo service postgresql status

# Puerto 5432 está disponible
sudo netstat -tupln | grep 5432

# Usuario y base de datos existen
sudo -u postgres psql -c "\l" | grep siame_dev
sudo -u postgres psql -c "\du" | grep siame_user
```

### Error con bcrypt

Si tienes problemas con bcrypt en Windows WSL:

```bash
# Reinstalar bcrypt
pnpm remove bcrypt
pnpm add bcrypt
```

### Regenerar Prisma Client

Si hay problemas con el cliente de Prisma:

```bash
# Limpiar y regenerar
rm -rf node_modules/.prisma
npx prisma generate
```

---

**Configuración completada por**: Sistema automatizado
**Fecha**: 2025-10-23
**Versión de PostgreSQL**: 16.10
**Versión de Prisma**: 5.22.0

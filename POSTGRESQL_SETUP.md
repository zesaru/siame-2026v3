# 🐘 Configuración de PostgreSQL - SIAME 2026v3

**Fecha**: 2025-10-22
**PostgreSQL Versión**: 16.10

---

## 📋 Estado Actual

- ✅ PostgreSQL 16 está instalado en WSL2
- ⏳ Servicio necesita ser iniciado
- ⏳ Base de datos necesita ser creada
- ⏳ Usuario necesita ser configurado

---

## 🚀 INICIO RÁPIDO (Ejecutar en orden)

### 1. Iniciar PostgreSQL

```bash
sudo service postgresql start
```

**Verificar que está corriendo:**
```bash
sudo service postgresql status
```

### 2. Crear Usuario y Base de Datos

```bash
# Conectar como superusuario postgres
sudo -u postgres psql

# Dentro de psql, ejecutar:
CREATE USER siame_user WITH PASSWORD 'siame_password';
CREATE DATABASE siame_dev OWNER siame_user;
GRANT ALL PRIVILEGES ON DATABASE siame_dev TO siame_user;

# Salir
\q
```

### 3. Verificar Conexión

```bash
# Probar conexión con el nuevo usuario
psql -U siame_user -d siame_dev -h localhost -c "SELECT version();"
```

Si te pide contraseña, usa: `siame_password`

### 4. Aplicar Migraciones de Prisma

```bash
cd /mnt/c/Users/embto/Documents/GitHub/siame-2026v3/src/frontend

# Generar cliente Prisma (si no está generado)
npx prisma generate

# Aplicar migraciones
npx prisma migrate dev --name initial_setup

# Ver la base de datos en el navegador
npx prisma studio
```

---

## 🔐 CONFIGURACIÓN DE AUTENTICACIÓN

### Método 1: Usando peer authentication (Recomendado para desarrollo)

Si quieres evitar escribir contraseña cada vez:

1. **Editar pg_hba.conf:**
```bash
sudo nano /etc/postgresql/16/main/pg_hba.conf
```

2. **Cambiar esta línea:**
```
# De:
local   all             all                                     peer

# A:
local   all             all                                     md5
```

3. **Reiniciar PostgreSQL:**
```bash
sudo service postgresql restart
```

### Método 2: Trust local connections (Solo para desarrollo local)

**⚠️ ADVERTENCIA: No usar en producción**

```bash
# Editar pg_hba.conf
sudo nano /etc/postgresql/16/main/pg_hba.conf

# Cambiar a:
local   all             all                                     trust

# Reiniciar
sudo service postgresql restart
```

---

## ✅ VERIFICACIÓN COMPLETA

### Script de Verificación

```bash
#!/bin/bash

echo "🔍 Verificando PostgreSQL..."

# 1. Verificar servicio
echo "1. Estado del servicio:"
sudo service postgresql status | grep "Active"

# 2. Verificar conexión
echo -e "\n2. Probando conexión:"
psql -U siame_user -d siame_dev -h localhost -c "SELECT 'Conexión exitosa!' as status;" 2>/dev/null || echo "❌ Conexión falló"

# 3. Verificar base de datos
echo -e "\n3. Bases de datos existentes:"
psql -U siame_user -d siame_dev -h localhost -c "\l" 2>/dev/null | grep siame_dev

# 4. Verificar tablas (después de migración)
echo -e "\n4. Tablas en siame_dev:"
psql -U siame_user -d siame_dev -h localhost -c "\dt" 2>/dev/null

echo -e "\n✅ Verificación completada"
```

Guardar como `verify-postgres.sh` y ejecutar:
```bash
chmod +x verify-postgres.sh
./verify-postgres.sh
```

---

## 🔄 MIGRACIONES DE PRISMA

### Comandos Importantes

```bash
cd /mnt/c/Users/embto/Documents/GitHub/siame-2026v3/src/frontend

# Ver estado de migraciones
npx prisma migrate status

# Crear nueva migración
npx prisma migrate dev --name nombre_de_la_migracion

# Aplicar migraciones pendientes
npx prisma migrate deploy

# Reset completo (⚠️ BORRA TODOS LOS DATOS)
npx prisma migrate reset

# Generar cliente después de cambios en schema
npx prisma generate

# Abrir Prisma Studio (GUI para la BD)
npx prisma studio
```

### Primera Migración

```bash
# Aplicar schema inicial
npx prisma migrate dev --name initial_setup

# Esto creará todas las tablas:
# - users
# - accounts
# - sessions
# - verification_tokens
# - documents
# - hojas_remision
# - guias_valija
# - valijas_internas
# - items_valija
# - precintos
# - document_authorizations
# - workflows
# - workflow_steps
# - document_workflows
# - notifications
# - audit_logs
# - file_uploads
# - system_config
```

---

## 👤 CREAR USUARIO DE PRUEBA

### Opción 1: Desde la aplicación

1. Ir a: `http://localhost:3005/auth/register`
2. Completar formulario:
   - Nombre: Tu nombre
   - Email: test@maeuec.es
   - Contraseña: test1234

### Opción 2: Directamente en la BD

```sql
-- Conectar a la base de datos
psql -U siame_user -d siame_dev -h localhost

-- Insertar usuario de prueba
INSERT INTO users (
  id,
  email,
  name,
  password,
  "diplomaticRole",
  "securityClearance",
  "isActive",
  "isVerified",
  "createdAt",
  "updatedAt"
) VALUES (
  gen_random_uuid()::text,
  'admin@maeuec.es',
  'Administrador',
  '$2a$10$YourHashedPasswordHere',  -- Usar bcrypt para hashear
  'EMBAJADOR',
  'ALTO_SECRETO',
  true,
  true,
  NOW(),
  NOW()
);
```

### Opción 3: Usando script Node.js

```javascript
// scripts/create-user.js
const bcrypt = require('bcryptjs');
const { PrismaClient } = require('@prisma/client');

const prisma = new PrismaClient();

async function main() {
  const hashedPassword = await bcrypt.hash('admin123', 10);

  const user = await prisma.user.create({
    data: {
      email: 'admin@maeuec.es',
      name: 'Administrador',
      password: hashedPassword,
      diplomaticRole: 'EMBAJADOR',
      securityClearance: 'ALTO_SECRETO',
      isActive: true,
      isVerified: true,
    },
  });

  console.log('✅ Usuario creado:', user);
}

main()
  .catch(console.error)
  .finally(() => prisma.$disconnect());
```

Ejecutar:
```bash
node scripts/create-user.js
```

---

## 🐛 TROUBLESHOOTING

### Error: "Connection refused"

**Causa**: PostgreSQL no está corriendo

**Solución:**
```bash
sudo service postgresql start
sudo service postgresql status
```

### Error: "FATAL: Peer authentication failed"

**Causa**: Método de autenticación incorrecto

**Solución:**
1. Editar `/etc/postgresql/16/main/pg_hba.conf`
2. Cambiar `peer` a `md5` o `trust`
3. Reiniciar: `sudo service postgresql restart`

### Error: "database 'siame_dev' does not exist"

**Causa**: Base de datos no creada

**Solución:**
```bash
sudo -u postgres psql -c "CREATE DATABASE siame_dev OWNER siame_user;"
```

### Error: "role 'siame_user' does not exist"

**Causa**: Usuario no creado

**Solución:**
```bash
sudo -u postgres psql -c "CREATE USER siame_user WITH PASSWORD 'siame_password';"
```

### Error al ejecutar migraciones

**Solución:**
```bash
# Limpiar y reintentar
rm -rf node_modules/.prisma
npx prisma generate
npx prisma migrate dev
```

---

## 📊 COMANDOS ÚTILES DE POSTGRESQL

```bash
# Listar bases de datos
psql -U siame_user -d siame_dev -c "\l"

# Listar tablas
psql -U siame_user -d siame_dev -c "\dt"

# Describir tabla
psql -U siame_user -d siame_dev -c "\d users"

# Ver todos los usuarios
psql -U siame_user -d siame_dev -c "SELECT * FROM users;"

# Contar registros
psql -U siame_user -d siame_dev -c "SELECT COUNT(*) FROM users;"

# Backup de la base de datos
pg_dump -U siame_user -h localhost siame_dev > backup.sql

# Restaurar backup
psql -U siame_user -h localhost siame_dev < backup.sql
```

---

## 🔄 CONFIGURACIÓN AUTOMÁTICA (Script Completo)

```bash
#!/bin/bash
# setup-postgres.sh

echo "🚀 Configurando PostgreSQL para SIAME 2026v3..."

# Iniciar PostgreSQL
echo "1️⃣ Iniciando PostgreSQL..."
sudo service postgresql start

# Crear usuario y base de datos
echo "2️⃣ Creando usuario y base de datos..."
sudo -u postgres psql << EOF
CREATE USER siame_user WITH PASSWORD 'siame_password';
CREATE DATABASE siame_dev OWNER siame_user;
GRANT ALL PRIVILEGES ON DATABASE siame_dev TO siame_user;
\q
EOF

# Verificar conexión
echo "3️⃣ Verificando conexión..."
PGPASSWORD=siame_password psql -U siame_user -d siame_dev -h localhost -c "SELECT 'Conexión exitosa!' as status;"

# Aplicar migraciones
echo "4️⃣ Aplicando migraciones de Prisma..."
cd /mnt/c/Users/embto/Documents/GitHub/siame-2026v3/src/frontend
npx prisma generate
npx prisma migrate dev --name initial_setup

echo "✅ PostgreSQL configurado correctamente!"
echo "🎯 Próximo paso: Crear usuario de prueba o iniciar la aplicación"
```

---

## ✅ CHECKLIST DE CONFIGURACIÓN

- [ ] PostgreSQL está corriendo
- [ ] Usuario `siame_user` creado
- [ ] Base de datos `siame_dev` creada
- [ ] Conexión verificada
- [ ] Migraciones aplicadas
- [ ] Tablas creadas (17 tablas)
- [ ] Usuario de prueba creado
- [ ] Login funciona correctamente

---

## 📞 PRÓXIMOS PASOS

Después de configurar PostgreSQL:

1. **Probar registro:**
   ```
   http://localhost:3005/auth/register
   ```

2. **Probar login:**
   ```
   http://localhost:3005/auth/login
   ```

3. **Ver dashboard autenticado:**
   ```
   http://localhost:3005/dashboard
   ```

4. **Explorar base de datos:**
   ```bash
   npx prisma studio
   ```

---

**🎯 CONFIGURACIÓN RECOMENDADA PARA DESARROLLO:**

```bash
# Ejecutar estos comandos en orden:
sudo service postgresql start
sudo -u postgres psql -c "CREATE USER siame_user WITH PASSWORD 'siame_password';"
sudo -u postgres psql -c "CREATE DATABASE siame_dev OWNER siame_user;"
cd /mnt/c/Users/embto/Documents/GitHub/siame-2026v3/src/frontend
npx prisma migrate dev --name initial_setup
```

---

_Última actualización: 2025-10-22_

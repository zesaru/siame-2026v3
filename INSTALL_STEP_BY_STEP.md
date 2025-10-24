# 🚀 INSTALACIÓN PASO A PASO - SIAME 2026v3

**Tiempo total estimado: 5-10 minutos**

---

## ✅ ANTES DE EMPEZAR

Copia y pega cada bloque de comandos en tu terminal WSL.

---

## 📋 PASO 1: Actualizar Sistema (30 segundos)

```bash
sudo apt update
```

**¿Qué hace?** Actualiza la lista de paquetes disponibles.

---

## 📦 PASO 2: Instalar Servicios (2-3 minutos)

Copia y pega este comando completo:

```bash
sudo apt install -y postgresql postgresql-contrib redis-server python3-pip python3-venv
```

**¿Qué instala?**
- PostgreSQL 15 (base de datos)
- Redis 7 (caché)
- pip (gestor de paquetes Python)
- venv (entornos virtuales Python)

---

## 🚀 PASO 3: Iniciar Servicios (5 segundos)

```bash
sudo service postgresql start && sudo service redis-server start
```

**¿Qué hace?** Inicia PostgreSQL y Redis.

---

## 🗄️ PASO 4: Configurar Base de Datos (10 segundos)

Copia y pega este bloque completo:

```bash
sudo -u postgres psql << 'EOF'
-- Crear usuario si no existe
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_user WHERE usename = 'siame_user') THEN
        CREATE USER siame_user WITH PASSWORD 'siame_password';
    END IF;
END $$;

-- Crear base de datos si no existe
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_database WHERE datname = 'siame_dev') THEN
        CREATE DATABASE siame_dev OWNER siame_user;
    END IF;
END $$;

-- Otorgar permisos
GRANT ALL PRIVILEGES ON DATABASE siame_dev TO siame_user;
ALTER USER siame_user CREATEDB;
EOF
```

**¿Qué hace?**
- Crea el usuario `siame_user`
- Crea la base de datos `siame_dev`
- Otorga todos los permisos

---

## ✅ PASO 5: Verificar Conexión (5 segundos)

```bash
PGPASSWORD=siame_password psql -U siame_user -d siame_dev -h localhost -c "SELECT 'PostgreSQL OK' as status;"
```

**Resultado esperado:**
```
    status
---------------
 PostgreSQL OK
```

```bash
redis-cli ping
```

**Resultado esperado:**
```
PONG
```

---

## 🐍 PASO 6: Instalar Dependencias Python (1-2 minutos)

```bash
cd /mnt/c/Users/embto/Documents/GitHub/siame-2026v3/orchestrator
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
deactivate
cd ..
```

**¿Qué hace?**
- Crea entorno virtual
- Actualiza pip
- Instala todas las dependencias Python
- Desactiva el entorno

---

## 🔍 PASO 7: Verificar Todo (10 segundos)

```bash
./verify-setup.sh
```

**Resultado esperado:**
Todos los servicios deberían mostrar ✅

---

## 🗄️ PASO 8: Aplicar Migraciones (30 segundos)

```bash
./run-migrations.sh
```

**¿Qué hace?**
- Valida el schema de Prisma
- Crea las 17 tablas en PostgreSQL
- Configura relaciones e índices

---

## 🎉 PASO 9: ¡Iniciar Desarrollo!

```bash
./start-dev.sh
```

Elige una opción:
- **1** = Frontend (Next.js)
- **2** = Prisma Studio (explorador de BD)
- **3** = Orchestrator (backend Python)

---

## 🚨 SI ALGO FALLA

### PostgreSQL no inicia:
```bash
sudo service postgresql status
sudo service postgresql restart
```

### Redis no responde:
```bash
sudo service redis-server status
sudo service redis-server restart
```

### Error en migraciones:
```bash
cd src/frontend
npx prisma migrate reset
npx prisma migrate dev --name initial_setup
```

---

## 📝 NOTAS

- **Usuario BD**: siame_user
- **Password BD**: siame_password
- **Base de datos**: siame_dev
- Estas credenciales son para **desarrollo solamente**

---

## ✅ CHECKLIST

Marca cuando completes:

- [ ] Paso 1: Sistema actualizado
- [ ] Paso 2: Servicios instalados
- [ ] Paso 3: Servicios iniciados
- [ ] Paso 4: BD configurada
- [ ] Paso 5: Conexión verificada
- [ ] Paso 6: Python configurado
- [ ] Paso 7: Todo verificado ✅
- [ ] Paso 8: Migraciones aplicadas
- [ ] Paso 9: Desarrollo iniciado

---

**¿Listo para empezar?** Empieza por el PASO 1 ⬆️

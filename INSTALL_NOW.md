# 🚀 INSTALACIÓN INMEDIATA - SIAME 2026v3

**Copia y pega estos comandos en tu terminal WSL**

---

## ⚡ OPCIÓN 1: SCRIPT AUTOMÁTICO (Recomendado)

Simplemente ejecuta:

```bash
./install-services.sh
```

Se te pedirá tu contraseña de sudo y el script hará todo automáticamente.

---

## 📋 OPCIÓN 2: COMANDOS MANUALES (Si prefieres control total)

### Paso 1: Actualizar sistema

```bash
sudo apt update && sudo apt upgrade -y
```

### Paso 2: Instalar PostgreSQL

```bash
sudo apt install -y postgresql postgresql-contrib
```

### Paso 3: Instalar Redis

```bash
sudo apt install -y redis-server
```

### Paso 4: Instalar pip

```bash
sudo apt install -y python3-pip python3-venv
```

### Paso 5: Iniciar servicios

```bash
sudo service postgresql start
sudo service redis-server start
```

### Paso 6: Configurar PostgreSQL

```bash
sudo -u postgres psql << 'EOF'
-- Crear usuario
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_user WHERE usename = 'siame_user') THEN
        CREATE USER siame_user WITH PASSWORD 'siame_password';
    END IF;
END
$$;

-- Crear base de datos
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_database WHERE datname = 'siame_dev') THEN
        CREATE DATABASE siame_dev OWNER siame_user;
    END IF;
END
$$;

-- Otorgar permisos
GRANT ALL PRIVILEGES ON DATABASE siame_dev TO siame_user;
ALTER USER siame_user CREATEDB;
EOF
```

### Paso 7: Verificar conexiones

```bash
# PostgreSQL
PGPASSWORD=siame_password psql -U siame_user -d siame_dev -h localhost -c "SELECT 'PostgreSQL OK' as status;"

# Redis
redis-cli ping
```

### Paso 8: Instalar dependencias Python

```bash
cd /mnt/c/Users/embto/Documents/GitHub/siame-2026v3/orchestrator
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
deactivate
```

### Paso 9: Verificar instalación

```bash
cd /mnt/c/Users/embto/Documents/GitHub/siame-2026v3
./verify-setup.sh
```

---

## ⚡ OPCIÓN 3: UN SOLO COMANDO (Todo junto)

```bash
sudo apt update && \
sudo apt install -y postgresql postgresql-contrib redis-server python3-pip python3-venv && \
sudo service postgresql start && \
sudo service redis-server start && \
sudo -u postgres psql -c "CREATE USER siame_user WITH PASSWORD 'siame_password';" 2>/dev/null || true && \
sudo -u postgres psql -c "CREATE DATABASE siame_dev OWNER siame_user;" 2>/dev/null || true && \
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE siame_dev TO siame_user;" && \
sudo -u postgres psql -c "ALTER USER siame_user CREATEDB;" && \
cd /mnt/c/Users/embto/Documents/GitHub/siame-2026v3/orchestrator && \
python3 -m venv venv && \
source venv/bin/activate && \
pip install --upgrade pip && \
pip install -r requirements.txt && \
deactivate && \
cd /mnt/c/Users/embto/Documents/GitHub/siame-2026v3 && \
./verify-setup.sh
```

---

## ✅ DESPUÉS DE INSTALAR

Una vez completada la instalación, ejecuta:

```bash
./verify-setup.sh
```

Si todo está ✅, continúa con:

```bash
./run-migrations.sh
```

Y finalmente:

```bash
./start-dev.sh
```

---

## 🔧 SOLUCIÓN DE PROBLEMAS

### Si PostgreSQL no inicia:

```bash
sudo service postgresql status
sudo service postgresql restart
```

### Si Redis no responde:

```bash
sudo service redis-server status
sudo service redis-server restart
```

### Si hay problemas con permisos:

```bash
sudo -u postgres psql
\du  # Ver usuarios
\l   # Ver bases de datos
\q   # Salir
```

---

## 📝 NOTAS

- Las credenciales son para **desarrollo solamente**
- Usuario: `siame_user`
- Password: `siame_password`
- Base de datos: `siame_dev`
- Los servicios se detendrán al cerrar WSL

---

**¿Listo?** Elige una opción y copia los comandos! 🚀

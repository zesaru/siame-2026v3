# ⚡ EL INICIO MÁS RÁPIDO - SIAME 2026v3

**3 comandos. 6 minutos. Listo para desarrollar.**

---

## 🚀 OPCIÓN 1: SUPER RÁPIDO (1 comando)

```bash
./INSTALL_ONE_COMMAND.sh && ./run-migrations.sh && ./start-dev.sh
```

**¿Qué hace?**
1. Instala todo (5 min)
2. Crea las tablas (30 seg)
3. Te pregunta qué iniciar

---

## ⚡ OPCIÓN 2: ULTRA RÁPIDO (Copiar y pegar)

### Paso 1: Instalar (5 minutos)

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
pip install --upgrade pip -q && \
pip install -r requirements.txt -q && \
deactivate && \
cd .. && \
echo "✅ Instalación completa"
```

### Paso 2: Crear Tablas (30 segundos)

```bash
cd /mnt/c/Users/embto/Documents/GitHub/siame-2026v3 && ./run-migrations.sh
```

### Paso 3: Iniciar (5 segundos)

```bash
./start-dev.sh
```

---

## 🎯 OPCIÓN 3: MÁS SEGURO (Paso a paso)

Si prefieres ver cada paso:

```bash
# 1. Usar script automático
./install-services.sh

# 2. Aplicar migraciones
./run-migrations.sh

# 3. Iniciar desarrollo
./start-dev.sh
```

---

## ✅ VERIFICAR QUE TODO FUNCIONA

```bash
./verify-setup.sh
```

Deberías ver todos ✅

---

## 🎮 DESPUÉS DE INSTALAR

### Explorar la Base de Datos
```bash
cd src/frontend
npx prisma studio
```
Se abre en: http://localhost:5555

### Iniciar Frontend
```bash
cd src/frontend
npm run dev
```
Se abre en: http://localhost:3000

### Iniciar Orchestrator (Backend)
```bash
cd orchestrator
source venv/bin/activate
python main.py
```
API en: http://localhost:8000

---

## 🚨 SI ALGO FALLA

### PostgreSQL no responde:
```bash
sudo service postgresql restart
PGPASSWORD=siame_password psql -U siame_user -d siame_dev -h localhost -c "SELECT 1;"
```

### Redis no responde:
```bash
sudo service redis-server restart
redis-cli ping
```

### Migraciones fallan:
```bash
cd src/frontend
npx prisma migrate reset
npx prisma migrate dev
```

---

## 📊 LO QUE SE INSTALARÁ

- **PostgreSQL 15**: Base de datos principal
- **Redis 7**: Caché y mensajería
- **pip**: Gestor de paquetes Python
- **Dependencias Python**: ~40 paquetes
- **Base de datos**: siame_dev
- **Usuario**: siame_user
- **17 tablas**: Estructura completa

---

## ⏱️ TIEMPO TOTAL

- Instalación: 5 minutos
- Migraciones: 30 segundos
- Iniciar: 5 segundos

**Total: ~6 minutos** ⚡

---

## 🎯 RECOMENDACIÓN

**Si tienes experiencia**: Usa OPCIÓN 2 (copiar y pegar)

**Si prefieres automatizado**: Usa OPCIÓN 1 (super rápido)

**Si quieres control**: Usa OPCIÓN 3 (paso a paso)

---

**¿Listo?** Elige una opción y ¡empieza! 🚀

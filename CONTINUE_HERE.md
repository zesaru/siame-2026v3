# 🚀 SIAME 2026v3 - CONTINUAR AQUÍ

## 📍 ESTADO ACTUAL DEL PROYECTO

**Fecha**: 2025-09-30
**Fase**: 2 - Configuración del Entorno
**Progreso Global**: 25%

---

## ✅ TAREAS COMPLETADAS

### Fase 1: Estructura del Proyecto ✅
- ✅ 93 archivos creados
- ✅ Estructura de carpetas organizada
- ✅ Configuración de Docker (`docker-compose.yml`)
- ✅ Archivos de configuración base

### Fase 2: Configuración del Entorno (Parcial) ⏳
- ✅ `orchestrator/requirements.txt` creado
- ✅ `.env.example` creado
- ✅ `.env.local` para desarrollo creado
- ✅ `docs/PROJECT_CONTEXT.md` creado
- ✅ Schema básico de Prisma con modelos fundamentales
- ⏳ **PENDIENTE**: Completar schema.prisma con modelos específicos

---

## 🎯 PRÓXIMOS PASOS INMEDIATOS

### 1. Completar Schema de Base de Datos
**Archivo**: `src/frontend/prisma/schema.prisma`

Agregar los siguientes modelos:

#### a) HojaRemision
```prisma
model HojaRemision {
  id                String                @id @default(cuid())
  documentId        String                @unique

  // Identificación
  numeroDocumento   String                @unique
  unidadRemitente   UnidadRemitente       // Enum: OGA, PCO, PRU, CON, ADM
  fechaEmision      DateTime

  // Contenido
  asunto            String
  destino           String
  observaciones     String?

  // Clasificación
  clasificacion     SecurityClassification

  // Relaciones
  document          Document              @relation(fields: [documentId], references: [id])

  createdAt         DateTime              @default(now())
  updatedAt         DateTime              @updatedAt

  @@map("hojas_remision")
}

enum UnidadRemitente {
  OGA
  PCO
  PRU
  CON
  ADM
}
```

#### b) GuiaValija (Estructura Jerárquica)
```prisma
model GuiaValija {
  id                  String                @id @default(cuid())
  documentId          String                @unique

  // Identificación
  numeroGuia          String                @unique
  tipoGuia            TipoGuia              // ENTRADA / SALIDA
  modalidad           ModalidadValija       // ORDINARIA / EXTRAORDINARIA

  // Fechas
  fechaDespacho       DateTime?
  fechaRecepcion      DateTime?

  // Origen y Destino
  origen              String
  destino             String

  // Clasificación
  clasificacion       SecurityClassification

  // Relaciones
  document            Document              @relation(fields: [documentId], references: [id])
  precintos           Precinto[]
  valijasInternas     ValijaInterna[]

  createdAt           DateTime              @default(now())
  updatedAt           DateTime              @updatedAt

  @@map("guias_valija")
}

enum TipoGuia {
  ENTRADA
  SALIDA
}

enum ModalidadValija {
  ORDINARIA
  EXTRAORDINARIA
}
```

#### c) ValijaInterna
```prisma
model ValijaInterna {
  id                String                @id @default(cuid())
  guiaValijaId      String

  // Identificación
  numeroValija      String
  orden             Int                   @default(1)

  // Contenido
  descripcion       String?

  // Relaciones
  guiaValija        GuiaValija            @relation(fields: [guiaValijaId], references: [id], onDelete: Cascade)
  items             ItemValija[]
  precintos         Precinto[]

  createdAt         DateTime              @default(now())
  updatedAt         DateTime              @updatedAt

  @@unique([guiaValijaId, numeroValija])
  @@map("valijas_internas")
}
```

#### d) ItemValija
```prisma
model ItemValija {
  id                String                @id @default(cuid())
  valijaInternaId   String

  // Contenido
  orden             Int
  descripcion       String
  cantidad          Int                   @default(1)
  observaciones     String?

  // Relaciones
  valijaInterna     ValijaInterna         @relation(fields: [valijaInternaId], references: [id], onDelete: Cascade)

  createdAt         DateTime              @default(now())
  updatedAt         DateTime              @updatedAt

  @@map("items_valija")
}
```

#### e) Precinto
```prisma
model Precinto {
  id                String                @id @default(cuid())
  guiaValijaId      String?
  valijaInternaId   String?

  // Información del precinto
  numeroPrecinto    String                @unique
  estado            EstadoPrecinto        @default(INTACTO)
  observaciones     String?

  // Relaciones (un precinto puede estar en la guía principal o en valija interna)
  guiaValija        GuiaValija?           @relation(fields: [guiaValijaId], references: [id], onDelete: Cascade)
  valijaInterna     ValijaInterna?        @relation(fields: [valijaInternaId], references: [id], onDelete: Cascade)

  createdAt         DateTime              @default(now())
  updatedAt         DateTime              @updatedAt

  @@map("precintos")
}

enum EstadoPrecinto {
  INTACTO
  ROTO
  FALTANTE
}
```

#### f) DocumentAuthorization (Control de Acceso por Documento)
```prisma
model DocumentAuthorization {
  id                String                @id @default(cuid())
  documentId        String
  userId            String

  // Permisos
  canRead           Boolean               @default(true)
  canEdit           Boolean               @default(false)
  canDelete         Boolean               @default(false)
  canShare          Boolean               @default(false)

  // Temporalidad
  validFrom         DateTime              @default(now())
  validUntil        DateTime?

  // Autorización
  authorizedById    String
  reason            String?

  // Relaciones
  document          Document              @relation(fields: [documentId], references: [id], onDelete: Cascade)
  user              User                  @relation(fields: [userId], references: [id], onDelete: Cascade)
  authorizedBy      User                  @relation("AuthorizationGranter", fields: [authorizedById], references: [id])

  createdAt         DateTime              @default(now())
  updatedAt         DateTime              @updatedAt

  @@unique([documentId, userId])
  @@map("document_authorizations")
}
```

### 2. Actualizar Modelos Existentes

Agregar relaciones faltantes:

**En User:**
```prisma
// Agregar
hojaRemisionCreated      HojaRemision[]
guiaValijaCreated        GuiaValija[]
authorizationsGranted    DocumentAuthorization[]    @relation("AuthorizationGranter")
authorizationsReceived   DocumentAuthorization[]
uploadedBy               FileUpload[]
```

**En Document:**
```prisma
// Agregar
hojaRemision      HojaRemision?
guiaValija        GuiaValija?
authorizations    DocumentAuthorization[]
```

---

## 💻 COMANDOS A EJECUTAR (EN ORDEN)

### 1. Completar Schema de Prisma
```bash
# Editar archivo
nano src/frontend/prisma/schema.prisma

# O usar editor de tu preferencia
code src/frontend/prisma/schema.prisma
```

### 2. Validar Schema
```bash
cd src/frontend
npx prisma validate
```

### 3. Generar Cliente Prisma
```bash
cd src/frontend
npx prisma generate
```

### 4. Crear Migración
```bash
cd src/frontend
npx prisma migrate dev --name add_diplomatic_document_models
```

### 5. Instalar Dependencias Python
```bash
cd orchestrator
pip install -r requirements.txt
```

### 6. Configurar Variables de Entorno
```bash
# Copiar .env.local a .env
cp .env.local .env

# Editar con tus credenciales reales (si las tienes)
nano .env
```

### 7. Levantar Servicios con Docker
```bash
# Desde la raíz del proyecto
docker-compose up -d postgres redis
```

### 8. Verificar Servicios
```bash
# Verificar PostgreSQL
docker-compose ps
docker-compose logs postgres

# Verificar Redis
docker-compose logs redis
```

### 9. Aplicar Migraciones
```bash
cd src/frontend
npx prisma migrate deploy
```

### 10. Poblar Base de Datos (Opcional)
```bash
cd src/frontend
npx prisma db seed
```

---

## 📋 VERIFICACIÓN DE PROGRESO

Marcar con `[x]` cuando se complete:

- [ ] Schema de Prisma completado con todos los modelos
- [ ] Validación de schema exitosa
- [ ] Cliente Prisma generado
- [ ] Migraciones aplicadas
- [ ] Dependencias Python instaladas
- [ ] Servicios Docker corriendo
- [ ] Base de datos accesible
- [ ] Variables de entorno configuradas

---

## 📚 REFERENCIAS RÁPIDAS

### Archivos Importantes
- **Schema**: `src/frontend/prisma/schema.prisma`
- **Env**: `.env.local` (desarrollo) / `.env` (personalizado)
- **Requirements**: `orchestrator/requirements.txt`
- **Docker**: `docker-compose.yml`
- **Contexto**: `docs/PROJECT_CONTEXT.md`

### Documentación
- **Prisma Schema**: https://www.prisma.io/docs/concepts/components/prisma-schema
- **Prisma Relations**: https://www.prisma.io/docs/concepts/components/prisma-schema/relations
- **Next.js + Prisma**: https://www.prisma.io/nextjs

### Comandos Útiles
```bash
# Ver estado de Docker
docker-compose ps

# Ver logs
docker-compose logs -f

# Parar servicios
docker-compose down

# Limpiar todo
docker-compose down -v

# Prisma Studio (UI para BD)
cd src/frontend && npx prisma studio
```

---

## 🔄 DESPUÉS DE COMPLETAR ESTO

### Fase 3: Implementación del Orquestador
1. Implementar agentes Python en `agents/`
2. Sistema de comunicación entre agentes
3. Coordinación de tareas
4. Manejo de errores

### Fase 4: Integración con Azure
1. Configurar Azure Form Recognizer
2. Implementar procesamiento OCR
3. Conectar Blob Storage
4. Integrar Key Vault

### Fase 5: Frontend Next.js
1. Sistema de autenticación
2. Dashboard principal
3. Módulos de documentos
4. UI para valijas diplomáticas

---

## ⚠️ NOTAS IMPORTANTES

1. **NO COMMITEAR** archivos `.env` con credenciales reales
2. Usar `MOCK_AZURE_SERVICES=true` en desarrollo
3. Verificar que PostgreSQL esté corriendo antes de migraciones
4. Hacer backup de la BD antes de cambios grandes
5. Consultar `docs/PROJECT_CONTEXT.md` para contexto completo

---

## 📞 AYUDA

Si encuentras problemas:
1. Revisar logs: `docker-compose logs`
2. Verificar variables de entorno
3. Consultar documentación en `/docs`
4. Revisar ejemplos en `/examples`

---

**🎯 OBJETIVO INMEDIATO**: Completar el schema de Prisma con todos los modelos de documentos diplomáticos.

**⏱️ TIEMPO ESTIMADO**: 30-45 minutos

**🚦 STATUS**: 🟡 Listo para continuar

---

_Última actualización: 2025-09-30_
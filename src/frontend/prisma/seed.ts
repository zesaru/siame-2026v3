/**
 * SIAME 2026v3 - Database Seed Script
 * Script para poblar la base de datos con datos de prueba
 */

import { PrismaClient } from '@prisma/client'
import bcrypt from 'bcrypt'

const prisma = new PrismaClient()

async function main() {
  console.log('🌱 Iniciando seed de la base de datos...')

  // Limpiar datos existentes
  console.log('🗑️  Limpiando datos existentes...')
  await prisma.documentWorkflow.deleteMany()
  await prisma.workflowStep.deleteMany()
  await prisma.workflow.deleteMany()
  await prisma.notification.deleteMany()
  await prisma.auditLog.deleteMany()
  await prisma.documentAuthorization.deleteMany()
  await prisma.fileUpload.deleteMany()
  await prisma.document.deleteMany()
  await prisma.account.deleteMany()
  await prisma.session.deleteMany()
  await prisma.user.deleteMany()

  // Crear usuarios de prueba
  console.log('👤 Creando usuarios de prueba...')

  const hashedPassword = await bcrypt.hash('password123', 10)

  const embajador = await prisma.user.create({
    data: {
      name: 'Luis Alberto Chuquihuara Chil',
      email: 'lchuquihuara@embaperu.jp',
      password: hashedPassword,
      diplomaticRole: 'EMBAJADOR',
      securityClearance: 'ALTO_SECRETO',
      isVerified: true,
      department: 'Despacho del Embajador',
      embassy: 'Embajada del Perú en Japón',
    },
  })

  const consejero = await prisma.user.create({
    data: {
      name: 'María Elena Castillo Ayala',
      email: 'mcastillo@embaperu.jp',
      password: hashedPassword,
      diplomaticRole: 'CONSEJERO',
      securityClearance: 'SECRETO',
      isVerified: true,
      department: 'Asuntos Políticos y Económicos',
      embassy: 'Embajada del Perú en Japón',
    },
  })

  const primerSecretario = await prisma.user.create({
    data: {
      name: 'Carlos Raúl Mendoza Flores',
      email: 'cmendoza@embaperu.jp',
      password: hashedPassword,
      diplomaticRole: 'PRIMER_SECRETARIO',
      securityClearance: 'CONFIDENCIAL',
      isVerified: true,
      department: 'Asuntos Consulares',
      embassy: 'Embajada del Perú en Japón',
    },
  })

  const segundoSecretario = await prisma.user.create({
    data: {
      name: 'Ana Patricia Quispe Mamani',
      email: 'aquispe@embaperu.jp',
      password: hashedPassword,
      diplomaticRole: 'SEGUNDO_SECRETARIO',
      securityClearance: 'RESTRINGIDO',
      isVerified: true,
      department: 'Valijas Diplomáticas y Protocolo',
      embassy: 'Embajada del Perú en Japón',
    },
  })

  const admin = await prisma.user.create({
    data: {
      name: 'Admin Sistema SIAME',
      email: 'admin@embaperu.jp',
      password: hashedPassword,
      diplomaticRole: 'EMBAJADOR',
      securityClearance: 'ALTO_SECRETO',
      isVerified: true,
      department: 'Tecnologías de la Información',
      embassy: 'Embajada del Perú en Japón',
    },
  })

  console.log(`✅ Creados 5 usuarios (password: password123)`)

  // Crear documentos de prueba
  console.log('📄 Creando documentos de prueba...')

  const doc1 = await prisma.document.create({
    data: {
      title: 'Hoja de Remisión OGA-2024-001',
      description: 'Remisión de documentos clasificados para revisión del Embajador',
      type: 'HOJA_REMISION_OGA',
      classification: 'SECRETO',
      status: 'APPROVED',
      createdById: consejero.id,
      assignedToId: embajador.id,
      extractedData: {
        numeroOficio: 'OGA-2024-001',
        destinatario: 'Embajador',
        asunto: 'Documentos para revisión urgente',
      },
    },
  })

  const doc2 = await prisma.document.create({
    data: {
      title: 'Guía de Valija Diplomática - Entrada Ordinaria',
      description: 'Recepción de valija diplomática desde la sede central',
      type: 'GUIA_VALIJA_ENTRADA_ORDINARIA',
      classification: 'CONFIDENCIAL',
      status: 'UNDER_REVIEW',
      createdById: segundoSecretario.id,
      assignedToId: primerSecretario.id,
      extractedData: {
        numeroGuia: 'GV-IN-2024-015',
        origen: 'Lima - Ministerio de Relaciones Exteriores',
        pesoKg: 5.2,
        numeroBultos: 3,
      },
    },
  })

  const doc3 = await prisma.document.create({
    data: {
      title: 'Nota Diplomática - Protocolo Bilateral',
      description: 'Propuesta de nuevo protocolo de cooperación bilateral',
      type: 'NOTA_DIPLOMATICA',
      classification: 'RESTRINGIDO',
      status: 'PENDING_REVIEW',
      createdById: primerSecretario.id,
      extractedData: {
        pais: 'Japón',
        tema: 'Cooperación Cultural Perú-Japón',
        urgencia: 'Alta',
      },
    },
  })

  const doc4 = await prisma.document.create({
    data: {
      title: 'Memorándum Interno - Actualización de Procedimientos',
      description: 'Nuevos procedimientos para gestión de valijas diplomáticas',
      type: 'MEMORANDUM_INTERNO',
      classification: 'PUBLICO',
      status: 'DRAFT',
      createdById: admin.id,
      extractedData: {
        departamento: 'Todos',
        fechaVigencia: '2024-02-01',
      },
    },
  })

  const doc5 = await prisma.document.create({
    data: {
      title: 'Informe Técnico - Sistema SIAME',
      description: 'Análisis de rendimiento del sistema SIAME en el primer trimestre',
      type: 'INFORME_TECNICO',
      classification: 'CONFIDENCIAL',
      status: 'APPROVED',
      createdById: admin.id,
      assignedToId: embajador.id,
      extractedData: {
        periodo: 'Q1 2024',
        metricas: {
          documentosProcesados: 1250,
          tiempoPromedio: '2.3 días',
          satisfaccion: '94%',
        },
      },
    },
  })

  console.log(`✅ Creados 5 documentos de prueba`)

  // Crear workflows de prueba
  console.log('📋 Creando workflows de prueba...')

  const workflow1 = await prisma.workflow.create({
    data: {
      name: 'Validación de Documentos Secretos',
      description: 'Proceso de revisión y aprobación de documentos clasificados como SECRETO',
      status: 'CREATED',
      createdById: embajador.id,
    },
  })

  const workflow2 = await prisma.workflow.create({
    data: {
      name: 'Procesamiento de Valijas Diplomáticas',
      description: 'Workflow estándar para recepción y validación de valijas diplomáticas',
      status: 'CREATED',
      createdById: primerSecretario.id,
    },
  })

  // Crear pasos del workflow
  await prisma.workflowStep.createMany({
    data: [
      {
        workflowId: workflow1.id,
        name: 'Revisión inicial',
        description: 'Verificación de documentación completa',
        stepOrder: 1,
      },
      {
        workflowId: workflow1.id,
        name: 'Aprobación final',
        description: 'Aprobación del Embajador',
        stepOrder: 2,
      },
      {
        workflowId: workflow2.id,
        name: 'Recepción',
        description: 'Registro de entrada de valija',
        stepOrder: 1,
      },
      {
        workflowId: workflow2.id,
        name: 'Validación',
        description: 'Verificación de contenido',
        stepOrder: 2,
      },
    ],
  })

  // Asignar workflows a documentos
  await prisma.documentWorkflow.create({
    data: {
      documentId: doc1.id,
      workflowId: workflow1.id,
      status: 'COMPLETED',
      completedAt: new Date(),
    },
  })

  await prisma.documentWorkflow.create({
    data: {
      documentId: doc2.id,
      workflowId: workflow2.id,
      status: 'IN_PROGRESS',
    },
  })

  console.log(`✅ Creados 2 workflows con pasos`)

  // Crear notificaciones de prueba
  console.log('🔔 Creando notificaciones de prueba...')

  await prisma.notification.createMany({
    data: [
      {
        receiverId: embajador.id,
        type: 'DOCUMENT_APPROVED',
        title: 'Documento Aprobado',
        message: 'El documento OGA-2024-001 ha sido aprobado',
        documentId: doc1.id,
      },
      {
        receiverId: primerSecretario.id,
        type: 'WORKFLOW_ASSIGNED',
        title: 'Workflow Asignado',
        message: 'Se te ha asignado el workflow de validación de valija diplomática',
      },
      {
        receiverId: consejero.id,
        type: 'COMMENT_ADDED',
        title: 'Nuevo Comentario',
        message: 'El Embajador ha comentado en tu documento',
        documentId: doc1.id,
        readAt: new Date(),
      },
      {
        receiverId: admin.id,
        type: 'SYSTEM',
        title: 'Actualización del Sistema',
        message: 'SIAME ha sido actualizado a la versión 2026v3',
        readAt: new Date(),
      },
    ],
  })

  console.log(`✅ Creadas 4 notificaciones`)

  // Crear logs de auditoría
  console.log('📊 Creando logs de auditoría...')

  await prisma.auditLog.createMany({
    data: [
      {
        action: 'USER_LOGIN',
        entity: 'USER',
        entityId: embajador.id,
        userId: embajador.id,
      },
      {
        action: 'DOCUMENT_CREATED',
        entity: 'DOCUMENT',
        entityId: doc1.id,
        userId: consejero.id,
        newValues: { title: doc1.title, classification: doc1.classification },
      },
      {
        action: 'DOCUMENT_APPROVED',
        entity: 'DOCUMENT',
        entityId: doc1.id,
        userId: embajador.id,
        oldValues: { status: 'UNDER_REVIEW' },
        newValues: { status: 'APPROVED' },
      },
      {
        action: 'WORKFLOW_COMPLETED',
        entity: 'WORKFLOW',
        entityId: workflow1.id,
        userId: embajador.id,
      },
    ],
  })

  console.log(`✅ Creados 4 logs de auditoría`)

  console.log('✨ Seed completado exitosamente!')
  console.log('\n📋 Resumen:')
  console.log('  - 5 usuarios creados')
  console.log('  - 5 documentos creados')
  console.log('  - 2 workflows con pasos')
  console.log('  - 4 notificaciones')
  console.log('  - 4 logs de auditoría')
  console.log('\n🔑 Credenciales de acceso:')
  console.log('  Email: carlos.martinez@maeuec.es (Embajador)')
  console.log('  Email: maria.lopez@maeuec.es (Consejero)')
  console.log('  Email: juan.garcia@maeuec.es (Primer Secretario)')
  console.log('  Email: ana.rodriguez@maeuec.es (Segundo Secretario)')
  console.log('  Email: admin@maeuec.es (Admin)')
  console.log('  Password: password123 (para todos)')
}

main()
  .catch((e) => {
    console.error('❌ Error durante el seed:', e)
    process.exit(1)
  })
  .finally(async () => {
    await prisma.$disconnect()
  })

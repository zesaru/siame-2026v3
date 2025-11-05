/**
 * API Route: Bulk Hojas de Remisión
 * POST /api/hojas-remision/bulk - Crear múltiples hojas de remisión
 */

import { NextRequest, NextResponse } from "next/server"
import { prisma } from "@/lib/database/prisma"
import { auth } from "@/lib/auth"
import { z } from "zod"

// Schema de validación para un item de Hoja de Remisión
const HojaRemisionItemSchema = z.object({
  orden: z.number(),
  destinatario: z.string().min(1, "Destinatario es requerido"),
  numeroDocumento: z.string().min(1, "Número de documento es requerido"),
  tipoEmbalaje: z.string().optional(),
  asunto: z.string().optional(),
  remitente: z.string().min(1, "Remitente es requerido"),
  cantidad: z.number().min(1, "Cantidad debe ser mayor a 0"),
  peso: z.number().min(0, "Peso no puede ser negativo"),
  clasificacion: z.enum([
    "PUBLICO",
    "RESTRINGIDO",
    "CONFIDENCIAL",
    "SECRETO",
    "ALTO_SECRETO",
  ]),
  observaciones: z.string().optional(),
})

const BulkCreateSchema = z.object({
  guiaValijaId: z.string().optional(),
  fechaEmision: z.string().datetime(),
  items: z.array(HojaRemisionItemSchema).min(1, "Debe incluir al menos un item"),
})

// POST /api/hojas-remision/bulk
export async function POST(request: NextRequest) {
  try {
    const session = await auth()

    if (!session?.user) {
      return NextResponse.json(
        { success: false, error: "No autenticado" },
        { status: 401 }
      )
    }

    // Validar body
    const body = await request.json()
    const validationResult = BulkCreateSchema.safeParse(body)

    if (!validationResult.success) {
      return NextResponse.json(
        {
          success: false,
          error: "Datos inválidos",
          details: validationResult.error.errors,
        },
        { status: 400 }
      )
    }

    const { guiaValijaId, fechaEmision, items } = validationResult.data

    // Verificar que no haya números de documento duplicados
    const numeros = items.map((item) => item.numeroDocumento)
    const duplicates = numeros.filter((numero, index) => numeros.indexOf(numero) !== index)
    if (duplicates.length > 0) {
      return NextResponse.json(
        {
          success: false,
          error: "Números de documento duplicados",
          duplicates: [...new Set(duplicates)],
        },
        { status: 400 }
      )
    }

    // Verificar que la guía de valija existe (si se proporcionó)
    if (guiaValijaId) {
      const guia = await prisma.guiaValija.findUnique({
        where: { id: guiaValijaId },
      })

      if (!guia) {
        return NextResponse.json(
          { success: false, error: "Guía de valija no encontrada" },
          { status: 404 }
        )
      }
    }

    // Crear las hojas de remisión en una transacción
    const result = await prisma.$transaction(async (tx) => {
      const created = []

      for (const item of items) {
        // Crear el documento base
        const document = await tx.document.create({
          data: {
            title: `Hoja de Remisión ${item.numeroDocumento}`,
            description: item.asunto,
            type: "HOJA_REMISION_OGA", // Podemos ajustar según el tipo
            status: "DRAFT",
            classification: item.clasificacion,
            documentNumber: item.numeroDocumento,
            createdById: session.user.id,
          },
        })

        // Crear la hoja de remisión
        const hojaRemision = await tx.hojaRemision.create({
          data: {
            documentId: document.id,
            numeroDocumento: item.numeroDocumento,
            unidadRemitente: item.remitente,
            fechaEmision: new Date(fechaEmision),
            asunto: item.asunto || null,
            destino: item.destinatario,
            observaciones: item.observaciones || null,
            cantidad: item.cantidad,
            pesoItem: item.peso,
            tipoEmbalaje: item.tipoEmbalaje || null,
            clasificacion: item.clasificacion,
            guiaValijaId: guiaValijaId || null,
            createdById: session.user.id,
          },
          include: {
            document: true,
            createdBy: {
              select: {
                id: true,
                name: true,
                email: true,
              },
            },
          },
        })

        created.push(hojaRemision)

        // Crear log de auditoría
        await tx.auditLog.create({
          data: {
            action: "HOJA_REMISION_CREATED",
            entity: "HOJA_REMISION",
            entityId: hojaRemision.id,
            userId: session.user.id,
            newValues: {
              numeroDocumento: item.numeroDocumento,
              remitente: item.remitente,
              destinatario: item.destinatario,
            },
          },
        })
      }

      return created
    })

    return NextResponse.json({
      success: true,
      data: result,
      message: `${result.length} Hoja${result.length !== 1 ? "s" : ""} de Remisión creada${result.length !== 1 ? "s" : ""} exitosamente`,
    })
  } catch (error) {
    console.error("Error creating hojas de remision:", error)
    return NextResponse.json(
      {
        success: false,
        error: "Error al crear hojas de remisión",
        details: error instanceof Error ? error.message : "Error desconocido",
      },
      { status: 500 }
    )
  }
}

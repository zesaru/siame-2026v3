/**
 * API Route: Documents
 * GET /api/documents - Listar documentos
 * POST /api/documents - Crear documento
 */

import { NextRequest, NextResponse } from "next/server"
import { prisma } from "@/lib/database/prisma"
import { auth } from "@/lib/auth"

// GET /api/documents - Listar documentos con filtros
export async function GET(request: NextRequest) {
  try {
    const session = await auth()

    // Verificar autenticación
    if (!session?.user) {
      return NextResponse.json(
        { error: "No autenticado" },
        { status: 401 }
      )
    }

    // Obtener parámetros de búsqueda
    const { searchParams } = new URL(request.url)
    const page = parseInt(searchParams.get("page") || "1")
    const limit = parseInt(searchParams.get("limit") || "10")
    const type = searchParams.get("type")
    const classification = searchParams.get("classification")
    const status = searchParams.get("status")
    const search = searchParams.get("search")

    const skip = (page - 1) * limit

    // Construir filtros
    const where: any = {}

    if (type && type !== "all") {
      where.type = type
    }

    if (classification && classification !== "all") {
      where.classification = classification
    }

    if (status && status !== "all") {
      where.status = status
    }

    if (search) {
      where.OR = [
        { title: { contains: search, mode: "insensitive" } },
        { description: { contains: search, mode: "insensitive" } },
      ]
    }

    // Obtener documentos
    const [documents, total] = await Promise.all([
      prisma.document.findMany({
        where,
        skip,
        take: limit,
        orderBy: { createdAt: "desc" },
        include: {
          creator: {
            select: {
              id: true,
              name: true,
              email: true,
              diplomaticRole: true,
            },
          },
          assignedTo: {
            select: {
              id: true,
              name: true,
            },
          },
        },
      }),
      prisma.document.count({ where }),
    ])

    return NextResponse.json({
      success: true,
      data: documents,
      pagination: {
        page,
        limit,
        total,
        pages: Math.ceil(total / limit),
      },
    })
  } catch (error) {
    console.error("Error fetching documents:", error)
    return NextResponse.json(
      { error: "Error al obtener documentos" },
      { status: 500 }
    )
  }
}

// POST /api/documents - Crear nuevo documento
export async function POST(request: NextRequest) {
  try {
    const session = await auth()

    // Verificar autenticación
    if (!session?.user) {
      return NextResponse.json(
        { error: "No autenticado" },
        { status: 401 }
      )
    }

    const body = await request.json()
    const {
      title,
      description,
      type,
      classification,
      // Datos extraídos de Azure
      extractedData,
      ocrText,
      ocrConfidence,
      rawAzureResponse,
      // Datos del archivo
      fileName,
      fileSize,
      mimeType,
      storagePath,
      // Datos específicos de Guía de Valija
      guiaValija,
    } = body

    console.log("📝 Creating document with data:", {
      title,
      type,
      classification,
      hasExtractedData: !!extractedData,
      hasGuiaValija: !!guiaValija,
    })

    // Validaciones
    if (!title || !type || !classification) {
      return NextResponse.json(
        { error: "Faltan campos requeridos" },
        { status: 400 }
      )
    }

    // Crear documento en una transacción
    const result = await prisma.$transaction(async (tx) => {
      // 1. Crear documento base
      const document = await tx.document.create({
        data: {
          title,
          description: description || null,
          type,
          classification,
          status: "DRAFT",
          createdById: session.user.id,
          // Archivo
          originalFileName: fileName || null,
          storagePath: storagePath || null,
          fileSize: fileSize || null,
          mimeType: mimeType || null,
          // OCR y datos extraídos
          ocrText: ocrText || null,
          ocrConfidence: ocrConfidence || null,
          extractedData: extractedData || null,
        },
      })

      // 2. Si es Guía de Valija, crear registro específico
      if (type.includes("GUIA_VALIJA") && guiaValija) {
        console.log("📋 Creating GuiaValija record:", guiaValija)

        await tx.guiaValija.create({
          data: {
            documentId: document.id,
            numeroGuia: guiaValija.numeroGuia,
            tipoGuia: guiaValija.tipoGuia,
            modalidad: guiaValija.modalidad,
            origen: guiaValija.origen || "N/A",
            destino: guiaValija.destino || "N/A",
            clasificacion: classification,
            createdById: session.user.id,
            // Fechas
            fechaDespacho: guiaValija.fechaDespacho ? new Date(guiaValija.fechaDespacho) : null,
            fechaRecepcion: guiaValija.fechaRecepcion ? new Date(guiaValija.fechaRecepcion) : null,
            // Personal responsable (extraído por Azure)
            preparadoPor: guiaValija.preparadoPor || null,
            revisadoPor: guiaValija.revisadoPor || null,
            receptorFirma: guiaValija.receptorFirma || null,
            // Pesos (extraído por Azure)
            pesoTotalItems: guiaValija.pesoTotalItems ? parseFloat(guiaValija.pesoTotalItems) : null,
            pesoOficial: guiaValija.pesoOficial ? parseFloat(guiaValija.pesoOficial) : null,
            // Totales (extraído por Azure)
            totalItems: guiaValija.totalItems ? parseInt(guiaValija.totalItems) : null,
            // Información de transporte
            numeroGuiaAerea: guiaValija.numeroGuiaAerea || null,
            numeroBolsa: guiaValija.numeroBolsa || null,
            tipoBolsa: guiaValija.tipoBolsa || null,
          },
        })
      }

      // 3. Crear log de auditoría
      await tx.auditLog.create({
        data: {
          action: "DOCUMENT_CREATED",
          entity: "DOCUMENT",
          entityId: document.id,
          userId: session.user.id,
          newValues: {
            title: document.title,
            type: document.type,
            classification: document.classification,
          },
        },
      })

      return document
    })

    console.log("✅ Document created successfully:", result.id)

    return NextResponse.json(
      {
        success: true,
        data: result,
        message: "Documento creado exitosamente",
      },
      { status: 201 }
    )
  } catch (error) {
    console.error("❌ Error creating document:", error)
    return NextResponse.json(
      { error: "Error al crear documento" },
      { status: 500 }
    )
  }
}

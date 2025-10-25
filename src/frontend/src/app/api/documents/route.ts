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
    } = body

    // Validaciones
    if (!title || !type || !classification) {
      return NextResponse.json(
        { error: "Faltan campos requeridos" },
        { status: 400 }
      )
    }

    // Crear documento
    const document = await prisma.document.create({
      data: {
        title,
        description: description || null,
        type,
        classification,
        status: "DRAFT",
        createdById: session.user.id,
      },
      include: {
        creator: {
          select: {
            id: true,
            name: true,
            email: true,
            diplomaticRole: true,
          },
        },
      },
    })

    // Crear log de auditoría
    await prisma.auditLog.create({
      data: {
        action: "DOCUMENT_CREATED",
        entity: "DOCUMENT",
        entityId: document.id,
        userId: session.user.id,
        newValues: {
          title: document.title,
          type: document.type,
        },
      },
    })

    return NextResponse.json(
      {
        success: true,
        data: document,
        message: "Documento creado exitosamente",
      },
      { status: 201 }
    )
  } catch (error) {
    console.error("Error creating document:", error)
    return NextResponse.json(
      { error: "Error al crear documento" },
      { status: 500 }
    )
  }
}

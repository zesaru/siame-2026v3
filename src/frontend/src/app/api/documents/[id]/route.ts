/**
 * API Route: Document by ID
 * GET /api/documents/[id] - Obtener documento
 * PUT /api/documents/[id] - Actualizar documento
 * DELETE /api/documents/[id] - Eliminar documento
 */

import { NextRequest, NextResponse } from "next/server"
import { prisma } from "@/lib/database/prisma"
import { auth } from "@/lib/auth"

interface RouteParams {
  params: {
    id: string
  }
}

// GET /api/documents/[id] - Obtener documento por ID
export async function GET(
  request: NextRequest,
  { params }: RouteParams
) {
  try {
    const session = await auth()

    if (!session?.user) {
      return NextResponse.json(
        { error: "No autenticado" },
        { status: 401 }
      )
    }

    const document = await prisma.document.findUnique({
      where: { id: params.id },
      include: {
        creator: {
          select: {
            id: true,
            name: true,
            email: true,
            diplomaticRole: true,
            securityClearance: true,
          },
        },
        assignee: {
          select: {
            id: true,
            name: true,
            diplomaticRole: true,
          },
        },
        workflow: {
          include: {
            workflow: true,
          },
        },
      },
    })

    if (!document) {
      return NextResponse.json(
        { error: "Documento no encontrado" },
        { status: 404 }
      )
    }

    // TODO: Verificar permisos de acceso según clasificación

    return NextResponse.json({
      success: true,
      data: document,
    })
  } catch (error) {
    console.error("Error fetching document:", error)
    return NextResponse.json(
      { error: "Error al obtener documento" },
      { status: 500 }
    )
  }
}

// PUT /api/documents/[id] - Actualizar documento
export async function PUT(
  request: NextRequest,
  { params }: RouteParams
) {
  try {
    const session = await auth()

    if (!session?.user) {
      return NextResponse.json(
        { error: "No autenticado" },
        { status: 401 }
      )
    }

    const body = await request.json()
    const { title, description, status, classification, metadata } = body

    // Verificar que el documento existe
    const existingDocument = await prisma.document.findUnique({
      where: { id: params.id },
    })

    if (!existingDocument) {
      return NextResponse.json(
        { error: "Documento no encontrado" },
        { status: 404 }
      )
    }

    // TODO: Verificar permisos de edición

    // Actualizar documento
    const document = await prisma.document.update({
      where: { id: params.id },
      data: {
        ...(title && { title }),
        ...(description !== undefined && { description }),
        ...(status && { status }),
        ...(classification && { classification }),
        ...(metadata && { metadata }),
      },
      include: {
        creator: {
          select: {
            id: true,
            name: true,
            email: true,
          },
        },
      },
    })

    // Crear log de auditoría
    await prisma.auditLog.create({
      data: {
        action: "DOCUMENT_UPDATED",
        entityType: "DOCUMENT",
        entityId: document.id,
        userId: session.user.id,
        details: {
          changes: body,
        },
      },
    })

    return NextResponse.json({
      success: true,
      data: document,
      message: "Documento actualizado exitosamente",
    })
  } catch (error) {
    console.error("Error updating document:", error)
    return NextResponse.json(
      { error: "Error al actualizar documento" },
      { status: 500 }
    )
  }
}

// DELETE /api/documents/[id] - Eliminar documento
export async function DELETE(
  request: NextRequest,
  { params }: RouteParams
) {
  try {
    const session = await auth()

    if (!session?.user) {
      return NextResponse.json(
        { error: "No autenticado" },
        { status: 401 }
      )
    }

    // Verificar que el documento existe
    const existingDocument = await prisma.document.findUnique({
      where: { id: params.id },
    })

    if (!existingDocument) {
      return NextResponse.json(
        { error: "Documento no encontrado" },
        { status: 404 }
      )
    }

    // TODO: Verificar permisos de eliminación
    // Solo el creador o admin debería poder eliminar

    // Eliminar documento (soft delete - cambiar status)
    const document = await prisma.document.update({
      where: { id: params.id },
      data: {
        status: "ARCHIVED",
      },
    })

    // Crear log de auditoría
    await prisma.auditLog.create({
      data: {
        action: "DOCUMENT_DELETED",
        entityType: "DOCUMENT",
        entityId: document.id,
        userId: session.user.id,
        details: {
          title: document.title,
        },
      },
    })

    return NextResponse.json({
      success: true,
      message: "Documento eliminado exitosamente",
    })
  } catch (error) {
    console.error("Error deleting document:", error)
    return NextResponse.json(
      { error: "Error al eliminar documento" },
      { status: 500 }
    )
  }
}

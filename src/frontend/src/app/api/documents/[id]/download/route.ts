/**
 * API Route: Descarga de Documentos
 * GET /api/documents/[id]/download - Descargar documento con validacion de permisos
 */

import { NextRequest, NextResponse } from "next/server"
import { auth } from "@/lib/auth"
import { prisma } from "@/lib/database/prisma"
import { hasAccess } from "@/lib/security/clearance"
import { readFile } from "fs/promises"
import path from "path"

/**
 * GET /api/documents/[id]/download
 * Descarga un documento validando permisos de clearance
 */
export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    // 1. Verificar autenticacion
    const session = await auth()

    if (!session?.user?.id) {
      return NextResponse.json(
        { success: false, error: "No autenticado" },
        { status: 401 }
      )
    }

    const { id } = await params

    // 2. Obtener documento con informacion del usuario
    const document = await prisma.document.findUnique({
      where: { id },
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

    if (!document) {
      return NextResponse.json(
        { success: false, error: "Documento no encontrado" },
        { status: 404 }
      )
    }

    // 3. Obtener usuario actual con su clearance
    const currentUser = await prisma.user.findUnique({
      where: { id: session.user.id },
      select: {
        id: true,
        name: true,
        email: true,
        securityClearance: true,
      },
    })

    if (!currentUser) {
      return NextResponse.json(
        { success: false, error: "Usuario no encontrado" },
        { status: 404 }
      )
    }

    // 4. VALIDACION DE CLEARANCE - Verificar permisos
    if (!hasAccess(currentUser.securityClearance, document.classification)) {
      // Registrar intento de acceso no autorizado
      await prisma.auditLog.create({
        data: {
          action: "ACCESS_DENIED",
          entity: "DOCUMENT",
          entityId: document.id,
          userId: currentUser.id,
          oldValues: {
            documentClassification: document.classification,
            userClearance: currentUser.securityClearance,
            reason: "Insufficient clearance level",
          },
        },
      })

      return NextResponse.json(
        {
          success: false,
          error: `Acceso denegado. Este documento requiere clearance ${document.classification} pero tu nivel es ${currentUser.securityClearance}.`,
        },
        { status: 403 }
      )
    }

    // 5. Verificar que el archivo existe
    if (!document.storagePath) {
      return NextResponse.json(
        { success: false, error: "El documento no tiene archivo asociado" },
        { status: 404 }
      )
    }

    // 6. Leer archivo del filesystem
    const filePath = path.join(process.cwd(), "public", document.storagePath)

    let fileBuffer: Buffer
    try {
      fileBuffer = await readFile(filePath)
    } catch (error) {
      console.error("Error reading file:", error)
      return NextResponse.json(
        { success: false, error: "Archivo no encontrado en el sistema" },
        { status: 404 }
      )
    }

    // 7. Registrar acceso exitoso en auditoria
    await prisma.auditLog.create({
      data: {
        action: "DOCUMENT_DOWNLOADED",
        entity: "DOCUMENT",
        entityId: document.id,
        userId: currentUser.id,
        newValues: {
          documentTitle: document.title,
          documentNumber: document.documentNumber,
          fileName: document.originalFileName,
        },
      },
    })

    // 8. Preparar headers de respuesta
    const headers = new Headers()
    headers.set("Content-Type", document.mimeType || "application/octet-stream")
    headers.set(
      "Content-Disposition",
      `attachment; filename="${encodeURIComponent(document.originalFileName || "documento")}"`
    )
    headers.set("Content-Length", fileBuffer.length.toString())
    headers.set("Cache-Control", "no-cache, no-store, must-revalidate")
    headers.set("Pragma", "no-cache")
    headers.set("Expires", "0")

    // Agregar headers de seguridad para documentos clasificados
    if (document.classification !== "PUBLICO") {
      headers.set("X-Content-Type-Options", "nosniff")
      headers.set("X-Frame-Options", "DENY")
      headers.set("X-Classification-Level", document.classification)
    }

    // 9. Retornar archivo
    return new NextResponse(new Uint8Array(fileBuffer), {
      status: 200,
      headers,
    })
  } catch (error) {
    console.error("Error downloading document:", error)
    return NextResponse.json(
      {
        success: false,
        error: error instanceof Error ? error.message : "Error al descargar documento",
      },
      { status: 500 }
    )
  }
}

/**
 * API Route: Upload de Documentos
 * POST /api/documents/upload - Subir nuevo documento
 */

import { NextRequest, NextResponse } from "next/server"
import { auth } from "@/lib/auth"
import { prisma } from "@/lib/database/prisma"
import { saveFile, getFileInfo } from "@/lib/storage/file-storage"
import { SecurityClassification, DocumentType, UnidadRemitente } from "@prisma/client"

// Configuracion para permitir archivos grandes
export const config = {
  api: {
    bodyParser: false,
  },
}

/**
 * POST /api/documents/upload
 * Sube un documento al sistema
 */
export async function POST(request: NextRequest) {
  try {
    // 1. Verificar autenticacion
    const session = await auth()

    if (!session?.user?.id) {
      return NextResponse.json(
        { success: false, error: "No autenticado" },
        { status: 401 }
      )
    }

    // 2. Extraer FormData
    const formData = await request.formData()
    const file = formData.get("file") as File | null
    const title = formData.get("title") as string
    const type = formData.get("type") as DocumentType
    const classification = formData.get("classification") as SecurityClassification
    const unidadRemitente = formData.get("unidadRemitente") as UnidadRemitente | null
    const destino = formData.get("destino") as string | null
    const asunto = formData.get("asunto") as string | null
    const observaciones = formData.get("observaciones") as string | null

    // Datos de Guía de Valija
    const numeroGuia = formData.get("numeroGuia") as string | null
    const tipoGuia = formData.get("tipoGuia") as string | null
    const modalidad = formData.get("modalidad") as string | null
    const origen = formData.get("origen") as string | null
    const preparadoPor = formData.get("preparadoPor") as string | null
    const revisadoPor = formData.get("revisadoPor") as string | null
    const pesoTotalItems = formData.get("pesoTotalItems") as string | null
    const pesoOficial = formData.get("pesoOficial") as string | null
    const totalItems = formData.get("totalItems") as string | null

    // 3. Validaciones basicas
    if (!file) {
      return NextResponse.json(
        { success: false, error: "No se proporciono archivo" },
        { status: 400 }
      )
    }

    if (!title || !type || !classification) {
      return NextResponse.json(
        { success: false, error: "Faltan campos obligatorios: title, type, classification" },
        { status: 400 }
      )
    }

    // 4. Guardar archivo en filesystem
    const saveResult = await saveFile(file, classification)

    if (!saveResult.success) {
      return NextResponse.json(
        { success: false, error: saveResult.error || "Error al guardar archivo" },
        { status: 400 }
      )
    }

    const { fileName, storagePath, checksum } = saveResult
    const fileInfo = getFileInfo(file)

    // 5. Generar numero de documento
    const year = new Date().getFullYear()
    const count = await prisma.document.count({
      where: {
        createdAt: {
          gte: new Date(year, 0, 1),
          lt: new Date(year + 1, 0, 1),
        },
      },
    })
    const documentNumber = `DOC-${year}-${String(count + 1).padStart(5, "0")}`

    // 6. Crear transaccion para Document y FileUpload
    const result = await prisma.$transaction(async (tx) => {
      // 6.1. Crear FileUpload
      const fileUpload = await tx.fileUpload.create({
        data: {
          originalName: fileInfo.originalName,
          fileName: fileName!,
          storagePath: storagePath!,
          fileSize: fileInfo.size,
          mimeType: fileInfo.mimeType,
          checksum: checksum!,
          uploadedById: session.user.id,
        },
      })

      // 6.2. Crear Document
      const document = await tx.document.create({
        data: {
          title,
          type,
          classification,
          status: "DRAFT",
          documentNumber,
          originalFileName: fileInfo.originalName,
          storagePath: storagePath!,
          fileSize: fileInfo.size,
          mimeType: fileInfo.mimeType,
          checksum: checksum!,
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

      // 6.3. Si es Hoja de Remision, crear registro especifico
      if (type.startsWith("HOJA_REMISION_") && unidadRemitente) {
        const hrCount = await tx.hojaRemision.count({
          where: {
            createdAt: {
              gte: new Date(year, 0, 1),
              lt: new Date(year + 1, 0, 1),
            },
          },
        })
        const numeroHR = `HR-${unidadRemitente}-${year}-${String(hrCount + 1).padStart(3, "0")}`

        await tx.hojaRemision.create({
          data: {
            documentId: document.id,
            numeroDocumento: numeroHR,
            unidadRemitente,
            fechaEmision: new Date(),
            asunto: asunto || title,
            destino: destino || "",
            observaciones: observaciones || null,
            clasificacion: classification,
            createdById: session.user.id,
          },
        })
      }

      // 6.4. Si es Guía de Valija, crear registro específico
      // numeroGuia es opcional - puede no ser detectado por Azure
      if (type.includes("GUIA_VALIJA") && tipoGuia && modalidad) {
        // Si no se extrajo numeroGuia, generar uno temporal
        const finalNumeroGuia = numeroGuia || null

        console.log("📋 Creating GuiaValija with data:", {
          numeroGuia: finalNumeroGuia,
          tipoGuia,
          modalidad,
          origen,
          destino,
          preparadoPor,
          revisadoPor,
          pesoTotalItems,
          pesoOficial,
          totalItems,
        })

        await tx.guiaValija.create({
          data: {
            documentId: document.id,
            numeroGuia: finalNumeroGuia,
            tipoGuia: tipoGuia as "ENTRADA" | "SALIDA",
            modalidad: modalidad as "ORDINARIA" | "EXTRAORDINARIA",
            origen: origen || "N/A",
            destino: destino || "N/A",
            clasificacion: classification,
            createdById: session.user.id,
            // Fechas
            fechaDespacho: new Date(), // Por ahora usar fecha actual
            fechaRecepcion: null,
            // Personal responsable (extraído por Azure)
            preparadoPor: preparadoPor || null,
            revisadoPor: revisadoPor || null,
            receptorFirma: null,
            // Pesos (extraído por Azure)
            pesoTotalItems: pesoTotalItems ? parseFloat(pesoTotalItems) : null,
            pesoOficial: pesoOficial ? parseFloat(pesoOficial) : null,
            // Totales (extraído por Azure)
            totalItems: totalItems ? parseInt(totalItems) : null,
            // Información de transporte
            numeroGuiaAerea: null,
            numeroBolsa: null,
            tipoBolsa: null,
          },
        })

        console.log("✅ GuiaValija created successfully")
      }

      // 6.4. Crear log de auditoria
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
            documentNumber: document.documentNumber,
          },
        },
      })

      return { document, fileUpload }
    })

    // 7. Retornar respuesta exitosa
    return NextResponse.json(
      {
        success: true,
        data: {
          document: result.document,
          fileUpload: result.fileUpload,
        },
        message: "Documento subido exitosamente",
      },
      { status: 201 }
    )

  } catch (error) {
    console.error("Error uploading document:", error)
    return NextResponse.json(
      {
        success: false,
        error: error instanceof Error ? error.message : "Error al subir documento"
      },
      { status: 500 }
    )
  }
}

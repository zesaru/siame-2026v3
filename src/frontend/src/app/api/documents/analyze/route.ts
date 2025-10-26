/**
 * API Route: Análisis de Documentos con Azure
 * POST /api/documents/analyze - Analizar documento y extraer datos automáticamente
 */

import { NextRequest, NextResponse } from "next/server"
import { extractDocumentData } from "@/lib/azure/document-intelligence"

/**
 * POST /api/documents/analyze
 * Analiza un documento con Azure Document Intelligence y extrae datos
 */
export async function POST(request: NextRequest) {
  try {
    // Obtener el archivo del FormData
    const formData = await request.formData()
    const file = formData.get("file") as File
    const documentType = formData.get("type") as string | null

    if (!file) {
      return NextResponse.json(
        { success: false, error: "No se proporcionó archivo" },
        { status: 400 }
      )
    }

    // Validar tipo de archivo
    const allowedTypes = [
      "application/pdf",
      "image/jpeg",
      "image/jpg",
      "image/png",
      "image/tiff",
    ]

    if (!allowedTypes.includes(file.type)) {
      return NextResponse.json(
        {
          success: false,
          error: `Tipo de archivo no soportado: ${file.type}`,
        },
        { status: 400 }
      )
    }

    console.log(`📄 Analyzing document: ${file.name} (${file.type})`)

    // Convertir archivo a Buffer
    const arrayBuffer = await file.arrayBuffer()
    const buffer = Buffer.from(arrayBuffer)

    // Extraer datos con Azure
    const result = await extractDocumentData(buffer, documentType || undefined)

    if (!result.success) {
      return NextResponse.json(
        {
          success: false,
          error: result.error || "Error al analizar documento",
        },
        { status: 500 }
      )
    }

    console.log("✅ Document analyzed successfully")

    // Log detallado de los datos extraídos
    if (result.data) {
      console.log("📊 Extracted fields:")
      console.log("  - Asunto:", result.data.asunto || result.data.subject || "N/A")
      console.log("  - Destino:", result.data.destino || result.data.recipient || "N/A")
      console.log("  - Full text length:", result.data.fullText?.length || 0, "chars")
      console.log("  - Confidence:", result.data.confidence, "%")

      console.log("\n📄 PROCESSED DATA JSON:")
      console.log(JSON.stringify(result.data, null, 2))
    }

    // Log del JSON RAW con coordenadas
    if (result.rawAzureResponse) {
      console.log("\n🗺️  RAW AZURE RESPONSE WITH COORDINATES:")
      console.log(JSON.stringify(result.rawAzureResponse, null, 2))
      console.log("\n")
    }

    return NextResponse.json({
      success: true,
      data: result.data,
      rawAzureResponse: result.rawAzureResponse,
    })
  } catch (error) {
    console.error("Error analyzing document:", error)
    return NextResponse.json(
      {
        success: false,
        error:
          error instanceof Error ? error.message : "Error al analizar documento",
      },
      { status: 500 }
    )
  }
}

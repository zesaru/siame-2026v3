"use client"

/**
 * SIAME 2026v3 - Upload de Documentos
 * Formulario para subir nuevos documentos diplomáticos
 */

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select } from "@/components/ui/select"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { useToast } from "@/hooks/use-toast"
import { detectDocumentType } from "@/lib/detection/document-detector"
import { mapAzureDataToForm, generateExtractionSummary } from "@/lib/utils/form-mapper"
import { Sparkles, FileText, Crosshair, UploadCloud, ArrowLeft, ArrowRight } from "lucide-react"
import { BoundingBoxOverlay } from "@/components/document/BoundingBoxOverlay"
import { HojasRemisionTable, HojaRemisionItem } from "@/components/hojas-remision/HojasRemisionTable"
import { parseTableToHojasRemision } from "@/lib/ocr/extractHojaRemision"

export default function UploadDocumentPage() {
  const router = useRouter()
  const { toast } = useToast()

  // Wizard steps
  const [currentStep, setCurrentStep] = useState(1)

  // Upload states
  const [uploading, setUploading] = useState(false)
  const [dragActive, setDragActive] = useState(false)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [autoDetected, setAutoDetected] = useState(false)
  const [detectionConfidence, setDetectionConfidence] = useState(0)
  const [filePreviewUrl, setFilePreviewUrl] = useState<string | null>(null)
  const [detectedPrefix, setDetectedPrefix] = useState<string>("")
  const [analyzingWithAzure, setAnalyzingWithAzure] = useState(false)
  const [azureExtracted, setAzureExtracted] = useState(false)
  const [extractedFields, setExtractedFields] = useState<Set<string>>(new Set())
  const [extractedText, setExtractedText] = useState<string>("")
  const [showExtractedText, setShowExtractedText] = useState(false)
  const [azureRawData, setAzureRawData] = useState<any>(null)
  const [azureRawResponse, setAzureRawResponse] = useState<any>(null)
  const [showJsonData, setShowJsonData] = useState(false)
  const [showRawJson, setShowRawJson] = useState(false)
  const [showBoundingBoxes, setShowBoundingBoxes] = useState(false)

  // Hojas de Remisión states
  const [hojasRemisionItems, setHojasRemisionItems] = useState<HojaRemisionItem[]>([])
  const [savingHojasRemision, setSavingHojasRemision] = useState(false)
  const [guiaValijaId, setGuiaValijaId] = useState<string | null>(null)

  const [formData, setFormData] = useState({
    title: "",
    type: "HOJA_REMISION_OGA",
    classification: "RESTRINGIDO",
    unidadRemitente: "OGA",
    destino: "",
    observaciones: "",

    // Guía de Valija specific fields
    numeroGuia: "",
    tipoGuia: "",
    modalidad: "",
    origen: "",
    preparadoPor: "",
    revisadoPor: "",
    pesoTotalItems: "",
    pesoOficial: "",
    totalItems: "",
  })

  // Cleanup preview URL on unmount
  useEffect(() => {
    return () => {
      if (filePreviewUrl) {
        URL.revokeObjectURL(filePreviewUrl)
      }
    }
  }, [filePreviewUrl])

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    setFormData(prev => ({
      ...prev,
      [e.target.name]: e.target.value
    }))
    // Resetear flag de auto-detección si el usuario modifica manualmente
    if (e.target.name === "type" && autoDetected) {
      setAutoDetected(false)
    }
  }

  /**
   * Analiza el documento con Azure Document Intelligence
   */
  const analyzeDocumentWithAzure = async (file: File, documentType: string) => {
    setAnalyzingWithAzure(true)

    try {
      // Crear FormData para enviar a la API
      const formData = new FormData()
      formData.append("file", file)
      formData.append("type", documentType)

      // Llamar a la API de análisis
      const response = await fetch("/api/documents/analyze", {
        method: "POST",
        body: formData,
      })

      const result = await response.json()

      console.log("🔍 Azure API Response:", result)

      if (result.success && result.data) {
        const extracted = result.data
        console.log("✅ Extracted data from Azure:", extracted)

        // Guardar el JSON procesado de Azure
        setAzureRawData(result.data)

        // Guardar el JSON RAW completo con coordenadas
        if (result.rawAzureResponse) {
          setAzureRawResponse(result.rawAzureResponse)
          console.log("📦 RAW Azure Response received:", result.rawAzureResponse)

          // 📋 PROCESAR TABLAS DE HOJAS DE REMISIÓN
          if (result.rawAzureResponse.tables && result.rawAzureResponse.tables.length > 0) {
            console.log("🔍 Detectadas", result.rawAzureResponse.tables.length, "tablas en el documento")

            // Buscar tabla con 6 columnas (estructura de Guía de Valija)
            const hojasTable = result.rawAzureResponse.tables.find((t: any) => t.columnCount === 6)

            if (hojasTable) {
              console.log("✅ Tabla de Hojas de Remisión encontrada con", hojasTable.rowCount, "filas")

              // Parsear tabla a items de HojaRemision
              const items = parseTableToHojasRemision(hojasTable, formData.classification || "RESTRINGIDO")
              console.log("📝 Items de HR extraídos:", items)

              setHojasRemisionItems(items)

              toast({
                title: "📋 Hojas de Remisión Detectadas",
                description: `Se encontraron ${items.length} items en la guía de valija`,
                variant: "success",
              })
            } else {
              console.log("⚠️ No se encontró tabla con 6 columnas")
            }
          }
        }

        // Guardar el texto completo extraído
        if (extracted.fullText) {
          setExtractedText(extracted.fullText)
        }

        // 🎯 USAR LA NUEVA FUNCIÓN DE MAPEO
        const mappingResult = mapAzureDataToForm(extracted, file.name)

        console.log("📋 Form Mapping Result:", {
          formData: mappingResult.formData,
          fieldsExtracted: Array.from(mappingResult.fieldsExtracted),
          confidence: mappingResult.confidence
        })

        // Actualizar formulario con datos mapeados
        setFormData(prev => {
          // Convertir todos los valores a string para compatibilidad de tipos
          const mappedData = Object.entries(mappingResult.formData).reduce((acc, [key, value]) => {
            if (value !== undefined && value !== null) {
              acc[key] = String(value)
            }
            return acc
          }, {} as Record<string, string>)

          const updated = {
            ...prev,
            ...mappedData
          }
          console.log("🔄 Updating formData:", updated)
          return updated
        })

        setExtractedFields(mappingResult.fieldsExtracted)
        setAzureExtracted(true)

        // Generar mensaje de resumen
        const summary = generateExtractionSummary(
          mappingResult.fieldsExtracted,
          mappingResult.confidence
        )

        toast({
          title: "✨ Datos extraídos con Azure",
          description: summary,
          variant: "success",
        })
      } else {
        // Azure no pudo extraer datos, pero no es un error crítico
        console.log("Azure analysis completed but no data extracted")
      }
    } catch (error) {
      console.error("Error analyzing with Azure:", error)
      // No mostrar error al usuario, solo log
      // El formulario puede continuar con los datos de detección por nombre
    } finally {
      setAnalyzingWithAzure(false)
    }
  }

  /**
   * Procesa un archivo y detecta automáticamente su tipo
   */
  const processFileDetection = async (file: File) => {
    setSelectedFile(file)

    // Crear URL de preview para el archivo
    const previewUrl = URL.createObjectURL(file)
    setFilePreviewUrl(previewUrl)

    // PASO 1: Detectar tipo de documento por nombre de archivo
    const detection = detectDocumentType(file.name)

    if (detection.detected && detection.confidence > 50) {
      // Auto-completar formulario con datos de detección
      setFormData(prev => ({
        ...prev,
        title: detection.suggestedTitle || prev.title,
        type: detection.type || prev.type,
        classification: detection.suggestedClassification || prev.classification,
        unidadRemitente: detection.unidadRemitente || prev.unidadRemitente,
      }))

      setAutoDetected(true)
      setDetectionConfidence(detection.confidence)

      // Guardar el prefijo detectado
      const prefix = detection.metadata?.prefix || ""
      setDetectedPrefix(prefix)

      // Mensaje específico según el tipo detectado
      let detectionMessage = ""
      if (prefix === "HR") {
        detectionMessage = "Hemos detectado una HR - Hoja de Remisión"
      } else if (prefix === "GUIA") {
        detectionMessage = "Hemos detectado una GUIA - Guía de Valija Diplomática"
      } else {
        detectionMessage = `Tipo: ${detection.suggestedTitle}`
      }

      // Notificar al usuario
      toast({
        title: detectionMessage,
        description: `Confianza: ${detection.confidence}%`,
        variant: "info",
      })

      // PASO 2: Analizar con Azure para extraer campos adicionales
      await analyzeDocumentWithAzure(file, detection.type || "")

      // Avanzar automáticamente al Step 2 para revisar el formulario
      setCurrentStep(2)
    } else {
      // No se pudo detectar
      setAutoDetected(false)
      setDetectionConfidence(0)
      setDetectedPrefix("")

      if (detection.confidence > 0) {
        toast({
          title: "Detección parcial",
          description: "Por favor verifica el tipo de documento manualmente",
          variant: "warning",
        })
      }

      // Incluso sin detección, avanzar al Step 2
      setCurrentStep(2)
    }
  }

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true)
    } else if (e.type === "dragleave") {
      setDragActive(false)
    }
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      processFileDetection(e.dataTransfer.files[0])
    }
  }

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      processFileDetection(e.target.files[0])
    }
  }

  /**
   * Guarda todas las Hojas de Remisión detectadas
   */
  const handleSaveHojasRemision = async () => {
    if (!guiaValijaId) {
      toast({
        title: "Error",
        description: "Primero debes guardar la Guía de Valija",
        variant: "destructive",
      })
      return
    }

    if (hojasRemisionItems.length === 0) {
      toast({
        title: "Error",
        description: "No hay hojas de remisión para guardar",
        variant: "destructive",
      })
      return
    }

    setSavingHojasRemision(true)

    try {
      // Preparar datos para el bulk create
      const bulkData = {
        guiaValijaId: guiaValijaId,
        fechaEmision: new Date().toISOString(),
        items: hojasRemisionItems,
      }

      console.log("📤 Enviando bulk create de Hojas de Remisión:", bulkData)

      const response = await fetch("/api/hojas-remision/bulk", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(bulkData),
      })

      const result = await response.json()

      if (!response.ok || !result.success) {
        throw new Error(result.error || "Error al guardar hojas de remisión")
      }

      // Éxito
      toast({
        title: "✅ Hojas de Remisión Guardadas",
        description: result.message || `${result.data.length} hojas de remisión creadas exitosamente`,
        variant: "success",
      })

      // Limpiar items después de guardar
      setHojasRemisionItems([])

      // Opcionalmente redirigir o actualizar UI
      console.log("✅ Hojas de Remisión guardadas:", result.data)
    } catch (error) {
      console.error("Error saving hojas de remision:", error)
      toast({
        title: "Error al guardar hojas de remisión",
        description: error instanceof Error ? error.message : "Ocurrió un error inesperado",
        variant: "destructive",
      })
    } finally {
      setSavingHojasRemision(false)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!selectedFile) {
      toast({
        title: "Error",
        description: "Por favor selecciona un archivo",
        variant: "destructive",
      })
      return
    }

    setUploading(true)

    try {
      // Crear FormData con archivo y metadata
      const uploadData = new FormData()
      uploadData.append("file", selectedFile)
      uploadData.append("title", formData.title)
      uploadData.append("type", formData.type)
      uploadData.append("classification", formData.classification)

      if (formData.unidadRemitente) {
        uploadData.append("unidadRemitente", formData.unidadRemitente)
      }
      if (formData.destino) {
        uploadData.append("destino", formData.destino)
      }
      if (formData.observaciones) {
        uploadData.append("observaciones", formData.observaciones)
      }

      // Guía de Valija fields
      if (formData.numeroGuia) {
        uploadData.append("numeroGuia", formData.numeroGuia)
      }
      if (formData.tipoGuia) {
        uploadData.append("tipoGuia", formData.tipoGuia)
      }
      if (formData.modalidad) {
        uploadData.append("modalidad", formData.modalidad)
      }
      if (formData.origen) {
        uploadData.append("origen", formData.origen)
      }
      if (formData.preparadoPor) {
        uploadData.append("preparadoPor", formData.preparadoPor)
      }
      if (formData.revisadoPor) {
        uploadData.append("revisadoPor", formData.revisadoPor)
      }
      if (formData.pesoTotalItems) {
        uploadData.append("pesoTotalItems", formData.pesoTotalItems)
      }
      if (formData.pesoOficial) {
        uploadData.append("pesoOficial", formData.pesoOficial)
      }
      if (formData.totalItems) {
        uploadData.append("totalItems", formData.totalItems)
      }

      // Enviar a la API
      const response = await fetch("/api/documents/upload", {
        method: "POST",
        body: uploadData,
      })

      const result = await response.json()

      if (!response.ok || !result.success) {
        throw new Error(result.error || "Error al subir documento")
      }

      // Capturar guiaValijaId si es una Guía de Valija
      if (result.data.guiaValija) {
        setGuiaValijaId(result.data.guiaValija.id)
        console.log("✅ Guía de Valija ID capturado:", result.data.guiaValija.id)
      }

      // Exito
      toast({
        title: "Documento subido exitosamente",
        description: `${result.data.document.title} ha sido creado`,
        variant: "success",
      })

      // Si hay hojas de remisión pendientes, no redirigir automáticamente
      if (hojasRemisionItems.length > 0 && guiaValijaId) {
        toast({
          title: "📋 Hojas de Remisión Pendientes",
          description: "Ahora puedes guardar las hojas de remisión detectadas",
          variant: "info",
        })
        return
      }

      // Redirigir a la lista de documentos
      router.push("/documents")
    } catch (error) {
      console.error("Upload error:", error)
      toast({
        title: "Error al subir documento",
        description: error instanceof Error ? error.message : "Ocurrio un error inesperado",
        variant: "destructive",
      })
    } finally {
      setUploading(false)
    }
  }

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return bytes + " B"
    if (bytes < 1048576) return (bytes / 1024).toFixed(1) + " KB"
    return (bytes / 1048576).toFixed(1) + " MB"
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <header className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                Subir Documento
              </h1>
              <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                {currentStep === 1 && "Paso 1 de 2: Selecciona el archivo"}
                {currentStep === 2 && "Paso 2 de 2: Completa la información"}
              </p>
            </div>
            <div className="flex items-center gap-3">
              {/* Progress Indicator */}
              <div className="flex items-center gap-2">
                <div className={`flex items-center justify-center w-8 h-8 rounded-full ${
                  currentStep === 1 ? "bg-blue-600 text-white" : "bg-green-600 text-white"
                }`}>
                  1
                </div>
                <div className={`w-12 h-1 ${currentStep === 2 ? "bg-blue-600" : "bg-gray-300"}`}></div>
                <div className={`flex items-center justify-center w-8 h-8 rounded-full ${
                  currentStep === 2 ? "bg-blue-600 text-white" : "bg-gray-300 text-gray-600"
                }`}>
                  2
                </div>
              </div>
              <Button variant="outline" asChild>
                <Link href="/documents">Cancelar</Link>
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* STEP 1: Upload File */}
        {currentStep === 1 && (
          <div className="max-w-2xl mx-auto">
            <Card>
              <CardHeader className="text-center">
                <CardTitle className="text-2xl">Selecciona un Documento</CardTitle>
                <CardDescription>
                  Arrastra y suelta tu archivo o haz clic para seleccionar
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div
                  className={`border-2 border-dashed rounded-lg p-12 text-center transition-colors ${
                    dragActive
                      ? "border-blue-500 bg-blue-50 dark:bg-blue-900/20"
                      : "border-gray-300 dark:border-gray-700 hover:border-blue-400 dark:hover:border-blue-600"
                  }`}
                  onDragEnter={handleDrag}
                  onDragLeave={handleDrag}
                  onDragOver={handleDrag}
                  onDrop={handleDrop}
                >
                  <input
                    type="file"
                    id="file-upload"
                    className="hidden"
                    accept=".pdf,.jpg,.jpeg,.png,.tiff,.tif"
                    onChange={handleFileChange}
                  />
                  <div className="flex flex-col items-center gap-4">
                    <UploadCloud className="h-16 w-16 text-gray-400" />
                    <div className="text-center">
                      <p className="text-lg font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Arrastra tu archivo aquí
                      </p>
                      <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">
                        o haz clic para seleccionar
                      </p>
                      <label htmlFor="file-upload">
                        <span className="inline-flex items-center justify-center px-6 py-3 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm text-base font-medium text-gray-700 dark:text-gray-200 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700 cursor-pointer transition-colors">
                          Seleccionar Archivo
                        </span>
                      </label>
                    </div>
                    <p className="text-xs text-gray-500 dark:text-gray-400 mt-4">
                      Formatos soportados: PDF, JPG, PNG, TIFF
                    </p>
                  </div>
                </div>

                {analyzingWithAzure && (
                  <div className="mt-6 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                    <div className="flex items-center gap-3">
                      <div className="animate-spin h-5 w-5 border-2 border-blue-600 border-t-transparent rounded-full"></div>
                      <div>
                        <p className="font-medium text-blue-900 dark:text-blue-100">
                          Procesando documento...
                        </p>
                        <p className="text-sm text-blue-700 dark:text-blue-300">
                          Extrayendo información con Azure Document Intelligence
                        </p>
                      </div>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        )}

        {/* STEP 2: Review & Complete */}
        {currentStep === 2 && (
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Layout: Preview on left, Form on right */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* File Preview - Left Side */}
              {filePreviewUrl && (
              <div className="space-y-6">
                <Card>
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <div>
                        <CardTitle className="flex items-center gap-2">
                          <Sparkles className="h-5 w-5 text-blue-500" />
                          Vista Previa del Documento
                        </CardTitle>
                        <CardDescription>
                          {detectedPrefix === "HR" && "Hoja de Remisión detectada"}
                          {detectedPrefix === "GUIA" && "Guía de Valija Diplomática detectada"}
                        </CardDescription>
                      </div>
                      {azureRawResponse && selectedFile?.type.startsWith("image/") && (
                        <Button
                          type="button"
                          variant={showBoundingBoxes ? "default" : "outline"}
                          size="sm"
                          onClick={() => setShowBoundingBoxes(!showBoundingBoxes)}
                        >
                          <Crosshair className="h-4 w-4 mr-2" />
                          {showBoundingBoxes ? "Ocultar" : "Ver"} Coordenadas
                        </Button>
                      )}
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="border rounded-lg overflow-hidden bg-gray-100 dark:bg-gray-800">
                      {selectedFile?.type === "application/pdf" ? (
                        <iframe
                          src={filePreviewUrl}
                          className="w-full h-[85vh]"
                          title="Vista previa del documento"
                        />
                      ) : selectedFile?.type.startsWith("image/") ? (
                        showBoundingBoxes && azureRawResponse ? (
                          <div className="relative max-h-[85vh] overflow-auto">
                            <BoundingBoxOverlay
                              azureResponse={azureRawResponse}
                              imageUrl={filePreviewUrl}
                              containerWidth={800}
                              containerHeight={1100}
                            />
                          </div>
                        ) : (
                          <img
                            src={filePreviewUrl}
                            alt="Vista previa del documento"
                            className="w-full h-auto max-h-[85vh] object-contain"
                          />
                        )
                      ) : (
                        <div className="flex items-center justify-center h-[85vh] text-gray-500">
                          <div className="text-center">
                            <FileText className="h-16 w-16 mx-auto mb-4 text-gray-400" />
                            <p>Vista previa no disponible para este tipo de archivo</p>
                            <p className="text-sm mt-2">{selectedFile?.type}</p>
                          </div>
                        </div>
                      )}
                    </div>
                    <div className="mt-4 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                      <p className="text-sm font-medium text-blue-900 dark:text-blue-100">
                        📄 {selectedFile?.name}
                      </p>
                      <p className="text-xs text-blue-700 dark:text-blue-300 mt-1">
                        {formatFileSize(selectedFile?.size || 0)} • {detectionConfidence}% confianza
                      </p>
                      {analyzingWithAzure && (
                        <div className="mt-3 flex items-center gap-2 text-xs text-blue-600 dark:text-blue-400">
                          <div className="animate-spin h-3 w-3 border-2 border-blue-600 border-t-transparent rounded-full"></div>
                          Analizando con Azure Document Intelligence...
                        </div>
                      )}
                      {azureExtracted && (
                        <div className="mt-3 space-y-2">
                          <div className="flex items-center justify-between">
                            <div className="flex items-center gap-2 text-xs text-green-600 dark:text-green-400">
                              <Sparkles className="h-3 w-3" />
                              {extractedFields.size} campos extraídos automáticamente
                            </div>
                          </div>
                          <div className="grid grid-cols-3 gap-2">
                            {extractedText && (
                              <Button
                                type="button"
                                variant="outline"
                                size="sm"
                                className="h-7 text-xs"
                                onClick={() => {
                                  setShowExtractedText(!showExtractedText)
                                  setShowJsonData(false)
                                  setShowRawJson(false)
                                }}
                              >
                                {showExtractedText ? "Ocultar" : "Ver"} texto
                              </Button>
                            )}
                            {azureRawData && (
                              <Button
                                type="button"
                                variant="outline"
                                size="sm"
                                className="h-7 text-xs"
                                onClick={() => {
                                  setShowJsonData(!showJsonData)
                                  setShowExtractedText(false)
                                  setShowRawJson(false)
                                }}
                              >
                                {showJsonData ? "Ocultar" : "Ver"} datos
                              </Button>
                            )}
                            {azureRawResponse && (
                              <Button
                                type="button"
                                variant="outline"
                                size="sm"
                                className="h-7 text-xs"
                                onClick={() => {
                                  setShowRawJson(!showRawJson)
                                  setShowExtractedText(false)
                                  setShowJsonData(false)
                                }}
                              >
                                {showRawJson ? "Ocultar" : "Ver"} coords
                              </Button>
                            )}
                          </div>
                        </div>
                      )}
                    </div>

                    {/* Texto Extraído por Azure */}
                    {azureExtracted && extractedText && showExtractedText && (
                      <div className="mt-4 p-4 bg-gray-50 dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
                        <div className="flex items-center justify-between mb-2">
                          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
                            📝 Texto Capturado por Azure
                          </h3>
                          <Badge variant="outline" className="text-xs">
                            OCR
                          </Badge>
                        </div>
                        <div className="max-h-96 overflow-y-auto">
                          <pre className="text-xs text-gray-700 dark:text-gray-300 whitespace-pre-wrap font-mono">
                            {extractedText}
                          </pre>
                        </div>
                      </div>
                    )}

                    {/* JSON Datos Procesados */}
                    {azureExtracted && azureRawData && showJsonData && (
                      <div className="mt-4 p-4 bg-gray-50 dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
                        <div className="flex items-center justify-between mb-2">
                          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
                            🔍 Datos Procesados (JSON)
                          </h3>
                          <div className="flex gap-2">
                            <Badge variant="outline" className="text-xs">
                              {azureRawData.confidence}% confianza
                            </Badge>
                            <Button
                              type="button"
                              variant="ghost"
                              size="sm"
                              className="h-6 text-xs"
                              onClick={() => {
                                navigator.clipboard.writeText(JSON.stringify(azureRawData, null, 2))
                                toast({
                                  title: "Copiado",
                                  description: "JSON copiado al portapapeles",
                                  variant: "success",
                                })
                              }}
                            >
                              Copiar
                            </Button>
                          </div>
                        </div>
                        <div className="max-h-96 overflow-y-auto bg-gray-900 dark:bg-gray-950 rounded p-3">
                          <pre className="text-xs text-green-400 font-mono">
                            {JSON.stringify(azureRawData, null, 2)}
                          </pre>
                        </div>
                      </div>
                    )}

                    {/* JSON RAW con Coordenadas */}
                    {azureExtracted && azureRawResponse && showRawJson && (
                      <div className="mt-4 p-4 bg-gray-50 dark:bg-gray-800 rounded-lg border border-blue-300 dark:border-blue-700">
                        <div className="flex items-center justify-between mb-2">
                          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
                            🗺️ Respuesta RAW de Azure con Coordenadas
                          </h3>
                          <div className="flex gap-2">
                            <Badge variant="outline" className="text-xs bg-blue-50 dark:bg-blue-900">
                              {azureRawResponse.pages?.length || 0} páginas
                            </Badge>
                            <Badge variant="outline" className="text-xs bg-blue-50 dark:bg-blue-900">
                              {azureRawResponse.pages?.reduce((sum: number, p: any) => sum + (p.words?.length || 0), 0) || 0} palabras
                            </Badge>
                            <Button
                              type="button"
                              variant="ghost"
                              size="sm"
                              className="h-6 text-xs"
                              onClick={() => {
                                navigator.clipboard.writeText(JSON.stringify(azureRawResponse, null, 2))
                                toast({
                                  title: "Copiado",
                                  description: "JSON RAW con coordenadas copiado",
                                  variant: "success",
                                })
                              }}
                            >
                              Copiar
                            </Button>
                          </div>
                        </div>
                        <div className="max-h-96 overflow-y-auto bg-gray-900 dark:bg-gray-950 rounded p-3">
                          <pre className="text-xs text-cyan-400 font-mono">
                            {JSON.stringify(azureRawResponse, null, 2)}
                          </pre>
                        </div>
                        <div className="mt-3 text-xs text-gray-600 dark:text-gray-400">
                          <p>📍 Este JSON contiene:</p>
                          <ul className="list-disc list-inside mt-1 space-y-1">
                            <li>Coordenadas (polígonos) de cada palabra</li>
                            <li>Coordenadas de líneas y párrafos</li>
                            <li>Tablas con posiciones de celdas</li>
                            <li>Pares clave-valor detectados</li>
                            <li>Regiones delimitadoras (bounding regions)</li>
                          </ul>
                        </div>
                      </div>
                    )}
                  </CardContent>
                </Card>
              </div>
            )}

            {/* Form Section - Right Side (or full width if no preview) */}
            <div className="space-y-6">
          {/* Header con badges */}
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-xl font-bold text-gray-900 dark:text-white">
                Información del Documento
              </h2>
              <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                {azureExtracted
                  ? "Campos completados automáticamente con Azure Document Intelligence"
                  : "Complete los detalles del documento"}
              </p>
            </div>
            <div className="flex items-center gap-2">
              {autoDetected && (
                <Badge variant="info" className="flex items-center gap-1">
                  <Sparkles className="h-3 w-3" />
                  Auto-detectado ({detectionConfidence}%)
                </Badge>
              )}
              {azureExtracted && extractedFields.size > 0 && (
                <Badge variant="success" className="flex items-center gap-1">
                  <FileText className="h-3 w-3" />
                  {extractedFields.size} campos extraídos
                </Badge>
              )}
            </div>
          </div>

          {/* Detalles del Documento */}
          <Card>
            <CardHeader>
              <CardTitle>Detalles del Documento</CardTitle>
              <CardDescription>
                Información extraída automáticamente del documento
              </CardDescription>
            </CardHeader>
              <CardContent className="space-y-4">
                {/* Destino y Origen */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="origen" className="flex items-center gap-2">
                      Origen
                      {extractedFields.has("origen") && (
                        <Sparkles className="h-3 w-3 text-blue-500" />
                      )}
                    </Label>
                    <Input
                      id="origen"
                      name="origen"
                      type="text"
                      placeholder="Ej: Unidad de Valija Diplomática"
                      value={formData.origen}
                      onChange={handleChange}
                      className={extractedFields.has("origen") ? "border-blue-300 bg-blue-50/30" : ""}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="destino" className="flex items-center gap-2">
                      Destino
                      {extractedFields.has("destino") && (
                        <Sparkles className="h-3 w-3 text-blue-500" />
                      )}
                    </Label>
                    <Input
                      id="destino"
                      name="destino"
                      type="text"
                      placeholder="Ej: LEPRU TOKIO"
                      value={formData.destino}
                      onChange={handleChange}
                      className={extractedFields.has("destino") ? "border-blue-300 bg-blue-50/30" : ""}
                    />
                  </div>
                </div>

                {/* Primera fila: Número de Guía, Tipo, Modalidad */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="numeroGuia" className="flex items-center gap-2">
                      Número de Guía
                      {extractedFields.has("numeroGuia") && (
                        <Sparkles className="h-3 w-3 text-blue-500" />
                      )}
                    </Label>
                    <Input
                      id="numeroGuia"
                      name="numeroGuia"
                      type="text"
                      placeholder="Ej: GV-2024-001"
                      value={formData.numeroGuia}
                      onChange={handleChange}
                      className={extractedFields.has("numeroGuia") ? "border-blue-300 bg-blue-50/30" : ""}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="tipoGuia" className="flex items-center gap-2">
                      Tipo de Guía
                      {extractedFields.has("tipoGuia") && (
                        <Sparkles className="h-3 w-3 text-blue-500" />
                      )}
                    </Label>
                    <Select
                      id="tipoGuia"
                      name="tipoGuia"
                      value={formData.tipoGuia}
                      onChange={handleChange}
                      className={extractedFields.has("tipoGuia") ? "border-blue-300 bg-blue-50/30" : ""}
                    >
                      <option value="">Seleccione...</option>
                      <option value="ENTRADA">Entrada</option>
                      <option value="SALIDA">Salida</option>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="modalidad" className="flex items-center gap-2">
                      Modalidad
                      {extractedFields.has("modalidad") && (
                        <Sparkles className="h-3 w-3 text-blue-500" />
                      )}
                    </Label>
                    <Select
                      id="modalidad"
                      name="modalidad"
                      value={formData.modalidad}
                      onChange={handleChange}
                      className={extractedFields.has("modalidad") ? "border-blue-300 bg-blue-50/30" : ""}
                    >
                      <option value="">Seleccione...</option>
                      <option value="ORDINARIA">Ordinaria</option>
                      <option value="EXTRAORDINARIA">Extraordinaria</option>
                    </Select>
                  </div>
                </div>

                {/* Personal Responsable */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="preparadoPor" className="flex items-center gap-2">
                      Preparado Por
                      {extractedFields.has("preparadoPor") && (
                        <Sparkles className="h-3 w-3 text-blue-500" />
                      )}
                    </Label>
                    <Input
                      id="preparadoPor"
                      name="preparadoPor"
                      type="text"
                      placeholder="Nombre del responsable"
                      value={formData.preparadoPor}
                      onChange={handleChange}
                      className={extractedFields.has("preparadoPor") ? "border-blue-300 bg-blue-50/30" : ""}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="revisadoPor" className="flex items-center gap-2">
                      Revisado Por
                      {extractedFields.has("revisadoPor") && (
                        <Sparkles className="h-3 w-3 text-blue-500" />
                      )}
                    </Label>
                    <Input
                      id="revisadoPor"
                      name="revisadoPor"
                      type="text"
                      placeholder="Nombre del revisor"
                      value={formData.revisadoPor}
                      onChange={handleChange}
                      className={extractedFields.has("revisadoPor") ? "border-blue-300 bg-blue-50/30" : ""}
                    />
                  </div>
                </div>

                {/* Cuarta fila: Pesos y Totales */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="pesoTotalItems" className="flex items-center gap-2">
                      Peso Total Items (Kgs)
                      {extractedFields.has("pesoTotalItems") && (
                        <Sparkles className="h-3 w-3 text-blue-500" />
                      )}
                    </Label>
                    <Input
                      id="pesoTotalItems"
                      name="pesoTotalItems"
                      type="number"
                      step="0.001"
                      placeholder="0.000"
                      value={formData.pesoTotalItems}
                      onChange={handleChange}
                      className={extractedFields.has("pesoTotalItems") ? "border-blue-300 bg-blue-50/30" : ""}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="pesoOficial" className="flex items-center gap-2">
                      Peso Oficial (Kgs)
                      {extractedFields.has("pesoOficial") && (
                        <Sparkles className="h-3 w-3 text-blue-500" />
                      )}
                    </Label>
                    <Input
                      id="pesoOficial"
                      name="pesoOficial"
                      type="number"
                      step="0.001"
                      placeholder="0.000"
                      value={formData.pesoOficial}
                      onChange={handleChange}
                      className={extractedFields.has("pesoOficial") ? "border-blue-300 bg-blue-50/30" : ""}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="totalItems" className="flex items-center gap-2">
                      Total de Items
                      {extractedFields.has("totalItems") && (
                        <Sparkles className="h-3 w-3 text-blue-500" />
                      )}
                    </Label>
                    <Input
                      id="totalItems"
                      name="totalItems"
                      type="number"
                      placeholder="0"
                      value={formData.totalItems}
                      onChange={handleChange}
                      className={extractedFields.has("totalItems") ? "border-blue-300 bg-blue-50/30" : ""}
                    />
                  </div>
                </div>
              </CardContent>
            </Card>

          {/* Hojas de Remisión Detectadas */}
          {hojasRemisionItems.length > 0 && (
            <HojasRemisionTable
              items={hojasRemisionItems}
              onItemsChange={setHojasRemisionItems}
              onSave={async () => {
                await handleSaveHojasRemision()
              }}
              isSaving={savingHojasRemision}
            />
          )}

          {/* Botones de Acción */}
          <Card>
            <CardFooter className="flex justify-between pt-6">
              <Button
                type="button"
                variant="outline"
                onClick={() => setCurrentStep(1)}
              >
                <ArrowLeft className="h-4 w-4 mr-2" />
                Volver
              </Button>
              <div className="flex gap-3">
                <Button
                  type="button"
                  variant="outline"
                  disabled={uploading}
                >
                  Guardar como Borrador
                </Button>
                <Button
                  type="submit"
                  disabled={uploading || !selectedFile}
                >
                  {uploading ? "Subiendo..." : "Guardar Documento"}
                  {!uploading && <ArrowRight className="h-4 w-4 ml-2" />}
                </Button>
              </div>
            </CardFooter>
          </Card>
          </div>
          {/* End Form Section */}
        </div>
        {/* End Grid Layout */}
      </form>
    )}
    {/* End Step 2 */}
      </main>
    </div>
  )
}

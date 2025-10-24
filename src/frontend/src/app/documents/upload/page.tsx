"use client"

/**
 * SIAME 2026v3 - Upload de Documentos
 * Formulario para subir nuevos documentos diplomáticos
 */

import { useState } from "react"
import { useRouter } from "next/navigation"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select } from "@/components/ui/select"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"

export default function UploadDocumentPage() {
  const router = useRouter()
  const [uploading, setUploading] = useState(false)
  const [dragActive, setDragActive] = useState(false)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)

  const [formData, setFormData] = useState({
    title: "",
    type: "HOJA_REMISION_OGA",
    classification: "RESTRINGIDO",
    unidadRemitente: "OGA",
    destino: "",
    asunto: "",
    observaciones: "",
  })

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    setFormData(prev => ({
      ...prev,
      [e.target.name]: e.target.value
    }))
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
      setSelectedFile(e.dataTransfer.files[0])
    }
  }

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0])
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setUploading(true)

    try {
      // TODO: Implementar upload real con FormData y API
      await new Promise(resolve => setTimeout(resolve, 2000))

      // Simulación exitosa
      alert("Documento subido exitosamente")
      router.push("/documents")
    } catch (error) {
      alert("Error al subir el documento")
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
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                Subir Documento
              </h1>
              <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                Añade un nuevo documento al sistema
              </p>
            </div>
            <Button variant="outline" asChild>
              <Link href="/documents">Cancelar</Link>
            </Button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Upload Area */}
          <Card>
            <CardHeader>
              <CardTitle>Archivo</CardTitle>
              <CardDescription>
                Arrastra y suelta o haz clic para seleccionar un archivo
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div
                className={`relative border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
                  dragActive
                    ? "border-blue-500 bg-blue-50 dark:bg-blue-900/10"
                    : "border-gray-300 dark:border-gray-700 hover:border-gray-400 dark:hover:border-gray-600"
                }`}
                onDragEnter={handleDrag}
                onDragLeave={handleDrag}
                onDragOver={handleDrag}
                onDrop={handleDrop}
              >
                <input
                  type="file"
                  id="file-upload"
                  className="sr-only"
                  onChange={handleFileChange}
                  accept=".pdf,.doc,.docx,.jpg,.jpeg,.png,.tiff"
                />

                {selectedFile ? (
                  <div className="space-y-4">
                    <div className="flex items-center justify-center gap-4">
                      <svg className="w-12 h-12 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                        <path d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z" />
                      </svg>
                      <div className="text-left">
                        <p className="text-sm font-medium text-gray-900 dark:text-white">
                          {selectedFile.name}
                        </p>
                        <p className="text-xs text-gray-500 dark:text-gray-400">
                          {formatFileSize(selectedFile.size)}
                        </p>
                      </div>
                    </div>
                    <Button
                      type="button"
                      variant="outline"
                      size="sm"
                      onClick={() => setSelectedFile(null)}
                    >
                      Cambiar archivo
                    </Button>
                  </div>
                ) : (
                  <label htmlFor="file-upload" className="cursor-pointer">
                    <svg
                      className="mx-auto h-12 w-12 text-gray-400"
                      stroke="currentColor"
                      fill="none"
                      viewBox="0 0 48 48"
                    >
                      <path
                        d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02"
                        strokeWidth={2}
                        strokeLinecap="round"
                        strokeLinejoin="round"
                      />
                    </svg>
                    <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
                      <span className="font-semibold text-blue-600 hover:text-blue-500">
                        Haz clic para subir
                      </span>{" "}
                      o arrastra y suelta
                    </p>
                    <p className="text-xs text-gray-500 dark:text-gray-500 mt-1">
                      PDF, DOC, DOCX, JPG, PNG, TIFF hasta 50MB
                    </p>
                  </label>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Información Básica */}
          <Card>
            <CardHeader>
              <CardTitle>Información Básica</CardTitle>
              <CardDescription>
                Proporciona los detalles del documento
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="title">Título del Documento *</Label>
                <Input
                  id="title"
                  name="title"
                  type="text"
                  placeholder="Ej: Hoja de Remisión OGA-2024-001"
                  value={formData.title}
                  onChange={handleChange}
                  required
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="type">Tipo de Documento *</Label>
                  <Select
                    id="type"
                    name="type"
                    value={formData.type}
                    onChange={handleChange}
                    required
                  >
                    <option value="HOJA_REMISION_OGA">Hoja de Remisión OGA</option>
                    <option value="HOJA_REMISION_PCO">Hoja de Remisión PCO</option>
                    <option value="HOJA_REMISION_PRU">Hoja de Remisión PRU</option>
                    <option value="GUIA_VALIJA">Guía de Valija</option>
                    <option value="NOTA_VERBAL">Nota Verbal</option>
                    <option value="TELEGRAMA_ORDINARIO">Telegrama Ordinario</option>
                    <option value="TELEGRAMA_CIFRADO">Telegrama Cifrado</option>
                    <option value="INFORME">Informe</option>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="classification">Clasificación *</Label>
                  <Select
                    id="classification"
                    name="classification"
                    value={formData.classification}
                    onChange={handleChange}
                    required
                  >
                    <option value="PUBLICO">Público</option>
                    <option value="RESTRINGIDO">Restringido</option>
                    <option value="CONFIDENCIAL">Confidencial</option>
                    <option value="SECRETO">Secreto</option>
                    <option value="ALTO_SECRETO">Alto Secreto</option>
                  </Select>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Detalles Específicos */}
          <Card>
            <CardHeader>
              <CardTitle>Detalles del Documento</CardTitle>
              <CardDescription>
                Información adicional según el tipo de documento
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="unidadRemitente">Unidad Remitente</Label>
                  <Select
                    id="unidadRemitente"
                    name="unidadRemitente"
                    value={formData.unidadRemitente}
                    onChange={handleChange}
                  >
                    <option value="OGA">OGA - Oficina de Gestión y Análisis</option>
                    <option value="PCO">PCO - Protocolo y Ceremonial</option>
                    <option value="PRU">PRU - Prensa</option>
                    <option value="CON">CON - Consulares</option>
                    <option value="ADM">ADM - Administración</option>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="destino">Destino</Label>
                  <Input
                    id="destino"
                    name="destino"
                    type="text"
                    placeholder="Ej: Embajada de España en París"
                    value={formData.destino}
                    onChange={handleChange}
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="asunto">Asunto</Label>
                <Input
                  id="asunto"
                  name="asunto"
                  type="text"
                  placeholder="Breve descripción del asunto"
                  value={formData.asunto}
                  onChange={handleChange}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="observaciones">Observaciones</Label>
                <textarea
                  id="observaciones"
                  name="observaciones"
                  rows={4}
                  className="flex w-full rounded-md border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 px-3 py-2 text-sm ring-offset-white dark:ring-offset-gray-950 placeholder:text-gray-500 dark:placeholder:text-gray-400 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 dark:focus-visible:ring-blue-400 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                  placeholder="Información adicional, instrucciones especiales, etc."
                  value={formData.observaciones}
                  onChange={handleChange}
                />
              </div>
            </CardContent>
          </Card>

          {/* Botones de Acción */}
          <Card>
            <CardFooter className="flex justify-between pt-6">
              <Button type="button" variant="outline" asChild>
                <Link href="/documents">Cancelar</Link>
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
                  {uploading ? "Subiendo..." : "Subir Documento"}
                </Button>
              </div>
            </CardFooter>
          </Card>
        </form>
      </main>
    </div>
  )
}

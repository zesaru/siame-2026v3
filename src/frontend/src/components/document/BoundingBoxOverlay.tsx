"use client"

/**
 * SIAME 2026v3 - Bounding Box Overlay Component
 * Visualiza las coordenadas de Azure sobre el documento
 */

import { useEffect, useRef, useState } from "react"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Eye, EyeOff } from "lucide-react"

interface BoundingBoxOverlayProps {
  azureResponse: any
  imageUrl: string
  containerWidth: number
  containerHeight: number
}

type LayerType = "words" | "lines" | "tables" | "keyValuePairs"

export function BoundingBoxOverlay({
  azureResponse,
  imageUrl,
  containerWidth,
  containerHeight,
}: BoundingBoxOverlayProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const imgRef = useRef<HTMLImageElement>(null)
  const [imageDimensions, setImageDimensions] = useState({ width: 0, height: 0 })
  const [visibleLayers, setVisibleLayers] = useState<Set<LayerType>>(
    new Set(["words"])
  )

  // Cargar dimensiones de la imagen
  useEffect(() => {
    const img = new Image()
    img.onload = () => {
      setImageDimensions({ width: img.width, height: img.height })
    }
    img.src = imageUrl
  }, [imageUrl])

  // Dibujar bounding boxes cuando cambien las capas visibles
  useEffect(() => {
    if (!canvasRef.current || !azureResponse || !imageDimensions.width) return

    const canvas = canvasRef.current
    const ctx = canvas.getContext("2d")
    if (!ctx) return

    // Limpiar canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height)

    // Obtener la primera página
    const page = azureResponse.pages?.[0]
    if (!page) return

    // Calcular escala
    const scaleX = containerWidth / (page.width || 1)
    const scaleY = containerHeight / (page.height || 1)

    console.log("📐 Drawing bounding boxes:")
    console.log("  Page dimensions:", page.width, "x", page.height, page.unit)
    console.log("  Container dimensions:", containerWidth, "x", containerHeight, "px")
    console.log("  Scale:", scaleX, "x", scaleY)

    // Dibujar palabras
    if (visibleLayers.has("words") && page.words) {
      ctx.strokeStyle = "rgba(0, 255, 0, 0.8)"
      ctx.lineWidth = 1
      ctx.fillStyle = "rgba(0, 255, 0, 0.1)"

      page.words.forEach((word: any, idx: number) => {
        if (word.polygon && word.polygon.length >= 8) {
          ctx.beginPath()
          // Azure devuelve polígonos como [x1, y1, x2, y2, x3, y3, x4, y4]
          ctx.moveTo(word.polygon[0] * scaleX, word.polygon[1] * scaleY)
          ctx.lineTo(word.polygon[2] * scaleX, word.polygon[3] * scaleY)
          ctx.lineTo(word.polygon[4] * scaleX, word.polygon[5] * scaleY)
          ctx.lineTo(word.polygon[6] * scaleX, word.polygon[7] * scaleY)
          ctx.closePath()
          ctx.fill()
          ctx.stroke()

          // Mostrar texto en las primeras 10 palabras para debug
          if (idx < 10) {
            ctx.fillStyle = "rgba(255, 255, 255, 0.9)"
            ctx.fillRect(
              word.polygon[0] * scaleX - 2,
              word.polygon[1] * scaleY - 12,
              ctx.measureText(word.content).width + 4,
              14
            )
            ctx.fillStyle = "rgba(0, 0, 0, 0.9)"
            ctx.font = "10px monospace"
            ctx.fillText(word.content, word.polygon[0] * scaleX, word.polygon[1] * scaleY)
          }
        }
      })

      console.log(`  ✅ Drew ${page.words.length} word boxes`)
    }

    // Dibujar líneas
    if (visibleLayers.has("lines") && page.lines) {
      ctx.strokeStyle = "rgba(0, 150, 255, 0.8)"
      ctx.lineWidth = 2
      ctx.fillStyle = "rgba(0, 150, 255, 0.05)"

      page.lines.forEach((line: any) => {
        if (line.polygon && line.polygon.length >= 8) {
          ctx.beginPath()
          ctx.moveTo(line.polygon[0] * scaleX, line.polygon[1] * scaleY)
          ctx.lineTo(line.polygon[2] * scaleX, line.polygon[3] * scaleY)
          ctx.lineTo(line.polygon[4] * scaleX, line.polygon[5] * scaleY)
          ctx.lineTo(line.polygon[6] * scaleX, line.polygon[7] * scaleY)
          ctx.closePath()
          ctx.fill()
          ctx.stroke()
        }
      })

      console.log(`  ✅ Drew ${page.lines.length} line boxes`)
    }

    // Dibujar tablas
    if (visibleLayers.has("tables") && azureResponse.tables) {
      ctx.strokeStyle = "rgba(255, 165, 0, 0.9)"
      ctx.lineWidth = 3
      ctx.fillStyle = "rgba(255, 165, 0, 0.1)"

      azureResponse.tables.forEach((table: any) => {
        if (table.boundingRegions && table.boundingRegions.length > 0) {
          const region = table.boundingRegions[0]
          if (region.polygon && region.polygon.length >= 8) {
            ctx.beginPath()
            ctx.moveTo(region.polygon[0] * scaleX, region.polygon[1] * scaleY)
            ctx.lineTo(region.polygon[2] * scaleX, region.polygon[3] * scaleY)
            ctx.lineTo(region.polygon[4] * scaleX, region.polygon[5] * scaleY)
            ctx.lineTo(region.polygon[6] * scaleX, region.polygon[7] * scaleY)
            ctx.closePath()
            ctx.fill()
            ctx.stroke()

            // Etiqueta de tabla
            ctx.fillStyle = "rgba(255, 165, 0, 0.9)"
            ctx.font = "12px bold monospace"
            ctx.fillText(
              `Tabla ${table.rowCount}x${table.columnCount}`,
              region.polygon[0] * scaleX,
              region.polygon[1] * scaleY - 5
            )
          }
        }
      })

      console.log(`  ✅ Drew ${azureResponse.tables.length} table boxes`)
    }

    // Dibujar key-value pairs
    if (visibleLayers.has("keyValuePairs") && azureResponse.keyValuePairs) {
      azureResponse.keyValuePairs.forEach((kvp: any) => {
        // Dibujar key
        if (kvp.key?.boundingRegions?.[0]?.polygon) {
          const polygon = kvp.key.boundingRegions[0].polygon
          ctx.strokeStyle = "rgba(255, 0, 255, 0.8)"
          ctx.lineWidth = 2
          ctx.fillStyle = "rgba(255, 0, 255, 0.1)"
          ctx.beginPath()
          ctx.moveTo(polygon[0] * scaleX, polygon[1] * scaleY)
          ctx.lineTo(polygon[2] * scaleX, polygon[3] * scaleY)
          ctx.lineTo(polygon[4] * scaleX, polygon[5] * scaleY)
          ctx.lineTo(polygon[6] * scaleX, polygon[7] * scaleY)
          ctx.closePath()
          ctx.fill()
          ctx.stroke()
        }

        // Dibujar value
        if (kvp.value?.boundingRegions?.[0]?.polygon) {
          const polygon = kvp.value.boundingRegions[0].polygon
          ctx.strokeStyle = "rgba(128, 0, 255, 0.8)"
          ctx.lineWidth = 2
          ctx.fillStyle = "rgba(128, 0, 255, 0.1)"
          ctx.beginPath()
          ctx.moveTo(polygon[0] * scaleX, polygon[1] * scaleY)
          ctx.lineTo(polygon[2] * scaleX, polygon[3] * scaleY)
          ctx.lineTo(polygon[4] * scaleX, polygon[5] * scaleY)
          ctx.lineTo(polygon[6] * scaleX, polygon[7] * scaleY)
          ctx.closePath()
          ctx.fill()
          ctx.stroke()
        }
      })

      console.log(`  ✅ Drew ${azureResponse.keyValuePairs.length} key-value pair boxes`)
    }
  }, [azureResponse, visibleLayers, containerWidth, containerHeight, imageDimensions])

  const toggleLayer = (layer: LayerType) => {
    setVisibleLayers(prev => {
      const newSet = new Set(prev)
      if (newSet.has(layer)) {
        newSet.delete(layer)
      } else {
        newSet.add(layer)
      }
      return newSet
    })
  }

  const page = azureResponse?.pages?.[0]
  if (!page) return null

  return (
    <div className="relative">
      {/* Imagen de fondo */}
      <img
        ref={imgRef}
        src={imageUrl}
        alt="Document preview"
        className="w-full h-auto"
        style={{ display: "block" }}
      />

      {/* Canvas overlay */}
      <canvas
        ref={canvasRef}
        width={containerWidth}
        height={containerHeight}
        className="absolute top-0 left-0 pointer-events-none"
        style={{
          width: "100%",
          height: "auto",
        }}
      />

      {/* Controles de capas */}
      <div className="absolute top-2 right-2 flex flex-col gap-2">
        <div className="bg-white/90 dark:bg-gray-900/90 rounded-lg p-2 shadow-lg">
          <p className="text-xs font-semibold mb-2">Capas:</p>
          <div className="flex flex-col gap-1">
            <Button
              size="sm"
              variant={visibleLayers.has("words") ? "default" : "outline"}
              className="h-7 text-xs justify-start"
              onClick={() => toggleLayer("words")}
            >
              {visibleLayers.has("words") ? <Eye className="h-3 w-3 mr-1" /> : <EyeOff className="h-3 w-3 mr-1" />}
              <span className="w-2 h-2 bg-green-500 rounded-full mr-1"></span>
              Palabras ({page.words?.length || 0})
            </Button>
            <Button
              size="sm"
              variant={visibleLayers.has("lines") ? "default" : "outline"}
              className="h-7 text-xs justify-start"
              onClick={() => toggleLayer("lines")}
            >
              {visibleLayers.has("lines") ? <Eye className="h-3 w-3 mr-1" /> : <EyeOff className="h-3 w-3 mr-1" />}
              <span className="w-2 h-2 bg-blue-500 rounded-full mr-1"></span>
              Líneas ({page.lines?.length || 0})
            </Button>
            {azureResponse.tables && azureResponse.tables.length > 0 && (
              <Button
                size="sm"
                variant={visibleLayers.has("tables") ? "default" : "outline"}
                className="h-7 text-xs justify-start"
                onClick={() => toggleLayer("tables")}
              >
                {visibleLayers.has("tables") ? <Eye className="h-3 w-3 mr-1" /> : <EyeOff className="h-3 w-3 mr-1" />}
                <span className="w-2 h-2 bg-orange-500 rounded-full mr-1"></span>
                Tablas ({azureResponse.tables.length})
              </Button>
            )}
            {azureResponse.keyValuePairs && azureResponse.keyValuePairs.length > 0 && (
              <Button
                size="sm"
                variant={visibleLayers.has("keyValuePairs") ? "default" : "outline"}
                className="h-7 text-xs justify-start"
                onClick={() => toggleLayer("keyValuePairs")}
              >
                {visibleLayers.has("keyValuePairs") ? <Eye className="h-3 w-3 mr-1" /> : <EyeOff className="h-3 w-3 mr-1" />}
                <span className="w-2 h-2 bg-purple-500 rounded-full mr-1"></span>
                Campos ({azureResponse.keyValuePairs.length})
              </Button>
            )}
          </div>
        </div>

        <div className="bg-blue-500/90 rounded-lg p-2 shadow-lg">
          <p className="text-xs font-semibold text-white mb-1">Estadísticas:</p>
          <div className="text-xs text-white space-y-0.5">
            <div>📄 Páginas: {azureResponse.pages?.length || 0}</div>
            <div>📝 Palabras: {page.words?.length || 0}</div>
            <div>📏 Líneas: {page.lines?.length || 0}</div>
          </div>
        </div>
      </div>
    </div>
  )
}

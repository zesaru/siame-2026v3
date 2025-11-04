"use client"

/**
 * SIAME 2026v3 - Tabla Editable de Hojas de Remisión
 * Componente para mostrar y editar items de HR detectados por Azure OCR
 */

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Select } from "@/components/ui/select"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Badge } from "@/components/ui/badge"
import { Trash2, Plus, Save } from "lucide-react"

export interface HojaRemisionItem {
  // Datos de la tabla OCR
  orden: number
  destinatario: string
  contenido: string // "HR Nº5-18-A/ 11 CAJA"
  remitente: string // "DAC"
  cantidad: number
  peso: number

  // Campos adicionales para el formulario
  numeroDocumento: string // Extraído de contenido: "5-18-A/11"
  tipoEmbalaje: string // Extraído de contenido: "CAJA", "SOBRE", "11 CAJA", etc
  asunto: string // Asunto del documento (usuario lo completa)
  clasificacion: string
  observaciones?: string
}

interface HojasRemisionTableProps {
  items: HojaRemisionItem[]
  onItemsChange: (items: HojaRemisionItem[]) => void
  onSave: () => void
  isSaving?: boolean
}

export function HojasRemisionTable({
  items,
  onItemsChange,
  onSave,
  isSaving = false,
}: HojasRemisionTableProps) {
  const [editingIndex, setEditingIndex] = useState<number | null>(null)

  const updateItem = (index: number, field: keyof HojaRemisionItem, value: any) => {
    const newItems = [...items]
    newItems[index] = { ...newItems[index], [field]: value }
    onItemsChange(newItems)
  }

  const removeItem = (index: number) => {
    const newItems = items.filter((_, i) => i !== index)
    onItemsChange(newItems)
  }

  const addItem = () => {
    const newItem: HojaRemisionItem = {
      orden: items.length + 1,
      destinatario: "",
      contenido: "",
      remitente: "",
      cantidad: 1,
      peso: 0,
      numeroDocumento: "",
      tipoEmbalaje: "",
      asunto: "",
      clasificacion: "RESTRINGIDO",
    }
    onItemsChange([...items, newItem])
    setEditingIndex(items.length)
  }

  const clasificaciones = [
    "PUBLICO",
    "RESTRINGIDO",
    "CONFIDENCIAL",
    "SECRETO",
    "ALTO_SECRETO",
  ]

  return (
    <Card className="mt-6">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle>Hojas de Remisión Detectadas</CardTitle>
            <CardDescription>
              {items.length} item{items.length !== 1 ? "s" : ""} encontrado{items.length !== 1 ? "s" : ""} en la guía.
              Revise y edite los datos antes de guardar.
            </CardDescription>
          </div>
          <Button onClick={onSave} disabled={isSaving || items.length === 0}>
            <Save className="mr-2 h-4 w-4" />
            {isSaving ? "Guardando..." : "Guardar Todas"}
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {items.map((item, index) => (
            <Card key={index} className="border-l-4 border-l-primary">
              <CardContent className="pt-6">
                <div className="grid gap-4">
                  {/* Header del item */}
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Badge variant="outline">HR #{item.orden}</Badge>
                      <span className="text-sm font-medium">
                        {item.destinatario || "(Sin destinatario)"}
                      </span>
                    </div>
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => removeItem(index)}
                      className="text-destructive hover:text-destructive"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>

                  {/* Grid de campos editables */}
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {/* Destinatario */}
                    <div className="space-y-2">
                      <label className="text-sm font-medium text-muted-foreground">
                        Destinatario
                      </label>
                      <Input
                        value={item.destinatario}
                        onChange={(e) => updateItem(index, "destinatario", e.target.value)}
                        placeholder="LEPRU TOKIO"
                      />
                    </div>

                    {/* Número de Documento */}
                    <div className="space-y-2">
                      <label className="text-sm font-medium text-muted-foreground">
                        Número de Documento
                      </label>
                      <Input
                        value={item.numeroDocumento}
                        onChange={(e) => updateItem(index, "numeroDocumento", e.target.value)}
                        placeholder="5-18-A/11"
                      />
                    </div>

                    {/* Tipo de Embalaje */}
                    <div className="space-y-2">
                      <label className="text-sm font-medium text-muted-foreground">
                        Tipo de Embalaje
                      </label>
                      <Input
                        value={item.tipoEmbalaje}
                        onChange={(e) => updateItem(index, "tipoEmbalaje", e.target.value.toUpperCase())}
                        placeholder="CAJA, SOBRE, PAQUETE"
                      />
                    </div>

                    {/* Asunto */}
                    <div className="space-y-2">
                      <label className="text-sm font-medium text-muted-foreground">
                        Asunto
                      </label>
                      <Input
                        value={item.asunto}
                        onChange={(e) => updateItem(index, "asunto", e.target.value)}
                        placeholder="Descripción del asunto"
                      />
                    </div>

                    {/* Remitente */}
                    <div className="space-y-2">
                      <label className="text-sm font-medium text-muted-foreground">
                        Remitente (Sigla)
                      </label>
                      <Input
                        value={item.remitente}
                        onChange={(e) => updateItem(index, "remitente", e.target.value.toUpperCase())}
                        placeholder="DAC"
                      />
                    </div>

                    {/* Cantidad */}
                    <div className="space-y-2">
                      <label className="text-sm font-medium text-muted-foreground">
                        Cantidad
                      </label>
                      <Input
                        type="number"
                        value={item.cantidad}
                        onChange={(e) => updateItem(index, "cantidad", parseInt(e.target.value) || 0)}
                        min="1"
                      />
                    </div>

                    {/* Peso */}
                    <div className="space-y-2">
                      <label className="text-sm font-medium text-muted-foreground">
                        Peso (Kg)
                      </label>
                      <Input
                        type="number"
                        step="0.001"
                        value={item.peso}
                        onChange={(e) => updateItem(index, "peso", parseFloat(e.target.value) || 0)}
                        min="0"
                      />
                    </div>

                    {/* Clasificación */}
                    <div className="space-y-2">
                      <label className="text-sm font-medium text-muted-foreground">
                        Clasificación
                      </label>
                      <Select
                        value={item.clasificacion}
                        onChange={(e) => updateItem(index, "clasificacion", e.target.value)}
                      >
                        {clasificaciones.map((c) => (
                          <option key={c} value={c}>
                            {c.replace(/_/g, " ")}
                          </option>
                        ))}
                      </Select>
                    </div>

                    {/* Contenido Original (solo lectura) */}
                    <div className="space-y-2 md:col-span-2">
                      <label className="text-sm font-medium text-muted-foreground">
                        Contenido Original (OCR)
                      </label>
                      <div className="px-3 py-2 text-sm bg-muted rounded-md text-muted-foreground">
                        {item.contenido}
                      </div>
                    </div>
                  </div>

                  {/* Observaciones */}
                  <div className="space-y-2">
                    <label className="text-sm font-medium text-muted-foreground">
                      Observaciones
                    </label>
                    <Input
                      value={item.observaciones || ""}
                      onChange={(e) => updateItem(index, "observaciones", e.target.value)}
                      placeholder="Observaciones adicionales (opcional)"
                    />
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}

          {/* Botón para agregar item manual */}
          <Button
            variant="outline"
            onClick={addItem}
            className="w-full"
          >
            <Plus className="mr-2 h-4 w-4" />
            Agregar Hoja de Remisión Manual
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}

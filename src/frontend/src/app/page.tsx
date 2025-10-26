/**
 * SIAME 2026v3 - Página Principal
 * Redirección automática al login
 */

"use client"

import { useEffect } from "react"
import { useRouter } from "next/navigation"
import { LoadingPage } from "@/components/ui/spinner"

export default function Home() {
  const router = useRouter()

  useEffect(() => {
    router.push("/auth/login")
  }, [router])

  return <LoadingPage message="Redirigiendo al login..." />
}

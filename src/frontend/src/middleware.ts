/**
 * NextAuth.js Middleware
 * Protege rutas que requieren autenticación
 */

import { auth } from "@/lib/auth"
import { NextResponse } from "next/server"

export default auth((req) => {
  const { nextUrl } = req
  const isLoggedIn = !!req.auth

  // Rutas públicas que no requieren autenticación
  const publicRoutes = ["/", "/auth/login", "/auth/register", "/auth/error"]
  const isPublicRoute = publicRoutes.some(route => nextUrl.pathname === route || nextUrl.pathname.startsWith(route + "/"))

  // Rutas protegidas que requieren autenticación
  const protectedRoutes = ["/dashboard", "/documents", "/workflows", "/admin", "/reports"]
  const isProtectedRoute = protectedRoutes.some(route => nextUrl.pathname.startsWith(route))

  // Si está en una ruta protegida y no está autenticado
  if (isProtectedRoute && !isLoggedIn) {
    const loginUrl = new URL("/auth/login", nextUrl.origin)
    loginUrl.searchParams.set("callbackUrl", nextUrl.pathname)
    return NextResponse.redirect(loginUrl)
  }

  // Si está autenticado y trata de ir a login/register, redirigir al dashboard
  if (isLoggedIn && (nextUrl.pathname === "/auth/login" || nextUrl.pathname === "/auth/register")) {
    return NextResponse.redirect(new URL("/dashboard", nextUrl.origin))
  }

  return NextResponse.next()
})

// Configuración del matcher - Excluir assets estáticos
export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - api (API routes)
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     * - public files (images, etc)
     */
    "/((?!api|_next/static|_next/image|favicon.ico|.*\\.png|.*\\.jpg|.*\\.svg).*)",
  ],
}

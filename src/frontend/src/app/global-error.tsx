'use client'

/**
 * Global Error Component
 * Error handler de nivel raíz
 */

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  return (
    <html>
      <body>
        <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
          <div className="max-w-md w-full text-center">
            <h1 className="text-6xl font-bold text-gray-900 mb-4">
              Error
            </h1>
            <p className="text-xl text-gray-600 mb-8">
              Algo salió mal
            </p>
            <p className="text-sm text-gray-500 mb-8">
              {error.message || 'Ha ocurrido un error inesperado'}
            </p>
            <button
              onClick={reset}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              Intentar de nuevo
            </button>
          </div>
        </div>
      </body>
    </html>
  )
}

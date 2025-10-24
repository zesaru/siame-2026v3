'use client'

/**
 * Error Component
 * Página de error global para la aplicación
 */

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900 px-4">
      <div className="max-w-md w-full text-center">
        <h1 className="text-6xl font-bold text-gray-900 dark:text-white mb-4">
          Error
        </h1>
        <p className="text-xl text-gray-600 dark:text-gray-400 mb-8">
          Algo salió mal
        </p>
        <p className="text-sm text-gray-500 dark:text-gray-500 mb-8">
          {error.message || 'Ha ocurrido un error inesperado'}
        </p>
        <button
          onClick={reset}
          className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          Intentar de nuevo
        </button>
      </div>
    </div>
  )
}

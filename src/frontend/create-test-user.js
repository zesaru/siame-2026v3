/**
 * Script para crear un usuario de prueba con contraseña conocida
 */

const { PrismaClient } = require('@prisma/client')
const bcrypt = require('bcryptjs')

const prisma = new PrismaClient()

async function main() {
  console.log('🔐 Creando usuario de prueba...')

  // Eliminar usuario si existe
  await prisma.user.deleteMany({
    where: { email: 'test@maeuec.es' }
  })

  // Crear hash de la contraseña
  const password = 'test123'
  const hashedPassword = await bcrypt.hash(password, 10)

  console.log('📝 Contraseña:', password)
  console.log('🔒 Hash:', hashedPassword)

  // Crear usuario
  const user = await prisma.user.create({
    data: {
      name: 'Usuario Prueba',
      email: 'test@maeuec.es',
      password: hashedPassword,
      diplomaticRole: 'TERCER_SECRETARIO',
      securityClearance: 'RESTRINGIDO',
      isVerified: true,
      isActive: true,
      department: 'Pruebas'
    }
  })

  console.log('✅ Usuario creado exitosamente:')
  console.log('   Email:', user.email)
  console.log('   Contraseña:', password)
  console.log('   Nombre:', user.name)
  console.log('\n🚀 Ahora puedes iniciar sesión con:')
  console.log('   Email: test@maeuec.es')
  console.log('   Contraseña: test123')
}

main()
  .catch(console.error)
  .finally(() => prisma.$disconnect())

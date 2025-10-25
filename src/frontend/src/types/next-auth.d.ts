/**
 * NextAuth.js Type Definitions
 * Extensiones de tipos para NextAuth
 */

import { DiplomaticRole, SecurityClassification } from "@prisma/client"
import { DefaultSession, DefaultUser } from "next-auth"
import { DefaultJWT } from "next-auth/jwt"

declare module "next-auth" {
  /**
   * Extended User object
   */
  interface User extends DefaultUser {
    diplomaticRole?: DiplomaticRole
    securityClearance?: SecurityClassification
  }

  /**
   * Extended Session object
   */
  interface Session {
    user: {
      id: string
      diplomaticRole?: DiplomaticRole
      securityClearance?: SecurityClassification
    } & DefaultSession["user"]
  }
}

declare module "next-auth/jwt" {
  /**
   * Extended JWT object
   */
  interface JWT extends DefaultJWT {
    id?: string
    diplomaticRole?: DiplomaticRole
    securityClearance?: SecurityClassification
  }
}

import { useContext } from "react"
import { SessionContext } from "./SessionContext"

export function useAuth() {
  const context = useContext(SessionContext)
  if (!context) throw new Error("useAuth must be used inside AuthProvider")
  return context
}
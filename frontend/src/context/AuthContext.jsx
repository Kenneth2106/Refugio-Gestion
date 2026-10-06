import { useEffect, useRef, useState } from "react"
import { useNavigate } from "react-router-dom"
import { api } from "../lib/api"
import { SessionContext } from "./SessionContext"

const INACTIVITY_LIMIT_MS = 3 * 60 * 1000

export function AuthProvider({ children }) {
  const navigate = useNavigate()
  const [user, setUser] = useState(null)
  const [isLoading, setIsLoading] = useState(true)
  const lastActivity = useRef(null)
  const pingInProgress = useRef(false)

  useEffect(() => {
    let mounted = true
    api("/auth/me")
      .then((profile) => { if (mounted) setUser(profile) })
      .catch(() => { if (mounted) setUser(null) })
      .finally(() => { if (mounted) setIsLoading(false) })
    return () => { mounted = false }
  }, [])

  async function signIn(identificacion, password) {
    await api("/auth/login", {
      method: "POST",
      body: JSON.stringify({ identificacion, password }),
    })
    const profile = await api("/auth/me")
    lastActivity.current = Date.now()
    setUser(profile)
    return profile
  }

  async function signOut() {
    try {
      await api("/auth/logout", { method: "POST" })
    } finally {
      setUser(null)
      navigate("/login", { replace: true })
    }
  }

  useEffect(() => {
    if (!user) return undefined

    if (lastActivity.current === null) lastActivity.current = Date.now()
    const recordActivity = () => { lastActivity.current = Date.now() }
    const activityEvents = ["pointerdown", "keydown", "scroll", "touchstart"]
    activityEvents.forEach((eventName) => window.addEventListener(eventName, recordActivity, { passive: true }))

    const activityTimer = window.setInterval(async () => {
      if (Date.now() - lastActivity.current >= INACTIVITY_LIMIT_MS) {
        try { await api("/auth/ping", { method: "POST" }) } catch { /* The backend revokes expired activity sessions. */ }
        setUser(null)
        navigate("/login", { replace: true, state: { reason: "inactivity" } })
        return
      }
      if (!pingInProgress.current && Date.now() - lastActivity.current < 60_000) {
        pingInProgress.current = true
        try {
          await api("/auth/ping", { method: "POST" })
        } catch {
          setUser(null)
          navigate("/login", { replace: true, state: { reason: "expired" } })
        } finally {
          pingInProgress.current = false
        }
      }
    }, 15_000)

    const remaining = Math.max(0, user.expires_at * 1000 - Date.now())
    const maximumTimer = window.setTimeout(() => {
      setUser(null)
      navigate("/login", { replace: true, state: { reason: "expired" } })
    }, Math.min(remaining, 2_147_483_647))

    return () => {
      activityEvents.forEach((eventName) => window.removeEventListener(eventName, recordActivity))
      window.clearInterval(activityTimer)
      window.clearTimeout(maximumTimer)
    }
  }, [user, navigate])

  return (
    <SessionContext.Provider value={{ user, isLoading, signIn, signOut }}>
      {children}
    </SessionContext.Provider>
  )
}

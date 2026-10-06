import { MapPin, UsersRound, Utensils } from "lucide-react"
import { useEffect, useState } from "react"
import { api } from "../lib/api"
import { useAuth } from "../context/useAuth"

export function OverviewPage() {
  const { user } = useAuth()
  const [summary, setSummary] = useState({ users: 0, sites: 0, tables: 0 })
  const [error, setError] = useState("")

  useEffect(() => {
    let active = true
    async function loadSummary() {
      try {
        const [users, sites] = await Promise.all([api("/usuarios/"), api("/sedes/")])
        const tableLists = await Promise.all(sites.map((site) => api(`/sedes/${site.id}/mesas`)))
        if (active) setSummary({ users: users.length, sites: sites.length, tables: tableLists.flat().length })
      } catch (requestError) {
        if (active) setError(requestError.message)
      }
    }
    if (user.is_admin) loadSummary()
    return () => { active = false }
  }, [user.is_admin])

  return (
    <section>
      <p className="page-kicker">Administration</p>
      <h1 className="page-title">Business overview</h1>
      <div className="gold-rule" />
      <p className="page-lead">Manage staff, locations and table setup from one place.</p>
      <div aria-live="polite" className="metric-row">
        <div className="metric"><strong><UsersRound aria-hidden="true" size={18} />{summary.users}</strong><span>Registered users</span></div>
        <div className="metric"><strong><MapPin aria-hidden="true" size={18} />{summary.sites}</strong><span>Locations you can access</span></div>
        <div className="metric"><strong><Utensils aria-hidden="true" size={18} />{summary.tables}</strong><span>Configured tables</span></div>
      </div>
      <p aria-live="polite" className="feedback error">{error}</p>
    </section>
  )
}
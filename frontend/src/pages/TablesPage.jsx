import { startTransition, useEffect, useState } from "react"
import { api } from "../lib/api"

export function TablesPage() {
  const [sites, setSites] = useState([])
  const [selectedSite, setSelectedSite] = useState("")
  const [tables, setTables] = useState([])
  const [number, setNumber] = useState("")
  const [error, setError] = useState("")
  const [notice, setNotice] = useState("")
  const [busy, setBusy] = useState(false)

  async function loadSites() {
    const rows = await api("/sedes/")
    startTransition(() => {
      setSites(rows)
      setSelectedSite((current) => rows.some((site) => String(site.id) === current && site.estado)
        ? current
        : String(rows.find((site) => site.estado)?.id || ""))
    })
  }

  async function loadTables(siteId) {
    if (!siteId) {
      startTransition(() => setTables([]))
      return
    }
    const rows = await api(`/sedes/${siteId}/mesas`)
    startTransition(() => setTables(rows))
  }

  useEffect(() => { loadSites().catch((requestError) => setError(requestError.message)) }, [])
  useEffect(() => { loadTables(selectedSite).catch((requestError) => setError(requestError.message)) }, [selectedSite])

  async function submit(event) {
    event.preventDefault()
    if (!selectedSite) { setError("Create or activate a location first."); return }
    setBusy(true)
    setError("")
    setNotice("")
    try {
      await api(`/sedes/${selectedSite}/mesas`, { method: "POST", body: JSON.stringify({ numero: Number(number) }) })
      setNumber("")
      setNotice("Table created.")
      await loadTables(selectedSite)
    } catch (requestError) { setError(requestError.message) }
    finally { setBusy(false) }
  }

  async function toggleActive(table) {
    try {
      await api(`/sedes/mesas/${table.id}`, { method: "PATCH", body: JSON.stringify({ estado: !table.estado }) })
      setNotice(table.estado ? "Table deactivated." : "Table reactivated.")
      await loadTables(selectedSite)
    } catch (requestError) { setError(requestError.message) }
  }

  const activeSites = sites.filter((site) => site.estado)

  return (
    <section>
      <p className="page-kicker">Location setup</p>
      <h1 className="page-title">Tables</h1>
      <p className="page-lead">Table numbers are unique within each location and can be reactivated without recreating them.</p>
      <form className="section-block" onSubmit={submit}>
        <div className="section-heading"><div><h2>New table</h2><p>Select a location and set its table number.</p></div></div>
        <div className="form-grid">
          <label className="field">Location<select onChange={(event) => setSelectedSite(event.target.value)} required value={selectedSite}>
            <option value="">Select a location</option>
            {activeSites.map((site) => <option key={site.id} value={site.id}>{site.codigo} · {site.nombre}</option>)}
          </select></label>
          <label className="field">Table number<input min="1" onChange={(event) => setNumber(event.target.value)} required step="1" type="number" value={number} /></label>
          <div className="form-actions"><button className="button button-primary" disabled={busy || !activeSites.length} type="submit">{busy ? "Saving..." : "Create table"}</button></div>
        </div>
        <p aria-live="polite" className={`feedback${error ? " error" : ""}`}>{error || notice}</p>
      </form>
      <section className="section-block">
        <div className="section-heading"><div><h2>Tables at selected location</h2><p>{tables.length} table(s)</p></div></div>
        {!selectedSite ? <p className="empty-state">No active location is available.</p> : (
          <div className="data-table-wrap"><table className="data-table"><thead><tr><th>Number</th><th>Status</th><th>Actions</th></tr></thead>
            <tbody>{tables.map((table) => <tr key={table.id}>
              <td>{table.numero}</td><td>{table.estado ? "Active" : "Inactive"}</td>
              <td><button className={`button button-small${table.estado ? " button-danger" : ""}`} onClick={() => toggleActive(table)} type="button">{table.estado ? "Deactivate" : "Reactivate"}</button></td>
            </tr>)}</tbody>
          </table></div>
        )}
      </section>
    </section>
  )
}
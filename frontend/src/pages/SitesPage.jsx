import { startTransition, useEffect, useState } from "react"
import { api } from "../lib/api"

export function SitesPage() {
  const [sites, setSites] = useState([])
  const [draft, setDraft] = useState({ codigo: "", nombre: "", direccion: "" })
  const [error, setError] = useState("")
  const [notice, setNotice] = useState("")
  const [busy, setBusy] = useState(false)

  async function refresh() {
    const rows = await api("/sedes/")
    startTransition(() => setSites(rows))
  }
  useEffect(() => { refresh().catch((requestError) => setError(requestError.message)) }, [])

  async function submit(event) {
    event.preventDefault()
    setBusy(true)
    setError("")
    setNotice("")
    try {
      await api("/sedes/", { method: "POST", body: JSON.stringify(draft) })
      setDraft({ codigo: "", nombre: "", direccion: "" })
      setNotice("Location created.")
      await refresh()
    } catch (requestError) { setError(requestError.message) }
    finally { setBusy(false) }
  }

  async function toggleActive(site) {
    try {
      await api(`/sedes/${site.id}`, { method: "PATCH", body: JSON.stringify({ estado: !site.estado }) })
      setNotice(site.estado ? "Location deactivated." : "Location reactivated.")
      await refresh()
    } catch (requestError) { setError(requestError.message) }
  }

  return (
    <section>
      <p className="page-kicker">Business locations</p>
      <h1 className="page-title">Locations</h1>
      <p className="page-lead">Create and maintain locations. Your administrator account can manage all of them without being assigned to one.</p>
      <form className="section-block" onSubmit={submit}>
        <div className="section-heading"><div><h2>New location</h2><p>Location codes must be unique.</p></div></div>
        <div className="form-grid">
          <label className="field">Location code<input maxLength={20} onChange={(event) => setDraft({ ...draft, codigo: event.target.value })} required value={draft.codigo} /></label>
          <label className="field">Location name<input maxLength={100} onChange={(event) => setDraft({ ...draft, nombre: event.target.value })} required value={draft.nombre} /></label>
          <label className="field field-wide">Address<input autoComplete="street-address" maxLength={200} onChange={(event) => setDraft({ ...draft, direccion: event.target.value })} required value={draft.direccion} /></label>
          <div className="form-actions"><button className="button button-primary" disabled={busy} type="submit">{busy ? "Saving..." : "Create location"}</button></div>
        </div>
        <p aria-live="polite" className={`feedback${error ? " error" : ""}`}>{error || notice}</p>
      </form>
      <section className="section-block">
        <div className="section-heading"><div><h2>Locations</h2><p>{sites.length} location(s)</p></div></div>
        <div className="data-table-wrap"><table className="data-table"><thead><tr><th>Code</th><th>Name</th><th>Address</th><th>Status</th><th>Actions</th></tr></thead>
          <tbody>{sites.map((site) => <tr key={site.id}>
            <td>{site.codigo}</td><td>{site.nombre}</td><td>{site.direccion}</td><td>{site.estado ? "Active" : "Inactive"}</td>
            <td><button className={`button button-small${site.estado ? " button-danger" : ""}`} onClick={() => toggleActive(site)} type="button">{site.estado ? "Deactivate" : "Reactivate"}</button></td>
          </tr>)}</tbody>
        </table></div>
      </section>
    </section>
  )
}
import { startTransition, useEffect, useState } from "react"
import { api } from "../lib/api"
import { useAuth } from "../context/useAuth"

const emptyUser = {
  identificacion: "",
  nombre: "",
  nombre_usuario: "",
  email: "",
  password: "",
  es_admin: false,
  es_mesero: false,
  es_cajero: false,
  sedes_ids: [],
}

export function UsersPage() {
  const { user: currentUser } = useAuth()
  const [users, setUsers] = useState([])
  const [sites, setSites] = useState([])
  const [draft, setDraft] = useState(emptyUser)
  const [editingId, setEditingId] = useState(null)
  const [error, setError] = useState("")
  const [notice, setNotice] = useState("")
  const [busy, setBusy] = useState(false)

  async function refresh() {
    const [userRows, siteRows] = await Promise.all([api("/usuarios/"), api("/sedes/")])
    startTransition(() => {
      setUsers(userRows)
      setSites(siteRows)
    })
  }

  useEffect(() => { refresh().catch((requestError) => setError(requestError.message)) }, [])

  function changeField(event) {
    const { name, value, checked, type } = event.target
    if (name === "es_admin" && checked) {
      setDraft((previous) => ({ ...previous, es_admin: true, sedes_ids: [] }))
      return
    }
    setDraft((previous) => ({ ...previous, [name]: type === "checkbox" ? checked : value }))
  }

  function toggleSite(siteId) {
    setDraft((previous) => ({
      ...previous,
      sedes_ids: previous.sedes_ids.includes(siteId)
        ? previous.sedes_ids.filter((id) => id !== siteId)
        : [...previous.sedes_ids, siteId],
    }))
  }

  async function submit(event) {
    event.preventDefault()
    setError("")
    setNotice("")
    if (!draft.es_admin && draft.sedes_ids.length === 0) {
      setError("Select at least one location for an operational user.")
      return
    }
    if (!draft.es_admin && !draft.es_mesero && !draft.es_cajero) {
      setError("Select at least one role.")
      return
    }

    const payload = { ...draft, sedes_ids: draft.es_admin ? [] : draft.sedes_ids }
    if (editingId && !payload.password) delete payload.password
    if (!editingId) delete payload.estado

    setBusy(true)
    try {
      if (editingId) {
        await api(`/usuarios/${editingId}`, { method: "PATCH", body: JSON.stringify(payload) })
        setNotice("User changes saved.")
      } else {
        await api("/usuarios/", { method: "POST", body: JSON.stringify(payload) })
        setNotice("User created.")
      }
      setDraft(emptyUser)
      setEditingId(null)
      await refresh()
    } catch (requestError) {
      setError(requestError.message)
    } finally {
      setBusy(false)
    }
  }

  function startEdit(record) {
    setEditingId(record.id)
    setDraft({
      identificacion: record.identificacion,
      nombre: record.nombre,
      nombre_usuario: record.nombre_usuario,
      email: record.email,
      password: "",
      es_admin: record.es_admin,
      es_mesero: record.es_mesero,
      es_cajero: record.es_cajero,
      estado: record.estado,
      sedes_ids: record.es_admin ? [] : record.sedes_ids,
    })
    setError("")
    setNotice("")
    window.scrollTo({ top: 0, behavior: "smooth" })
  }

  function cancelEdit() {
    setDraft(emptyUser)
    setEditingId(null)
    setError("")
  }

  async function toggleActive(record) {
    setError("")
    try {
      if (record.estado) await api(`/usuarios/${record.id}/inactivar`, { method: "PATCH" })
      else await api(`/usuarios/${record.id}`, { method: "PATCH", body: JSON.stringify({ estado: true }) })
      setNotice(record.estado ? "User deactivated." : "User reactivated.")
      await refresh()
    } catch (requestError) {
      setError(requestError.message)
    }
  }

  const activeSites = sites.filter((site) => site.estado)

  return (
    <section>
      <p className="page-kicker">Access and permissions</p>
      <h1 className="page-title">Users</h1>
      <p className="page-lead">Create accounts and assign roles and authorized locations.</p>
      <form className="section-block" onSubmit={submit}>
        <div className="section-heading"><div><h2>{editingId ? "Edit user" : "New user"}</h2><p>Administrators manage all locations and cannot be assigned to specific locations.</p></div></div>
        <div className="form-grid">
          <label className="field">Identification number<input maxLength={30} name="identificacion" onChange={changeField} required value={draft.identificacion} /></label>
          <label className="field">Full name<input maxLength={100} name="nombre" onChange={changeField} required value={draft.nombre} /></label>
          <label className="field">Username<input maxLength={50} minLength={3} name="nombre_usuario" onChange={changeField} required value={draft.nombre_usuario} /></label>
          <label className="field">Email address<input autoComplete="email" name="email" onChange={changeField} required type="email" value={draft.email} /></label>
          <label className="field">{editingId ? "New password (optional)" : "Initial password"}<input autoComplete="new-password" maxLength={72} minLength={8} name="password" onChange={changeField} required={!editingId} type="password" value={draft.password} /></label>
          {editingId && <label className="check-field"><input checked={draft.estado} name="estado" onChange={changeField} type="checkbox" />Account active</label>}
          <fieldset className="role-fieldset field-wide">
            <legend>Roles</legend>
            <label className="check-field"><input checked={draft.es_admin} name="es_admin" onChange={changeField} type="checkbox" />Administrator</label>
            <label className="check-field"><input checked={draft.es_mesero} name="es_mesero" onChange={changeField} type="checkbox" />Waiter</label>
            <label className="check-field"><input checked={draft.es_cajero} name="es_cajero" onChange={changeField} type="checkbox" />Cashier</label>
          </fieldset>
          <fieldset className="role-fieldset field-wide">
            <legend>Authorized locations{draft.es_admin ? " (not applicable for administrators)" : " (required)"}</legend>
            {draft.es_admin ? (
              <p className="empty-state">Administrators manage all locations and are not assigned to specific locations.</p>
            ) : (
              <>
                {activeSites.map((site) => (
                  <label className="check-field" key={site.id}>
                    <input checked={draft.sedes_ids.includes(site.id)} onChange={() => toggleSite(site.id)} type="checkbox" />
                    {site.codigo} · {site.nombre}
                  </label>
                ))}
                {activeSites.length === 0 && <span className="empty-state">Create a location before assigning operational users.</span>}
              </>
            )}
          </fieldset>
          <div className="form-actions">
            <button className="button button-primary" disabled={busy} type="submit">{busy ? "Saving..." : editingId ? "Save changes" : "Create user"}</button>
            {editingId && <button className="button" onClick={cancelEdit} type="button">Cancel</button>}
          </div>
        </div>
        <p aria-live="polite" className={`feedback${error ? " error" : ""}`}>{error || notice}</p>
      </form>

      <section className="section-block">
        <div className="section-heading"><div><h2>Staff accounts</h2><p>{users.length} account(s)</p></div></div>
        <div className="data-table-wrap"><table className="data-table"><thead><tr><th>Name</th><th>Username</th><th>Identification</th><th>Roles</th><th>Status</th><th>Actions</th></tr></thead>
          <tbody>{users.map((record) => (
            <tr key={record.id}>
              <td>{record.nombre}</td><td>{record.nombre_usuario}</td><td>{record.identificacion}</td>
              <td>{[record.es_admin && "Administrator", record.es_mesero && "Waiter", record.es_cajero && "Cashier"].filter(Boolean).join(", ")}</td>
              <td>{record.estado ? "Active" : "Inactive"}</td>
              <td><div className="table-actions">
                <button className="button button-small" onClick={() => startEdit(record)} type="button">Edit</button>
                {record.id !== currentUser.id && <button className={`button button-small${record.estado ? " button-danger" : ""}`} onClick={() => toggleActive(record)} type="button">{record.estado ? "Deactivate" : "Reactivate"}</button>}
              </div></td>
            </tr>
          ))}</tbody>
        </table></div>
      </section>
    </section>
  )
}
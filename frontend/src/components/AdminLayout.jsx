import { LogOut } from "lucide-react"
import { Outlet } from "react-router-dom"
import { useAuth } from "../context/useAuth"
import { Sidebar } from "./Sidebar"

export function AdminLayout() {
  const { user, signOut } = useAuth()

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="brand-lockup"><span className="brand-mark" aria-hidden="true">R</span><span>Refugio Management</span></div>
        <div className="account-actions">
          <span className="account-name">{user.nombre}</span>
          <button className="button button-quiet" onClick={signOut} type="button"><LogOut size={16} />Sign out</button>
        </div>
      </header>
      <div className="dashboard-layout">
        <Sidebar />
        <main className="workspace"><div className="workspace-inner"><Outlet /></div></main>
      </div>
    </div>
  )
}
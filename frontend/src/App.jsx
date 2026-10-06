import { BrowserRouter, Navigate, Outlet, Route, Routes } from "react-router-dom"
import { AuthProvider } from "./context/AuthContext"
import { useAuth } from "./context/useAuth"
import { AdminLayout } from "./components/AdminLayout"
import { LoginPage } from "./pages/LoginPage"
import { OverviewPage } from "./pages/OverviewPage"
import { UsersPage } from "./pages/UsersPage"
import { SitesPage } from "./pages/SitesPage"
import { TablesPage } from "./pages/TablesPage"
import "./styles.css"

function ProtectedLayout() {
  const { user, isLoading, signOut } = useAuth()

  if (isLoading) return <div className="page-loading">Loading your workspace...</div>
  if (!user) return <Navigate to="/login" replace />

  if (!user.is_admin) {
    return (
      <div className="employee-shell">
        <header className="topbar">
          <div className="brand-lockup"><span className="brand-mark">R</span><span>Refugio Management</span></div>
          <div className="account-actions"><span className="account-name">{user.nombre}</span><button className="button button-quiet" onClick={signOut} type="button">Sign out</button></div>
        </header>
        <main className="employee-content">
          <p className="page-kicker">Signed in</p>
          <h1>Welcome, {user.nombre}</h1>
          <p>Your account has access to {user.sedes_ids.length} assigned location(s).</p>
        </main>
      </div>
    )
  }

  return <AdminLayout><Outlet /></AdminLayout>
}

function AdminOnly({ children }) {
  const { user } = useAuth()
  return user?.is_admin ? children : <Navigate to="/dashboard" replace />
}

function LoginRoute() {
  const { user, isLoading } = useAuth()
  if (isLoading) return <div className="page-loading">Loading...</div>
  return user ? <Navigate to="/dashboard" replace /> : <LoginPage />
}

function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/login" replace />} />
      <Route path="/login" element={<LoginRoute />} />
      <Route path="/dashboard" element={<ProtectedLayout />}>
        <Route index element={<OverviewPage />} />
        <Route path="users" element={<AdminOnly><UsersPage /></AdminOnly>} />
        <Route path="sites" element={<AdminOnly><SitesPage /></AdminOnly>} />
        <Route path="tables" element={<AdminOnly><TablesPage /></AdminOnly>} />
      </Route>
      <Route path="*" element={<Navigate to="/login" replace />} />
    </Routes>
  )
}

export default function App() {
  return <BrowserRouter><AuthProvider><AppRoutes /></AuthProvider></BrowserRouter>
}

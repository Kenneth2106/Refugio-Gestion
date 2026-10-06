import { LayoutDashboard, MapPin, Table2, UsersRound } from "lucide-react"
import { NavLink } from "react-router-dom"

const items = [
  { to: "/dashboard", label: "Overview", icon: LayoutDashboard, end: true },
  { to: "/dashboard/users", label: "Users", icon: UsersRound },
  { to: "/dashboard/sites", label: "Locations", icon: MapPin },
  { to: "/dashboard/tables", label: "Tables", icon: Table2 },
]

export function Sidebar() {
  return (
    <aside className="sidebar" aria-label="Administration">
      <p className="sidebar-heading">Administration</p>
      <nav className="sidebar-nav">
        {items.map(({ to, label, icon: Icon, end }) => (
          <NavLink className={({ isActive }) => `sidebar-link${isActive ? " active" : ""}`} end={end} key={to} to={to}>
            <Icon aria-hidden="true" size={18} strokeWidth={1.8} />
            <span>{label}</span>
          </NavLink>
        ))}
      </nav>
    </aside>
  )
}
import "./styles.css"

const app = document.querySelector("#app")
const INACTIVITY_MS = 3 * 60 * 1000
const navigation = [
  { path: "/dashboard", label: "Overview", icon: "⌂", access: "any" },
  { path: "/dashboard/users", label: "Users", icon: "♙", access: "admin" },
  { path: "/dashboard/sites", label: "Locations", icon: "⌖", access: "admin" },
  { path: "/dashboard/products", label: "Products", icon: "◇", access: "admin" },
  { path: "/dashboard/inventory", label: "Inventory", icon: "▤", access: "inventory" },
  { path: "/dashboard/tables", label: "Tables", icon: "▦", access: "tables" },
  { path: "/dashboard/orders", label: "Orders", icon: "≡", access: "waiter" },
]

const state = {
  user: null,
  sites: [],
  path: window.location.pathname,
  notice: "",
  noticeKind: "info",
  loading: true,
  heartbeat: null,
  lastActivity: Date.now(),
  heartbeatBusy: false,
  noticeTimer: null,
}

function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>"']/g, (character) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#39;",
  })[character])
}

function errorMessage(detail, status) {
  const messages = {
    "Identificación o contraseña incorrectas": "Identification or password is incorrect.",
    "Usuario inactivado": "This account is inactive.",
    "El usuario no tiene una sede activa asignada": "This account has no active location assigned.",
    "Selecciona una sede para continuar": "Select a location before continuing.",
    "No tienes acceso a esta sede": "You do not have access to this location.",
    "Se requieren privilegios de administrador": "Administrator permission is required.",
    "Se requieren permisos de mesero": "Waiter permission is required.",
    "El pedido ya tiene un pedido abierto": "This table already has an open order.",
    "La mesa ya tiene un pedido abierto": "This table already has an open order.",
    "Inventario insuficiente para uno o más productos": "There is not enough inventory for one or more products.",
    "Solo se pueden modificar pedidos abiertos": "Only open orders can be modified.",
  }
  if (Array.isArray(detail)) return "Check the required fields and try again."
  if (messages[detail]) return messages[detail]
  if (status === 401) return "Your session has expired. Sign in again."
  if (status === 403) return "You do not have permission to perform this action."
  if (status === 404) return "The requested record could not be found."
  if (status === 409) return "This operation conflicts with the current data."
  if (status === 422) return "Check the required fields and try again."
  return detail || "The request could not be completed. Please try again."
}

async function api(path, options = {}) {
  let response
  try {
    response = await fetch(path, {
      credentials: "same-origin",
      ...options,
      headers: {
        ...(options.body ? { "Content-Type": "application/json" } : {}),
        ...options.headers,
      },
    })
  } catch {
    throw new Error("Cannot reach the server. Check that the API is running.")
  }

  let result = {}
  try {
    result = await response.json()
  } catch {
    if (response.ok) return {}
  }
  if (!response.ok) {
    const error = new Error(errorMessage(result.detail, response.status))
    error.status = response.status
    throw error
  }
  return result
}

function hasRole(role) {
  return Boolean(state.user?.is_admin || state.user?.roles?.includes(role))
}

function hasAccess(access) {
  if (access === "any") return true
  if (access === "admin") return Boolean(state.user?.is_admin)
  if (access === "waiter") return hasRole("mesero")
  if (access === "inventory" || access === "tables") {
    return hasRole("mesero") || Boolean(state.user?.is_admin)
  }
  return false
}

function setNotice(message, kind = "info") {
  state.notice = message
  state.noticeKind = kind
  if (state.noticeTimer) window.clearTimeout(state.noticeTimer)
  if (message) {
    state.noticeTimer = window.setTimeout(() => {
      state.notice = ""
      document.querySelector(".toast")?.remove()
    }, 5000)
  }
}

function redirect(path, replace = false) {
  if (replace) window.history.replaceState({}, "", path)
  else window.history.pushState({}, "", path)
  state.path = window.location.pathname
  render()
}

function signOut(message = "") {
  if (state.heartbeat) window.clearInterval(state.heartbeat)
  state.heartbeat = null
  state.user = null
  state.sites = []
  setNotice(message)
  redirect("/login", true)
}

function startHeartbeat() {
  if (state.heartbeat) window.clearInterval(state.heartbeat)
  state.lastActivity = Date.now()
  state.heartbeat = window.setInterval(async () => {
    if (!state.user || state.heartbeatBusy) return
    const now = Date.now()
    if (now >= state.user.expires_at * 1000) {
      signOut("Your session expired. Please sign in again.")
      return
    }
    if (now - state.lastActivity >= INACTIVITY_MS) {
      signOut("Your session ended after 3 minutes of inactivity.")
      return
    }
    if (now - state.lastActivity < 60_000) {
      state.heartbeatBusy = true
      try {
        state.user = await api("/auth/me")
      } catch (error) {
        if (error.status === 401 || error.status === 403) {
          signOut(error.message)
        }
      } finally {
        state.heartbeatBusy = false
      }
    }
  }, 15_000)
}

async function loadSites() {
  state.sites = await api("/sedes/")
}

function siteSelector() {
  if (!state.sites.length) return ""
  const selected = state.user.sede_seleccionada_id
  if (state.sites.length === 1) {
    return `<span class="site-current">${escapeHtml(state.sites[0].nombre)}</span>`
  }
  return `<label class="site-picker"><span>Working location</span>
    <select id="site-picker" aria-label="Select working location">
      <option value="">Select a location</option>
      ${state.sites.filter((site) => site.estado).map((site) => `
        <option value="${site.id}" ${Number(selected) === site.id ? "selected" : ""}>
          ${escapeHtml(site.codigo)} · ${escapeHtml(site.nombre)}
        </option>`).join("")}
    </select>
  </label>`
}

function sidebar() {
  return `<aside class="sidebar" aria-label="Main navigation">
    <p class="sidebar-heading">Workspace</p>
    <nav class="sidebar-nav">
      ${navigation.map((item) => `
        <a class="sidebar-link ${state.path === item.path ? "active" : ""}"
           href="${item.path}" data-nav="${item.path}">
          <span class="nav-icon" aria-hidden="true">${item.icon}</span>
          <span>${item.label}</span>
        </a>`).join("")}
    </nav>
  </aside>`
}

function shell(content) {
  const roles = (state.user.roles || []).map((role) => ({
    admin: "Administrator",
    mesero: "Waiter",
    cajero: "Cashier",
  })[role] || role).join(" · ")
  return `<div class="app-shell">
    <header class="topbar">
      <a class="brand-lockup" href="/dashboard" data-nav="/dashboard">
        <img class="brand-logo-small" src="/brand-logo.svg" alt="El Refugio Bar">
        <span>Refugio Management</span>
      </a>
      <div class="topbar-right">${siteSelector()}
        <div class="account-actions">
          <span class="account-name">${escapeHtml(state.user.nombre)}
            <small>${escapeHtml(roles)}</small>
          </span>
          <button class="button button-quiet" data-action="logout" type="button">Sign out</button>
        </div>
      </div>
    </header>
    <div class="dashboard-layout">
      ${sidebar()}
      <main class="workspace"><div class="workspace-inner">${content}</div></main>
    </div>
    ${state.notice ? `<div class="toast ${state.noticeKind === "error" ? "toast-error" : state.noticeKind === "success" ? "toast-success" : ""}" role="status">${escapeHtml(state.notice)}</div>` : ""}
  </div>`
}

function pageHeading(kicker, title, lead = "") {
  return `<p class="page-kicker">${escapeHtml(kicker)}</p>
    <h1 class="page-title">${escapeHtml(title)}</h1>
    ${lead ? `<p class="page-lead">${escapeHtml(lead)}</p>` : ""}`
}

function deniedPage() {
  const label = navigation.find((item) => item.path === state.path)?.label || "this module"
  return `<section class="access-denied" role="alert">
    <span class="denied-mark" aria-hidden="true">!</span>
    <p class="page-kicker">Access restricted</p>
    <h1 class="page-title">You do not have permission</h1>
    <p class="page-lead">Your account does not have permission to enter ${escapeHtml(label)}. Contact an administrator if you need access.</p>
    <button class="button button-primary" data-nav="/dashboard" type="button">Return to overview</button>
  </section>`
}

function feedback(message = "", error = false) {
  return `<p class="feedback ${error ? "error" : ""}" data-feedback aria-live="polite">${escapeHtml(message)}</p>`
}

function showFeedback(form, message, isError = false) {
  const target = form.querySelector("[data-feedback]")
  if (!target) return
  target.textContent = message
  target.classList.toggle("error", isError)
}

function formatMoney(value) {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: 2,
  }).format(Number(value || 0))
}

function tableMarkup(headers, rows, emptyMessage = "No records found.") {
  return `<div class="data-table-wrap"><table class="data-table">
    <thead><tr>${headers.map((header) => `<th>${escapeHtml(header)}</th>`).join("")}</tr></thead>
    <tbody>${rows || `<tr><td class="empty-state" colspan="${headers.length}">${escapeHtml(emptyMessage)}</td></tr>`}</tbody>
  </table></div>`
}

async function renderOverview() {
  if (state.user.is_admin) {
    const overview = await api("/admin/informacion-general")
    return `${pageHeading("Administration", "Business overview", "Review the current information available to your account.")}
      <div class="gold-rule"></div>
      <div class="metric-row">
        ${metric(overview.usuarios.length, "Registered users", "♙")}
        ${metric(overview.sedes.length, "Locations", "⌖")}
        ${metric(overview.mesas.length, "Configured tables", "▦")}
        ${metric(overview.pedidos_abiertos.length, "Open orders", "≡")}
      </div>
      <section class="section-block">
        <div class="section-heading"><div><h2>Open orders</h2><p>Orders currently in progress across locations.</p></div></div>
        ${tableMarkup(["Order", "Location", "Table", "Status", "Total"], overview.pedidos_abiertos.map((order) => `
          <tr><td>#${order.id}</td><td>${escapeHtml(siteName(order.sede_id))}</td><td>${order.mesa_id}</td>
          <td><span class="status-pill">${escapeHtml(order.estado)}</span></td><td>${formatMoney(order.total)}</td></tr>`).join(""))}
      </section>`
  }
  const assignedSites = state.sites.length
  return `${pageHeading("Workspace", `Welcome, ${state.user.nombre}`, "Your account is ready. Choose a module from the shared navigation.")}
    <div class="gold-rule"></div>
    <div class="metric-row">
      ${metric(assignedSites, "Authorized locations", "⌖")}
      ${metric((state.user.roles || []).length, "Assigned roles", "♙")}
      ${metric(state.user.sede_seleccionada_id ? "Ready" : "Choose", "Working location", "▦")}
    </div>
    ${state.user.sede_seleccionada_id ? "" : `<p class="notice">Select a working location before opening tables, inventory, or orders.</p>`}`
}

function metric(value, label, icon) {
  return `<div class="metric"><strong><span aria-hidden="true">${icon}</span>${escapeHtml(value)}</strong><span>${escapeHtml(label)}</span></div>`
}

function siteName(siteId) {
  const site = state.sites.find((entry) => entry.id === siteId)
  return site ? `${site.codigo} · ${site.nombre}` : `Location ${siteId}`
}

async function renderUsers() {
  const [users, sites] = await Promise.all([api("/usuarios/"), api("/sedes/")])
  const rows = users.map((user) => `<tr>
    <td>${escapeHtml(user.nombre)}</td><td>${escapeHtml(user.nombre_usuario)}</td>
    <td>${escapeHtml(user.identificacion)}</td>
    <td>${escapeHtml(roleLabels(user))}</td>
    <td><span class="status-pill ${user.estado ? "" : "inactive"}">${user.estado ? "Active" : "Inactive"}</span></td>
    <td><div class="table-actions">
      <button class="button button-small" data-action="edit-user" data-user="${user.id}" type="button">Edit</button>
      <button class="button button-small ${user.estado ? "button-danger" : ""}" data-action="toggle-user" data-user="${user.id}" type="button">${user.estado ? "Deactivate" : "Reactivate"}</button>
    </div></td></tr>`).join("")
  const activeSites = sites.filter((site) => site.estado)
  return `${pageHeading("Access and permissions", "Users", "Create accounts and assign roles and authorized locations.")}
    <form class="section-block" data-form="user">
      <div class="section-heading"><div><h2 data-user-form-title>New user</h2><p>New accounts are active when created. Administrators manage every location.</p></div></div>
      <input type="hidden" name="id" value="">
      <div class="form-grid">
        <label class="field">Identification number<input name="identificacion" maxlength="30" required></label>
        <label class="field">Full name<input name="nombre" maxlength="100" required></label>
        <label class="field">Username<input name="nombre_usuario" minlength="3" maxlength="50" required></label>
        <label class="field">Email address (optional)<input name="email" type="email" autocomplete="email"></label>
        <label class="field">Password<input name="password" type="password" minlength="8" maxlength="72" autocomplete="new-password"></label>
        <label class="field" data-status-field hidden>Account status<select name="estado"><option value="true">Active</option><option value="false">Inactive</option></select></label>
        <label class="field">Role<select name="role"><option value="mesero">Waiter</option><option value="cajero">Cashier</option><option value="admin">Administrator</option></select></label>
        <label class="field field-wide" data-site-field>Authorized locations (required for operational users)
          <select name="sedes_ids" multiple size="3">${activeSites.map((site) => `<option value="${site.id}">${escapeHtml(site.codigo)} · ${escapeHtml(site.nombre)}</option>`).join("")}</select>
        </label>
        <div class="form-actions"><button class="button button-primary" type="submit">Create user</button>
          <button class="button" data-action="cancel-user-edit" type="button" hidden>Cancel</button></div>
      </div>${feedback()}</form>
    <section class="section-block"><div class="section-heading"><div><h2>Staff accounts</h2><p>${users.length} account(s)</p></div></div>
      ${tableMarkup(["Name", "Username", "Identification", "Roles", "Status", "Actions"], rows, "No users have been added.")}</section>`
}

function roleLabels(user) {
  return [
    user.es_admin && "Administrator",
    user.es_mesero && "Waiter",
    user.es_cajero && "Cashier",
  ].filter(Boolean).join(", ")
}

async function renderSites() {
  const overview = await api("/admin/informacion-general")
  const sites = overview.sedes
  const rows = sites.map((site) => `<tr>
    <td>${escapeHtml(site.codigo)}</td><td>${escapeHtml(site.nombre)}</td><td>${escapeHtml(site.direccion)}</td>
    <td><span class="status-pill ${site.estado ? "" : "inactive"}">${site.estado ? "Active" : "Inactive"}</span></td>
    <td><button class="button button-small ${site.estado ? "button-danger" : ""}" data-action="toggle-site" data-site="${site.id}" type="button">${site.estado ? "Deactivate" : "Reactivate"}</button></td></tr>`).join("")
  return `${pageHeading("Business locations", "Locations", "Create and maintain locations and their operating status.")}
    <form class="section-block" data-form="site">
      <div class="section-heading"><div><h2>New location</h2><p>Location codes must be unique.</p></div></div>
      <div class="form-grid">
        <label class="field">Location code<input name="codigo" maxlength="20" required></label>
        <label class="field">Location name<input name="nombre" maxlength="100" required></label>
        <label class="field field-wide">Address<input name="direccion" maxlength="200" required></label>
        <div class="form-actions"><button class="button button-primary" type="submit">Create location</button></div>
      </div>${feedback()}</form>
    <section class="section-block"><div class="section-heading"><div><h2>Locations</h2><p>${sites.length} location(s)</p></div></div>
      ${tableMarkup(["Code", "Name", "Address", "Status", "Actions"], rows, "No locations have been added.")}</section>`
}

async function renderProducts() {
  const [products, providers] = await Promise.all([api("/productos"), api("/proveedores")])
  const rows = products.map((product) => {
    const provider = providers.find((entry) => entry.id === product.proveedor_id)
    return `<tr><td>${escapeHtml(product.codigo)}</td><td>${escapeHtml(product.nombre)}</td>
      <td>${formatMoney(product.precio_venta)}</td><td>${formatMoney(product.precio_compra)}</td>
      <td>${escapeHtml(provider?.nombre || "")}</td><td>${product.estado ? "Active" : "Inactive"}</td>
      <td><button class="button button-small" data-action="edit-product" data-product="${product.id}" type="button">Edit</button></td></tr>`
  }).join("")
  const providerOptions = providers.map((provider) => `<option value="${provider.id}">${escapeHtml(provider.nombre)}</option>`).join("")
  return `${pageHeading("Catalog management", "Products", "Manage the shared product catalog and its suppliers.")}
    <form class="section-block" data-form="provider">
      <div class="section-heading"><div><h2>New supplier</h2><p>Supplier names are unique.</p></div></div>
      <div class="form-grid"><label class="field">Supplier name<input name="nombre" maxlength="120" required></label>
        <div class="form-actions"><button class="button" type="submit">Create supplier</button></div></div>${feedback()}</form>
    <form class="section-block" data-form="product">
      <div class="section-heading"><div><h2 data-product-form-title>New product</h2><p>Inventory is recorded separately for each location.</p></div></div>
      <input type="hidden" name="id" value="">
      <div class="form-grid">
        <label class="field">Product code<input name="codigo" maxlength="40" required></label>
        <label class="field">Product name<input name="nombre" maxlength="120" required></label>
        <label class="field">Sale price<input name="precio_venta" inputmode="decimal" type="number" min="0" step="0.01" required></label>
        <label class="field">Purchase price<input name="precio_compra" inputmode="decimal" type="number" min="0" step="0.01" required></label>
        <label class="field">Supplier<select name="proveedor_id" required><option value="">Select a supplier</option>${providerOptions}</select></label>
        <label class="check-field"><input name="estado" type="checkbox" checked>Product active</label>
        <div class="form-actions"><button class="button button-primary" type="submit">Save product</button>
          <button class="button" data-action="cancel-product-edit" type="button" hidden>Cancel</button></div>
      </div>${feedback()}</form>
    <section class="section-block"><div class="section-heading"><div><h2>Catalog</h2><p>${products.length} product(s)</p></div></div>
      ${tableMarkup(["Code", "Product", "Sale price", "Purchase price", "Supplier", "Status", "Actions"], rows, "No products have been added.")}</section>
    <section class="section-block"><div class="section-heading"><div><h2>Suppliers</h2><p>${providers.length} supplier(s)</p></div></div>
      ${tableMarkup(["ID", "Supplier"], providers.map((provider) => `<tr><td>${provider.id}</td><td>${escapeHtml(provider.nombre)}</td></tr>`).join(""), "No suppliers have been added.")}</section>`
}

async function renderInventory() {
  const inventory = state.user.sede_seleccionada_id ? await api("/inventario") : []
  const productOptions = inventory.filter((item) => item.cantidad > 0).map((item) => `<option value="${item.producto_id}">${escapeHtml(item.codigo)} · ${escapeHtml(item.nombre)} (${item.cantidad})</option>`).join("")
  const rows = inventory.map((item) => `<tr><td>${escapeHtml(item.codigo)}</td><td>${escapeHtml(item.nombre)}</td>
    <td>${item.cantidad}</td><td><span class="status-pill ${item.cantidad ? "" : "inactive"}">${item.cantidad ? "Available" : "Out of stock"}</span></td></tr>`).join("")
  return `${pageHeading("Location operations", "Inventory", "Inventory balances belong to the selected location and use whole units.")}
    ${state.user.is_admin ? `<form class="section-block" data-form="inventory">
      <div class="section-heading"><div><h2>Add units</h2><p>Administrators may add stock; manual reductions are not available.</p></div></div>
      <div class="form-grid"><label class="field">Product<select name="producto_id" required><option value="">Select a product</option>${productOptions}</select></label>
        <label class="field">Units<input name="cantidad" type="number" min="1" step="1" required></label>
        <div class="form-actions"><button class="button button-primary" type="submit" ${state.user.sede_seleccionada_id ? "" : "disabled"}>Add inventory</button></div>
      </div>${feedback()}</form>` : ""}
    <section class="section-block"><div class="section-heading"><div><h2>${escapeHtml(state.user.sede_seleccionada_id ? siteName(state.user.sede_seleccionada_id) : "Select a location")}</h2><p>${inventory.length} product(s)</p></div></div>
      ${state.user.sede_seleccionada_id ? tableMarkup(["Code", "Product", "Units", "Availability"], rows, "No inventory has been loaded for this location.") : `<p class="notice">Choose a working location in the top bar to view inventory.</p>`}</section>`
}

async function renderTables() {
  if (!state.user.sede_seleccionada_id) {
    return `${pageHeading("Location operations", "Tables", "Select an authorized location to continue.")}
      <p class="notice">Choose a working location in the top bar to view its tables.</p>`
  }
  const tables = state.user.is_admin
    ? (await api("/admin/informacion-general")).mesas.filter(
      (table) => table.sede_id === state.user.sede_seleccionada_id,
    ).map((table) => ({ ...table, estado: table.activa }))
    : await api(`/sedes/${state.user.sede_seleccionada_id}/mesas`)
  const rows = tables.map((table) => `<tr><td>${table.numero}</td>
    <td><span class="status-pill ${table.estado ? "" : "inactive"}">${table.estado ? "Active" : "Inactive"}</span></td>
    <td><span class="status-pill ${table.estado_operativo === "OCUPADA" ? "occupied" : ""}">${escapeHtml(table.estado_operativo)}</span></td>
    ${state.user.is_admin ? `<td><button class="button button-small ${table.estado ? "button-danger" : ""}" data-action="toggle-table" data-table="${table.id}" data-active="${table.estado}" type="button">${table.estado ? "Deactivate" : "Reactivate"}</button></td>` : ""}</tr>`).join("")
  return `${pageHeading(state.user.is_admin ? "Location setup" : "Location operations", "Tables", "Table status is derived from open orders. Tables are not assigned to individual staff.")}
    ${state.user.is_admin ? `<form class="section-block" data-form="table">
      <div class="section-heading"><div><h2>New table</h2><p>${escapeHtml(siteName(state.user.sede_seleccionada_id))}</p></div></div>
      <div class="form-grid"><label class="field">Table number<input name="numero" type="number" min="1" step="1" required></label>
        <div class="form-actions"><button class="button button-primary" type="submit">Create table</button></div>
      </div>${feedback()}</form>` : ""}
    <section class="section-block"><div class="section-heading"><div><h2>Tables at ${escapeHtml(siteName(state.user.sede_seleccionada_id))}</h2><p>${tables.length} table(s)</p></div></div>
      ${tableMarkup(state.user.is_admin ? ["Number", "Setup status", "Current status", "Actions"] : ["Number", "Setup status", "Current status"], rows, "No tables have been configured.")}</section>`
}

async function renderOrders() {
  if (!state.user.sede_seleccionada_id) {
    return `${pageHeading("Location operations", "Orders", "Select an authorized location to continue.")}
      <p class="notice">Choose a working location in the top bar to view and create orders.</p>`
  }
  const [orders, inventory, tables] = await Promise.all([
    api("/pedidos"),
    api("/inventario"),
    api(`/sedes/${state.user.sede_seleccionada_id}/mesas`),
  ])
  const freeTables = tables.filter((table) => table.estado && table.estado_operativo === "LIBRE")
  const availableProducts = inventory.filter((item) => item.cantidad > 0)
  const orderRows = orders.map((order) => {
    const items = order.productos.map((line) => `<li>${line.cantidad} × ${escapeHtml(line.nombre)} <span>${formatMoney(line.precio_unitario)}</span></li>`).join("")
    return `<article class="order-card">
      <div class="order-heading"><div><p class="page-kicker">Table ${order.mesa_id}</p><h3>Order #${order.id}</h3>
      <p class="order-meta">${new Date(order.creado_en).toLocaleString()} · ${escapeHtml(order.estado)}</p></div>
      <strong>${formatMoney(order.total)}</strong></div>
      <ul class="order-lines">${items || "<li>No products</li>"}</ul>
      ${order.estado === "ABIERTO" ? `<form class="inline-form" data-form="add-order-product" data-order="${order.id}">
        <label class="field">Add product<select name="producto_id" required><option value="">Select a product</option>${availableProducts.map((item) => `<option value="${item.producto_id}">${escapeHtml(item.codigo)} · ${escapeHtml(item.nombre)} (${item.cantidad})</option>`).join("")}</select></label>
        <label class="field quantity-field">Units<input name="cantidad" type="number" min="1" step="1" value="1" required></label>
        <button class="button button-primary" type="submit">Add product</button>${feedback()}</form>` : ""}
    </article>`
  }).join("")
  const productOptions = availableProducts.map((item) => `<option value="${item.producto_id}">${escapeHtml(item.codigo)} · ${escapeHtml(item.nombre)} (${item.cantidad})</option>`).join("")
  const tableOptions = freeTables.map((table) => `<option value="${table.id}">Table ${table.numero}</option>`).join("")
  return `${pageHeading("Waiter operations", "Orders", `Open orders at ${siteName(state.user.sede_seleccionada_id)}.`)}
    <form class="section-block" data-form="new-order">
      <div class="section-heading"><div><h2>New order</h2><p>Only free tables and products with available units can be selected.</p></div></div>
      <div class="form-grid">
        <label class="field">Free table<select name="mesa_id" required><option value="">Select a table</option>${tableOptions}</select></label>
        <div class="order-product-list" data-order-products>
          <div class="order-product-row"><label class="field">Product<select name="producto_id" required><option value="">Select a product</option>${productOptions}</select></label>
            <label class="field quantity-field">Units<input name="cantidad" type="number" min="1" step="1" value="1" required></label></div>
        </div>
        <div class="form-actions"><button class="button" data-action="add-order-line" type="button">Add another product</button>
          <button class="button button-primary" type="submit" ${freeTables.length && availableProducts.length ? "" : "disabled"}>Save open order</button></div>
      </div>${feedback()}</form>
    <section class="section-block"><div class="section-heading"><div><h2>Orders at selected location</h2><p>${orders.length} order(s)</p></div></div>
      ${orders.length ? `<div class="order-list">${orderRows}</div>` : `<p class="empty-state">No orders have been created for this location.</p>`}</section>`
}

async function renderLogin() {
  const reason = state.notice
  const reasonMarkup = reason ? `<p class="notice" role="status">${escapeHtml(reason)}</p>` : ""
  return `<main class="login-shell">
    <section class="login-brand">
      <img class="login-logo" src="/brand-logo.svg" alt="El Refugio Bar">
      <div><p class="page-kicker">Refugio Bar</p><h1>Refugio Management</h1>
        <p>Secure access for the people who keep the business moving.</p></div>
      <small>Protected workspace</small>
    </section>
    <section class="login-panel"><form class="login-form" data-form="login">
      <p class="page-kicker">Staff access</p><h2>Sign in</h2>
      <p class="lead">Use your identification number and password to continue.</p>
      ${reasonMarkup}
      <label class="field">Identification number<input name="identificacion" maxlength="30" autocomplete="username" required></label>
      <label class="field">Password<input name="password" type="password" autocomplete="current-password" required></label>
      <button class="button button-primary" type="submit">Continue <span aria-hidden="true">→</span></button>
      ${feedback()}</form></section></main>`
}

const pageRenderers = {
  "/dashboard": renderOverview,
  "/dashboard/users": renderUsers,
  "/dashboard/sites": renderSites,
  "/dashboard/products": renderProducts,
  "/dashboard/inventory": renderInventory,
  "/dashboard/tables": renderTables,
  "/dashboard/orders": renderOrders,
}

async function render() {
  if (state.loading) {
    app.innerHTML = `<div class="page-loading">Loading your workspace...</div>`
    return
  }
  if (!state.user) {
    app.innerHTML = await renderLogin()
    return
  }

  let renderer = pageRenderers[state.path]
  if (!renderer) {
    state.path = "/dashboard"
    window.history.replaceState({}, "", state.path)
    renderer = renderOverview
  }
  const access = navigation.find((item) => item.path === state.path)?.access || "any"
  let content
  if (!hasAccess(access)) {
    content = deniedPage()
  } else {
    try {
      content = await renderer()
    } catch (error) {
      if (error.status === 401) {
        signOut("Your session expired. Please sign in again.")
        return
      }
      if (error.status === 403) content = deniedPage()
      else content = `<section class="error-panel" role="alert">${pageHeading("Request failed", "Unable to load this module", error.message)}
        <button class="button" data-action="reload-page" type="button">Try again</button></section>`
    }
  }
  app.innerHTML = shell(content)
}

function formDataObject(form) {
  return Object.fromEntries(new FormData(form).entries())
}

function selectedSites(form) {
  return [...form.elements.sedes_ids.selectedOptions].map((option) => Number(option.value))
}

function resetUserForm(form) {
  form.reset()
  form.elements.id.value = ""
  form.elements.password.required = false
  form.elements.password.placeholder = ""
  form.elements.identificacion.disabled = false
  form.querySelector("[data-status-field]").hidden = true
  form.querySelector("[data-site-field]").hidden = false
  form.querySelector("[data-user-form-title]").textContent = "New user"
  form.querySelector('[type="submit"]').textContent = "Create user"
  form.querySelector('[data-action="cancel-user-edit"]').hidden = true
}

function setBusy(form, busy) {
  const button = form.querySelector('[type="submit"]')
  if (button) button.disabled = busy
}

async function onSubmit(event) {
  const form = event.target.closest("form[data-form]")
  if (!form) return
  event.preventDefault()
  const type = form.dataset.form
  setBusy(form, true)
  showFeedback(form, "")
  try {
    const data = formDataObject(form)
    if (type === "login") {
      await api("/auth/login", {
        method: "POST",
        body: JSON.stringify({
          identificacion: data.identificacion.trim(),
          password: data.password,
        }),
      })
      state.user = await api("/auth/me")
      await loadSites()
      startHeartbeat()
      setNotice("")
      redirect("/dashboard", true)
      return
    }
    if (type === "user") {
      const id = data.id
      const isAdmin = data.role === "admin"
      const payload = {
        nombre: data.nombre.trim(),
        nombre_usuario: data.nombre_usuario.trim(),
        es_admin: isAdmin,
        es_mesero: !isAdmin && data.role === "mesero",
        es_cajero: !isAdmin && data.role === "cajero",
        sedes_ids: isAdmin ? [] : selectedSites(form),
      }
      if (!id) {
        payload.identificacion = data.identificacion.trim()
        payload.password = data.password
        payload.email = data.email.trim() || null
      } else {
        payload.estado = data.estado === "true"
        if (data.email.trim()) payload.email = data.email.trim()
        if (data.password) payload.password = data.password
      }
      await api(id ? `/usuarios/${id}` : "/usuarios/", {
        method: id ? "PATCH" : "POST",
        body: JSON.stringify(payload),
      })
      await refreshPage("User changes saved.")
      return
    }
    if (type === "site") {
      await api("/sedes/", { method: "POST", body: JSON.stringify(data) })
      await refreshPage("Location created.")
      return
    }
    if (type === "provider") {
      await api("/proveedores", {
        method: "POST",
        body: JSON.stringify({ nombre: data.nombre.trim() }),
      })
      await refreshPage("Supplier created.")
      return
    }
    if (type === "product") {
      const id = data.id
      const payload = {
        codigo: data.codigo.trim(),
        nombre: data.nombre.trim(),
        precio_venta: data.precio_venta,
        precio_compra: data.precio_compra,
        proveedor_id: Number(data.proveedor_id),
        estado: form.elements.estado.checked,
      }
      await api(id ? `/productos/${id}` : "/productos", {
        method: id ? "PATCH" : "POST",
        body: JSON.stringify(payload),
      })
      await refreshPage("Product saved.")
      return
    }
    if (type === "inventory") {
      await api(`/sedes/${state.user.sede_seleccionada_id}/inventario`, {
        method: "POST",
        body: JSON.stringify({
          producto_id: Number(data.producto_id),
          cantidad: Number(data.cantidad),
        }),
      })
      await refreshPage("Inventory updated.")
      return
    }
    if (type === "table") {
      await api(`/sedes/${state.user.sede_seleccionada_id}/mesas`, {
        method: "POST",
        body: JSON.stringify({ numero: Number(data.numero) }),
      })
      await refreshPage("Table created.")
      return
    }
    if (type === "new-order") {
      const productIds = [...form.querySelectorAll('[name="producto_id"]')]
      const quantities = [...form.querySelectorAll('[name="cantidad"]')]
      const products = productIds.map((element, index) => ({
        producto_id: Number(element.value),
        cantidad: Number(quantities[index].value),
      })).filter((product) => product.producto_id)
      await api("/pedidos", {
        method: "POST",
        body: JSON.stringify({ mesa_id: Number(data.mesa_id), productos: products }),
      })
      await refreshPage("Order saved and inventory deducted.")
      return
    }
    if (type === "add-order-product") {
      await api(`/pedidos/${form.dataset.order}/productos`, {
        method: "POST",
        body: JSON.stringify({
          producto_id: Number(data.producto_id),
          cantidad: Number(data.cantidad),
        }),
      })
      await refreshPage("Product added to the open order.")
    }
  } catch (error) {
    if (error.status === 401) {
      signOut(error.message)
      return
    }
    showFeedback(form, error.message, true)
  } finally {
    if (form.isConnected) setBusy(form, false)
  }
}

async function refreshPage(message) {
  setNotice(message, "success")
  state.user = await api("/auth/me")
  await loadSites()
  await render()
}

async function onAction(actionElement) {
  const action = actionElement.dataset.action
  try {
    if (action === "logout") {
      try {
        await api("/auth/logout", { method: "POST" })
      } finally {
        signOut("")
      }
    } else if (action === "reload-page") {
      setNotice("")
      await render()
    } else if (action === "cancel-user-edit") {
      resetUserForm(actionElement.closest("form"))
    } else if (action === "edit-user") {
      const user = await api(`/usuarios/${actionElement.dataset.user}`)
      const form = document.querySelector('[data-form="user"]')
      form.elements.id.value = user.id
      form.elements.identificacion.value = user.identificacion
      form.elements.identificacion.disabled = true
      form.elements.nombre.value = user.nombre
      form.elements.nombre_usuario.value = user.nombre_usuario
      form.elements.email.value = user.email || ""
      form.elements.password.value = ""
      form.elements.password.required = false
      form.elements.password.placeholder = "Leave blank to keep current password"
      form.elements.estado.value = String(user.estado)
      form.querySelector("[data-status-field]").hidden = false
      form.querySelector("[data-user-form-title]").textContent = "Edit user"
      form.querySelector('[type="submit"]').textContent = "Save changes"
      form.querySelector('[data-action="cancel-user-edit"]').hidden = false
      form.querySelector("[data-site-field]").hidden = Boolean(user.es_admin)
      form.elements.role.value = user.es_admin ? "admin" : user.es_mesero ? "mesero" : "cajero"
      for (const option of form.elements.sedes_ids.options) {
        option.selected = user.sedes_ids.includes(Number(option.value))
      }
      form.scrollIntoView({ behavior: "smooth", block: "start" })
    } else if (action === "toggle-user") {
      const user = await api(`/usuarios/${actionElement.dataset.user}`)
      if (!window.confirm(`${user.estado ? "Deactivate" : "Reactivate"} ${user.nombre}?`)) return
      await api(user.estado ? `/usuarios/${user.id}/inactivar` : `/usuarios/${user.id}`, {
        method: "PATCH",
        ...(user.estado ? {} : { body: JSON.stringify({ estado: true }) }),
      })
      await refreshPage(user.estado ? "User deactivated." : "User reactivated.")
    } else if (action === "toggle-site") {
      const overview = await api("/admin/informacion-general")
      const site = overview.sedes.find(
        (entry) => entry.id === Number(actionElement.dataset.site),
      )
      if (!site) throw new Error("The requested location could not be found.")
      if (!window.confirm(`${site.estado ? "Deactivate" : "Reactivate"} ${site.nombre}?`)) return
      await api(`/sedes/${site.id}`, {
        method: "PATCH",
        body: JSON.stringify({ estado: !site.estado }),
      })
      await refreshPage(site.estado ? "Location deactivated." : "Location reactivated.")
    } else if (action === "toggle-table") {
      const active = actionElement.dataset.active === "true"
      if (!window.confirm(`${active ? "Deactivate" : "Reactivate"} this table?`)) return
      await api(`/sedes/mesas/${actionElement.dataset.table}`, {
        method: "PATCH",
        body: JSON.stringify({ estado: !active }),
      })
      await refreshPage(active ? "Table deactivated." : "Table reactivated.")
    } else if (action === "edit-product") {
      const product = await api(`/productos/${actionElement.dataset.product}`)
      const form = document.querySelector('[data-form="product"]')
      for (const [field, value] of Object.entries(product)) {
        if (form.elements[field]) form.elements[field].value = value
      }
      form.elements.id.value = product.id
      form.elements.estado.checked = product.estado
      form.querySelector("[data-product-form-title]").textContent = "Edit product"
      form.querySelector('[type="submit"]').textContent = "Save changes"
      form.querySelector('[data-action="cancel-product-edit"]').hidden = false
      form.scrollIntoView({ behavior: "smooth", block: "start" })
    } else if (action === "cancel-product-edit") {
      const form = document.querySelector('[data-form="product"]')
      form.reset()
      form.elements.id.value = ""
      form.elements.estado.checked = true
      form.querySelector("[data-product-form-title]").textContent = "New product"
      form.querySelector('[type="submit"]').textContent = "Save product"
      form.querySelector('[data-action="cancel-product-edit"]').hidden = true
    } else if (action === "add-order-line") {
      const list = document.querySelector("[data-order-products]")
      const firstRow = list.querySelector(".order-product-row")
      const copy = firstRow.cloneNode(true)
      copy.querySelector("select").value = ""
      copy.querySelector("input").value = "1"
      list.append(copy)
    }
  } catch (error) {
    if (error.status === 401) signOut(error.message)
    else setNotice(error.message, "error")
  }
}

document.addEventListener("submit", onSubmit)
document.addEventListener("click", (event) => {
  const nav = event.target.closest("[data-nav]")
  if (nav) {
    event.preventDefault()
    setNotice("")
    redirect(nav.dataset.nav)
    return
  }
  const action = event.target.closest("[data-action]")
  if (action) void onAction(action)
})
document.addEventListener("change", async (event) => {
  if (event.target.id !== "site-picker") return
  if (!event.target.value) return
  try {
    const result = await api("/auth/sede", {
      method: "POST",
      body: JSON.stringify({ sede_id: Number(event.target.value) }),
    })
    state.user.sede_seleccionada_id = result.sede_seleccionada_id
    setNotice("Working location changed.", "success")
    await render()
  } catch (error) {
    event.target.value = state.user.sede_seleccionada_id || ""
    setNotice(error.message, "error")
    await render()
  }
})
for (const eventName of ["pointerdown", "keydown", "scroll", "touchstart", "input"]) {
  window.addEventListener(eventName, () => {
    if (state.user) state.lastActivity = Date.now()
  }, { passive: true })
}
window.addEventListener("popstate", () => {
  state.path = window.location.pathname
  setNotice("")
  void render()
})

async function bootstrap() {
  if (window.location.pathname === "/") {
    window.history.replaceState({}, "", "/login")
    state.path = "/login"
  }
  try {
    state.user = await api("/auth/me")
    await loadSites()
    startHeartbeat()
    if (state.path === "/login") {
      window.history.replaceState({}, "", "/dashboard")
      state.path = "/dashboard"
    }
  } catch (error) {
    state.user = null
    if (error.status !== 401) setNotice(error.message, "error")
    if (state.path !== "/login") {
      window.history.replaceState({}, "", "/login")
      state.path = "/login"
    }
  } finally {
    state.loading = false
    await render()
  }
}

void bootstrap()

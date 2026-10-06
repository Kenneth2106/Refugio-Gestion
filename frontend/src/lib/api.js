const knownMessages = new Map([
  ["Identificación o contraseña incorrectas", "Identification or password is incorrect."],
  ["Usuario inactivado", "This account is inactive."],
  ["El usuario no tiene una sede activa asignada", "This account has no active location assigned."],
  ["Los usuarios operativos deben tener al menos una sede asignada", "Assign at least one active location to this operational user."],
  ["El usuario debe tener al menos un rol asignado", "Select at least one role."],
  ["El correo, nombre de usuario o identificación ya están registrados", "That email, username, or identification is already in use."],
  ["El número de mesa ya existe en esta sede", "That table number already exists at this location."],
  ["El código de sede ya existe", "That location code is already in use."],
  ["El administrador no debe tener sedes asignadas ya que gestiona todas las sedes", "Administrators manage all locations and cannot be assigned to specific locations."],
])

function translateDetail(detail, status) {
  if (knownMessages.has(detail)) return knownMessages.get(detail)
  if (Array.isArray(detail)) return "Check the highlighted fields and try again."
  if (status === 401) return "Your session has expired. Sign in again."
  if (status === 403) return "You do not have permission to perform this action."
  if (status === 404) return "The requested record could not be found."
  if (status === 422) return "Check the required fields and try again."
  return "The request could not be completed. Please try again."
}

export async function api(path, options = {}) {
  const response = await fetch(path, {
    credentials: "same-origin",
    ...options,
    headers: {
      ...(options.body ? { "Content-Type": "application/json" } : {}),
      ...options.headers,
    },
  })

  let result = {}
  try {
    result = await response.json()
  } catch {
    result = {}
  }

  if (!response.ok) {
    const error = new Error(translateDetail(result.detail, response.status))
    error.status = response.status
    throw error
  }
  return result
}
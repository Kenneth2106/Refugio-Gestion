import { ArrowRight, ShieldCheck } from "lucide-react"
import { useState } from "react"
import { useLocation, useNavigate } from "react-router-dom"
import { useAuth } from "../context/useAuth"

export function LoginPage() {
  const { signIn } = useAuth()
  const location = useLocation()
  const navigate = useNavigate()
  const [identificacion, setIdentificacion] = useState("")
  const [password, setPassword] = useState("")
  const [error, setError] = useState("")
  const [isSubmitting, setIsSubmitting] = useState(false)

  async function handleSubmit(event) {
    event.preventDefault()
    setError("")
    setIsSubmitting(true)
    try {
      await signIn(identificacion.trim(), password)
      navigate(location.state?.from?.pathname || "/dashboard", { replace: true })
    } catch (requestError) {
      setError(requestError.message)
    } finally {
      setIsSubmitting(false)
    }
  }

  const reason = location.state?.reason

  return (
    <main className="login-shell">
      <section className="login-brand">
        <div className="brand-mark" aria-hidden="true">R</div>
        <div>
          <p className="page-kicker">Refugio Bar</p>
          <h1>Refugio Management</h1>
          <p>Secure access for the people who keep the business moving.</p>
        </div>
        <small><ShieldCheck aria-hidden="true" size={15} /> Protected workspace</small>
      </section>
      <section className="login-panel">
        <form className="login-form" onSubmit={handleSubmit}>
          <p className="page-kicker">Staff access</p>
          <h2>Sign in</h2>
          <p className="lead">Use your identification number and password to continue.</p>
          {reason && <p className="notice">{reason === "inactivity" ? "Your session ended after inactivity." : "Your session expired. Please sign in again."}</p>}
          <label className="field" htmlFor="identificacion">Identification number
            <input autoComplete="username" id="identificacion" maxLength={30} onChange={(event) => setIdentificacion(event.target.value)} required value={identificacion} />
          </label>
          <label className="field" htmlFor="password">Password
            <input autoComplete="current-password" id="password" onChange={(event) => setPassword(event.target.value)} required type="password" value={password} />
          </label>
          <button className="button button-primary" disabled={isSubmitting} type="submit">
            {isSubmitting ? "Signing in..." : "Continue"}<ArrowRight aria-hidden="true" size={17} />
          </button>
          <p aria-live="polite" className="login-error" role="alert">{error}</p>
        </form>
      </section>
    </main>
  )
}
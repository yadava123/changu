import { useState } from 'react'
import { ArrowLeft, ArrowUpRight, LockKeyhole, Mail } from 'lucide-react'
import { Link, Navigate, useLocation, useNavigate } from 'react-router-dom'

import { useAuth } from '../context/AuthContext'

function apiError(error) {
  return error.response?.data?.detail || 'Unable to login right now. Please try again.'
}

export default function Login() {
  const { login, user, isAuthenticated } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [form, setForm] = useState({ email: '', password: '' })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  if (isAuthenticated) return <Navigate to={user?.role === 'VENDOR' ? '/vendor/dashboard' : user?.role === 'ADMIN' ? '/admin/dashboard' : '/home'} replace />

  function update(event) {
    setForm({ ...form, [event.target.name]: event.target.value })
  }

  async function submit(event) {
    event.preventDefault()
    setError('')
    setLoading(true)
    try {
      const result = await login(form)
      const destination = result.user.role === 'VENDOR' ? '/vendor/dashboard' : result.user.role === 'ADMIN' ? '/admin/dashboard' : location.state?.from?.pathname || '/home'
      navigate(destination, { replace: true })
    } catch (requestError) {
      setError(apiError(requestError))
    } finally {
      setLoading(false)
    }
  }

  return <AuthLayout eyebrow="Welcome back" title="Your neighbourhood, waiting.">
    <form className="auth-form" onSubmit={submit}>
      {error && <div className="form-error" role="alert">{error}</div>}
      <label>Email<input name="email" type="email" autoComplete="email" value={form.email} onChange={update} placeholder="you@example.com" required /></label>
      <label>Password<input name="password" type="password" autoComplete="current-password" value={form.password} onChange={update} placeholder="Your password" required /></label>
      <button className="auth-submit" disabled={loading}>{loading ? 'Logging in...' : 'Login to ChanGu'} <ArrowUpRight size={17} /></button>
    </form>
    <p className="auth-switch">Don't have an account? <Link to="/register">Create account</Link></p>
  </AuthLayout>
}

export function AuthLayout({ eyebrow, title, children }) {
  return <div className="auth-page"><Link to="/" className="auth-back"><ArrowLeft size={16} /> Back to ChanGu</Link><div className="auth-panel"><div className="auth-brand"><span className="brand-mark">C</span><span>ChanGu</span></div><span className="section-kicker">{eyebrow}</span><h1>{title}</h1>{children}</div><div className="auth-aside"><span className="aside-mark"><Mail size={23} /></span><p>Local life, made simpler.</p><small>One account for everything your neighbourhood can offer.</small></div></div>
}

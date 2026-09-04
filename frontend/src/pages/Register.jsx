import { useState } from 'react'
import { ArrowUpRight, CheckCircle2 } from 'lucide-react'
import { Link, useNavigate } from 'react-router-dom'

import { useAuth } from '../context/AuthContext'
import { AuthLayout } from './Login'

function apiError(error) {
  const detail = error.response?.data?.detail
  if (Array.isArray(detail)) return detail[0]?.msg || 'Please check your details.'
  return detail || 'Unable to create your account right now. Please try again.'
}

export default function Register() {
  const { register } = useAuth()
  const navigate = useNavigate()
  const [form, setForm] = useState({ full_name: '', email: '', phone: '', password: '', confirmPassword: '' })
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [loading, setLoading] = useState(false)

  function update(event) {
    setForm({ ...form, [event.target.name]: event.target.value })
  }

  async function submit(event) {
    event.preventDefault()
    setError('')
    setSuccess('')
    if (form.password !== form.confirmPassword) {
      setError('Passwords do not match')
      return
    }
    setLoading(true)
    try {
      await register({ full_name: form.full_name, email: form.email, phone: form.phone, password: form.password })
      setSuccess('Registration successful. You can now login.')
      setTimeout(() => navigate('/login'), 800)
    } catch (requestError) {
      setError(apiError(requestError))
    } finally {
      setLoading(false)
    }
  }

  return <AuthLayout eyebrow="Create your account" title="Start closer to home.">
    <form className="auth-form register-form" onSubmit={submit}>
      {error && <div className="form-error" role="alert">{error}</div>}
      {success && <div className="form-success" role="status"><CheckCircle2 size={16} />{success}</div>}
      <label>Full name<input name="full_name" value={form.full_name} onChange={update} placeholder="Your full name" minLength="2" required /></label>
      <label>Email<input name="email" type="email" autoComplete="email" value={form.email} onChange={update} placeholder="you@example.com" required /></label>
      <label>Phone<input name="phone" inputMode="numeric" value={form.phone} onChange={update} placeholder="9876543210" pattern="[0-9]{10,15}" required /></label>
      <div className="auth-fields-row"><label>Password<input name="password" type="password" autoComplete="new-password" value={form.password} onChange={update} minLength="8" placeholder="8+ characters" required /></label><label>Confirm password<input name="confirmPassword" type="password" autoComplete="new-password" value={form.confirmPassword} onChange={update} minLength="8" placeholder="Repeat password" required /></label></div>
      <button className="auth-submit" disabled={loading}>{loading ? 'Creating account...' : 'Create account'} <ArrowUpRight size={17} /></button>
    </form>
    <p className="auth-switch">Already have an account? <Link to="/login">Login</Link></p>
  </AuthLayout>
}

import { useState } from 'react'
import { ArrowUpRight, CheckCircle2, HeartPulse, Store, Truck, UserRound, ShieldCheck } from 'lucide-react'
import { Link, Navigate, useNavigate, useParams } from 'react-router-dom'

import { useAuth } from '../context/AuthContext'
import { AuthLayout } from './Login'

const roles = {
  customer: { label: 'Customer', role: 'CUSTOMER', description: 'Order food, shop local, and book everyday services.', destination: '/home', fields: [] },
  vendor: { label: 'Vendor', role: 'VENDOR', description: 'Manage your business, catalogue, and orders.', destination: '/vendor/dashboard', fields: ['business_name', 'business_type', 'description', 'address', 'area', 'city', 'state', 'pincode'] },
  driver: { label: 'Driver', role: 'DRIVER', description: 'Deliver parcels and provide rides across your neighbourhood.', destination: '/driver/dashboard', fields: ['vehicle_type', 'vehicle_number', 'license_number', 'address', 'area', 'city', 'state', 'pincode'] },
  provider: { label: 'Emergency Provider', role: 'EMERGENCY_PROVIDER', description: 'Respond to Siren service requests when people need help.', destination: '/provider', fields: ['provider_type', 'business_name', 'contact_name', 'address', 'area', 'city', 'state', 'pincode'] },
  admin: { label: 'Admin', role: 'ADMIN', description: 'Manage ChanGu operations and community safety.', destination: '/admin/dashboard', fields: [] },
}

const labels = { business_name: 'Business name', business_type: 'Business category', description: 'Business description', address: 'Business address', area: 'Area', city: 'City', state: 'State', pincode: 'PIN code', vehicle_type: 'Vehicle type', vehicle_number: 'Vehicle number', license_number: 'License number', provider_type: 'Service category', contact_name: 'Contact person' }
const options = { business_type: ['RESTAURANT', 'HOME_CHEF', 'GROCERY', 'BAKERY', 'ARTISAN', 'MSME', 'LOCAL_SELLER', 'OTHER'], vehicle_type: ['BIKE', 'SCOOTER', 'AUTO', 'CAR', 'OTHER'], provider_type: ['MECHANIC', 'TOWING', 'FUEL', 'AMBULANCE', 'DOCTOR', 'PHARMACY', 'BLOOD_NETWORK', 'OTHER'] }
const initial = { full_name: '', email: '', phone: '', password: '', confirmPassword: '', business_name: '', business_type: 'RESTAURANT', description: '', address: '', area: '', city: '', state: '', pincode: '', vehicle_type: 'BIKE', vehicle_number: '', license_number: '', provider_type: 'MECHANIC', contact_name: '' }

function apiError(error) {
  const detail = error.response?.data?.detail
  if (Array.isArray(detail)) return detail[0]?.msg || 'Please check your details.'
  return detail || 'Unable to complete this request right now.'
}

function destination(role) { return roles[role].destination }

export function RoleChooser() {
  return <div className="role-chooser"><span className="section-kicker">Welcome to ChanGu</span><h1>Choose how you want to continue.</h1><div className="role-grid">{Object.entries(roles).map(([key, config]) => <Link className="role-card" to={`/${key}/login`} key={key}><span className="role-icon">{key === 'customer' ? <UserRound size={21} /> : key === 'vendor' ? <Store size={21} /> : key === 'driver' ? <Truck size={21} /> : key === 'provider' ? <HeartPulse size={21} /> : <ShieldCheck size={21} />}</span><strong>{config.label}</strong><small>{config.description}</small><ArrowUpRight size={16} /></Link>)}</div></div>
}

export function RoleLogin() {
  const { role = 'customer' } = useParams()
  const config = roles[role] || roles.customer
  const { login, user, isAuthenticated } = useAuth()
  const navigate = useNavigate()
  const [form, setForm] = useState({ email: '', password: '' })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  if (isAuthenticated) return <Navigate to={destination(role)} replace />
  function update(event) { setForm({ ...form, [event.target.name]: event.target.value }) }
  async function submit(event) { event.preventDefault(); setError(''); setLoading(true); try { const result = await login(form, role); navigate(destination(role), { replace: true }); return result } catch (requestError) { setError(apiError(requestError)) } finally { setLoading(false) } }
  return <AuthLayout eyebrow={`${config.label} access`} title={`Welcome back, ${config.label.toLowerCase()}.`}><form className="auth-form" onSubmit={submit}>{error && <div className="form-error" role="alert">{error}</div>}<label>{role === 'customer' || role === 'driver' || role === 'provider' ? 'Email or phone' : `${config.label} email`}<input name="email" type={role === 'customer' || role === 'driver' || role === 'provider' ? 'text' : 'email'} autoComplete="username" value={form.email} onChange={update} placeholder="you@example.com" required /></label><label>Password<input name="password" type="password" autoComplete="current-password" value={form.password} onChange={update} placeholder="Your password" required /></label><div className="auth-actions"><Link to="#">Forgot password?</Link></div><button className="auth-submit" disabled={loading}>{loading ? 'Checking account...' : `Login as ${config.label}`} <ArrowUpRight size={17} /></button></form>{role === 'admin' ? <p className="auth-switch">Admin accounts are created by a super admin.</p> : <p className="auth-switch">Don't have an account? <Link to={`/${role}/register`}>Register as {config.label}</Link></p>}</AuthLayout>
}

export function RoleRegister() {
  const { role = 'customer' } = useParams()
  const config = roles[role] || roles.customer
  const { register } = useAuth()
  const navigate = useNavigate()
  const [form, setForm] = useState(initial)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [loading, setLoading] = useState(false)
  if (role === 'admin') return <Navigate to="/admin/login" replace />
  function update(event) { setForm({ ...form, [event.target.name]: event.target.value }) }
  async function submit(event) { event.preventDefault(); setError(''); if (form.password !== form.confirmPassword) { setError('Passwords do not match'); return } setLoading(true); try { const details = { full_name: form.full_name, email: form.email, phone: form.phone, password: form.password }; config.fields.forEach(field => { details[field] = form[field] }); const result = await register(details, role); setSuccess(result.message); setTimeout(() => navigate(`/${role}/login`), 900) } catch (requestError) { setError(apiError(requestError)) } finally { setLoading(false) } }
  return <AuthLayout eyebrow={`Join as a ${config.label}`} title={`Build your place in ChanGu.`}><form className="auth-form register-form" onSubmit={submit}>{error && <div className="form-error" role="alert">{error}</div>}{success && <div className="form-success" role="status"><CheckCircle2 size={16} />{success}</div>}<label>Full name<input name="full_name" value={form.full_name} onChange={update} required /></label><label>Email<input name="email" type="email" value={form.email} onChange={update} required /></label><label>Phone<input name="phone" inputMode="numeric" pattern="[0-9]{10,15}" value={form.phone} onChange={update} required /></label>{config.fields.map(field => <label key={field}>{labels[field]}{options[field] ? <select name={field} value={form[field]} onChange={update}>{options[field].map(option => <option key={option}>{option}</option>)}</select> : field === 'description' ? <textarea name={field} value={form[field]} onChange={update} required /> : <input name={field} value={form[field]} onChange={update} required />}</label>)}<div className="auth-fields-row"><label>Password<input name="password" type="password" minLength="8" value={form.password} onChange={update} required /></label><label>Confirm password<input name="confirmPassword" type="password" minLength="8" value={form.confirmPassword} onChange={update} required /></label></div><button className="auth-submit" disabled={loading}>{loading ? 'Creating account...' : `Register as ${config.label}`} <ArrowUpRight size={17} /></button></form><p className="auth-switch">Already have an account? <Link to={`/${role}/login`}>Login as {config.label}</Link></p></AuthLayout>
}
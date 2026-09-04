import { useState } from 'react'
import { CalendarDays, Mail, Phone, ShieldCheck, UserRound } from 'lucide-react'
import { useAuth } from '../context/AuthContext'
import api from '../services/api'

export default function Profile() {
  const { user } = useAuth()
  const [profile, setProfile] = useState({ full_name: user.full_name, phone: user.phone })
  const [password, setPassword] = useState({ current_password: '', new_password: '' })
  const [notice, setNotice] = useState('')
  const [error, setError] = useState('')
  async function saveProfile(event) { event.preventDefault(); setError(''); setNotice(''); try { await api.patch('/api/auth/me', profile); setNotice('Profile saved.') } catch (requestError) { setError(requestError.response?.data?.detail || 'Unable to save profile.') } }
  async function changePassword(event) { event.preventDefault(); setError(''); setNotice(''); try { await api.post('/api/auth/change-password', password); setPassword({ current_password: '', new_password: '' }); setNotice('Password changed.') } catch (requestError) { setError(requestError.response?.data?.detail || 'Unable to change password.') } }
  return <div className="profile-page"><div className="page-intro"><span className="section-kicker">Your account</span><h1>Profile</h1><p>Manage your ChanGu account details.</p></div><div className="profile-card"><div className="profile-avatar"><UserRound size={28} /></div><h2>{user.full_name}</h2><span className="role-badge">{user.role}</span><div className="profile-details"><Detail icon={Mail} label="Email" value={user.email} /><Detail icon={Phone} label="Phone" value={user.phone} /><Detail icon={ShieldCheck} label="Account status" value={user.is_active ? 'Active' : 'Inactive'} /><Detail icon={CalendarDays} label="Member since" value={user.created_at ? new Date(user.created_at).toLocaleDateString() : 'ChanGu member'} /></div></div><section className="form-page profile-form"><h2>Edit profile</h2>{error && <p className="form-error" role="alert">{error}</p>}{notice && <p className="form-success" role="status">{notice}</p>}<form className="vendor-form" onSubmit={saveProfile}><label>Name<input value={profile.full_name} onChange={(event) => setProfile({ ...profile, full_name: event.target.value })} minLength="2" required /></label><label>Phone<input value={profile.phone} onChange={(event) => setProfile({ ...profile, phone: event.target.value })} pattern="[0-9]{10,15}" required /></label><button className="auth-submit">Save profile</button></form><h2>Change password</h2><form className="vendor-form" onSubmit={changePassword}><label>Current password<input type="password" value={password.current_password} onChange={(event) => setPassword({ ...password, current_password: event.target.value })} required /></label><label>New password<input type="password" value={password.new_password} onChange={(event) => setPassword({ ...password, new_password: event.target.value })} minLength="8" required /></label><button className="auth-submit">Change password</button></form></section></div>
}

function Detail({ icon: Icon, label, value }) { return <div className="profile-detail"><Icon size={18} /><span><small>{label}</small><strong>{value}</strong></span></div> }

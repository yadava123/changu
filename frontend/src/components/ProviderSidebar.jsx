import { ClipboardList, LogOut, ShieldCheck } from 'lucide-react'
import { NavLink } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function ProviderSidebar() {
  const { logout } = useAuth()
  return <aside className="vendor-sidebar driver-sidebar"><div className="vendor-brand"><span className="brand-mark">C</span><span>ChanGu Provider</span></div><nav><NavLink to="/provider" end className={({ isActive }) => isActive ? 'active' : ''}><ShieldCheck size={17} />Dashboard</NavLink><NavLink to="/provider/requests" className={({ isActive }) => isActive ? 'active' : ''}><ClipboardList size={17} />Requests</NavLink></nav><button type="button" onClick={logout}><LogOut size={17} />Logout</button></aside>
}

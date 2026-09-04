import { BarChart3, Box, ClipboardList, LogOut, Settings, Store, UserRound } from 'lucide-react'
import { NavLink } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

const links = [['/vendor/dashboard','Dashboard',BarChart3],['/vendor/store','Store',Store],['/vendor/products','Products',Box],['/vendor/orders','Orders',ClipboardList],['/vendor/inventory','Inventory',Box],['/vendor/profile','Profile',UserRound],['/vendor/settings','Settings',Settings]]
export default function VendorSidebar() { const { logout } = useAuth(); return <aside className="vendor-sidebar"><div className="vendor-brand"><span className="brand-mark">C</span><span>ChanGu Partner</span></div><nav>{links.map(([to,label,Icon]) => <NavLink key={to} to={to} className={({isActive}) => isActive ? 'active' : ''}><Icon size={17}/>{label}</NavLink>)}</nav><button type="button" onClick={logout}><LogOut size={17}/>Logout</button></aside> }

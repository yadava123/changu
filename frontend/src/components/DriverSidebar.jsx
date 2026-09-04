import { BarChart3, Box, ClipboardList, History, LogOut, Settings, UserRound } from 'lucide-react'
import { NavLink } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
const links=[['/driver/dashboard','Dashboard',BarChart3],['/driver/deliveries','Deliveries',ClipboardList],['/driver/parcels','Parcels',Box],['/driver/transport','Parcel & Rides',Box],['/driver/deliveries/history','History',History],['/driver/profile','Profile',UserRound],['/driver/settings','Settings',Settings]]
export default function DriverSidebar(){const {logout}=useAuth();return <aside className="vendor-sidebar driver-sidebar"><div className="vendor-brand"><span className="brand-mark">C</span><span>ChanGu Driver</span></div><nav>{links.map(([to,label,Icon])=><NavLink to={to} key={to} className={({isActive})=>isActive?'active':''}><Icon size={17}/>{label}</NavLink>)}</nav><button type="button" onClick={logout}><LogOut size={17}/>Logout</button></aside>}

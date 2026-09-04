import { AlertTriangle, Compass, Home, ListOrdered, ShoppingCart, UserRound } from 'lucide-react'
import { useCart } from '../context/CartContext'
import { NavLink } from 'react-router-dom'

const links = [
  { to: '/home', label: 'Home', icon: Home },
  { to: '/explore', label: 'Explore', icon: Compass },
  { to: '/orders', label: 'Orders', icon: ListOrdered },
  { to: '/profile', label: 'Profile', icon: UserRound },
]

export default function CustomerNav() {
  const { itemCount } = useCart()
  return <nav className="customer-nav" aria-label="Customer navigation">{links.map(({ to, label, icon: Icon }) => <NavLink key={to} to={to} className={({ isActive }) => isActive ? 'active' : ''}><Icon size={18} /><span>{label}</span></NavLink>)}<NavLink to="/siren"><AlertTriangle size={18} /><span>Siren</span></NavLink><NavLink to="/cart"><ShoppingCart size={18} /><span>Cart {itemCount ? `(${itemCount})` : ''}</span></NavLink></nav>
}

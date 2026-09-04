import { useEffect, useState } from 'react'
import { ArrowUpRight, Bell, Box, Car, HeartPulse, ShoppingBag } from 'lucide-react'
import { Link } from 'react-router-dom'

import api from '../services/api'
import EmptyState from '../components/EmptyState'
import LoadingSpinner from '../components/LoadingSpinner'
import { useAuth } from '../context/AuthContext'

const activeOrderStatuses = ['PENDING', 'CONFIRMED', 'PREPARING', 'READY_FOR_PICKUP', 'OUT_FOR_DELIVERY']
const activeTransportStatuses = ['PENDING', 'REQUESTED', 'DRIVER_ASSIGNED', 'DRIVER_ARRIVING', 'DRIVER_ARRIVED', 'RIDE_STARTED', 'ACCEPTED', 'PICKED_UP', 'IN_TRANSIT', 'OUT_FOR_DELIVERY']

export default function CustomerDashboard() {
  const { user } = useAuth()
  const [data, setData] = useState(null)
  const [error, setError] = useState('')
  useEffect(() => {
    Promise.all([api.get('/api/orders'), api.get('/api/parcels'), api.get('/api/rides'), api.get('/api/emergency/requests'), api.get('/api/notifications/unread-count')])
      .then(([orders, parcels, rides, siren, notifications]) => setData({ orders: orders.data, parcels: parcels.data, rides: rides.data, siren: siren.data, unread: notifications.data.count }))
      .catch((requestError) => setError(requestError.response?.data?.detail || 'Unable to load your dashboard.'))
  }, [])
  if (error) return <div className="state-panel error-state"><strong>{error}</strong><button type="button" onClick={() => window.location.reload()}>Retry</button></div>
  if (!data) return <LoadingSpinner label="Loading your dashboard..." />
  const activeOrders = data.orders.filter(item => activeOrderStatuses.includes(item.status))
  const activeParcels = data.parcels.filter(item => activeTransportStatuses.includes(item.status))
  const activeRides = data.rides.filter(item => activeTransportStatuses.includes(item.status))
  const activeSiren = data.siren.filter(item => !['RESOLVED', 'CANCELLED'].includes(item.status))
  const cards = [[ShoppingBag, 'Active orders', activeOrders.length, '/orders'], [Box, 'Active parcels', activeParcels.length, '/parcel'], [Car, 'Active rides', activeRides.length, '/rides'], [HeartPulse, 'Siren requests', activeSiren.length, '/emergency/requests'], [Bell, 'Unread notifications', data.unread, '/notifications']]
  return <div className="customer-dashboard"><section className="customer-dashboard-head"><div><span className="section-kicker">Your ChanGu</span><h1>Welcome back, {user?.full_name}.</h1><p>Everything you have in motion, in one place.</p></div><Link className="auth-submit" to="/profile">View profile <ArrowUpRight size={16} /></Link></section><div className="dashboard-stat-grid">{cards.map(([Icon, label, value, to]) => <Link className="dashboard-stat" to={to} key={label}><Icon size={19} /><span><small>{label}</small><strong>{value}</strong></span><ArrowUpRight size={15} /></Link>)}</div><section className="dashboard-section"><div className="section-heading"><div><span className="section-kicker">In progress</span><h2>Active services</h2></div><Link to="/orders" className="view-link">View history <ArrowUpRight size={15} /></Link></div>{!activeOrders.length && !activeParcels.length && !activeRides.length && !activeSiren.length ? <EmptyState title="Nothing active right now." detail="Your new orders, rides, parcels, and Siren requests will appear here." /> : <div className="active-service-list">{activeOrders.slice(0, 3).map(item => <Link className="active-service" to={`/orders/${item.id}`} key={`order-${item.id}`}><span><strong>Order #{item.order_number}</strong><small>{item.status.replaceAll('_', ' ')}</small></span><ArrowUpRight size={16} /></Link>)}{activeParcels.slice(0, 3).map(item => <Link className="active-service" to={`/parcel/${item.id}`} key={`parcel-${item.id}`}><span><strong>Parcel #{item.id}</strong><small>{item.status.replaceAll('_', ' ')}</small></span><ArrowUpRight size={16} /></Link>)}{activeRides.slice(0, 3).map(item => <Link className="active-service" to={`/rides/${item.id}`} key={`ride-${item.id}`}><span><strong>Ride #{item.id}</strong><small>{item.status.replaceAll('_', ' ')}</small></span><ArrowUpRight size={16} /></Link>)}{activeSiren.slice(0, 3).map(item => <Link className="active-service" to={`/emergency/requests/${item.id}`} key={`siren-${item.id}`}><span><strong>{item.request_number}</strong><small>{item.status.replaceAll('_', ' ')}</small></span><ArrowUpRight size={16} /></Link>)}</div>}</section><section className="dashboard-quick-links"><Link to="/food">Food</Link><Link to="/shop">Shop</Link><Link to="/parcel">Parcel</Link><Link to="/rides">Rides</Link><Link to="/siren">Siren</Link><Link to="/assistant">AI Assistant</Link><Link to="/cart">Cart</Link></section></div>
}
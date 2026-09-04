import { ClipboardList, ArrowUpRight } from 'lucide-react'
import { Link } from 'react-router-dom'
import { useEffect, useState } from 'react'
import api from '../services/api'
import EmptyState from '../components/EmptyState'
import LoadingSpinner from '../components/LoadingSpinner'

export default function Orders() {
  const [orders, setOrders] = useState(null)
  useEffect(() => { api.get('/api/orders').then(({ data }) => setOrders(data)).catch(() => setOrders([])) }, [])
  if (orders === null) return <LoadingSpinner label="Loading orders..." />
  return <div className="commerce-page"><div className="page-intro"><span className="section-kicker">Your activity</span><h1>My Orders</h1><p>Track your ChanGu purchases.</p></div>{!orders.length ? <EmptyState title="No orders yet." detail="Start exploring ChanGu and place your first order." /> : <div className="orders-list">{orders.map((order) => <Link className="order-row" to={`/orders/${order.id}`} key={order.id}><span><strong>#{order.order_number}</strong><small>{order.items.map((item) => `${item.item_name} x ${item.quantity}`).join(', ')}</small></span><span><b>₹{Number(order.total_amount).toFixed(0)}</b><small>{order.status.replaceAll('_', ' ')}</small></span><ArrowUpRight size={17} /></Link>)}</div>}</div>
}

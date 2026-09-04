import { ArrowLeft, MapPin, RefreshCw } from 'lucide-react'
import { Link, useParams } from 'react-router-dom'
import { useEffect, useState } from 'react'
import api from '../services/api'
import LoadingSpinner from '../components/LoadingSpinner'
import ErrorState from '../components/ErrorState'
import OrderStatusTimeline from '../components/OrderStatusTimeline'
import TrackingMap from '../components/TrackingMap'

export default function DeliveryTracking() {
  const { orderId } = useParams()
  const [order, setOrder] = useState(null)
  const [error, setError] = useState('')
  const [tracking, setTracking] = useState(null)
  useEffect(() => { let active = true; const load = () => Promise.all([api.get(`/api/orders/${orderId}`), api.get(`/api/tracking/orders/${orderId}`)]).then(([orderResponse, trackingResponse]) => { if (active) { setOrder(orderResponse.data); setTracking(trackingResponse.data) } }).catch(() => active && setError('Tracking is unavailable.')); load(); const refresh = event => { if (event.detail?.entity_type === 'ORDER' && String(event.detail.entity_id) === String(orderId)) load() }; window.addEventListener('changu:tracking', refresh); const timer = setInterval(load, 30000); return () => { active = false; clearInterval(timer); window.removeEventListener('changu:tracking', refresh); clearInterval(timer) } }, [orderId])
  if (error) return <ErrorState message={error} />
  if (!order) return <LoadingSpinner label="Loading tracking..." />
  const location = tracking?.location
  const mapUrl = location ? `https://www.openstreetmap.org/?mlat=${location.latitude}&mlon=${location.longitude}#map=16/${location.latitude}/${location.longitude}` : ''
  return <div className="commerce-page"><Link to={`/orders/${orderId}`} className="back-link"><ArrowLeft size={15} /> Order</Link><div className="page-intro"><span className="section-kicker">Delivery tracking</span><h1>Order status</h1><p>#{order.order_number}</p></div><div className="order-detail-card"><OrderStatusTimeline status={order.status} /><TrackingMap location={location} label="Delivery driver location" /><div className="tracking-panel"><MapPin size={22} /><strong>{location ? 'Driver location available' : 'Driver location unavailable'}</strong>{location ? <a href={mapUrl} target="_blank" rel="noreferrer">Open current location</a> : <span>The driver has not shared a current location yet.</span>}<small><RefreshCw size={13}/> Updates automatically when the driver shares location.</small></div></div></div>
}
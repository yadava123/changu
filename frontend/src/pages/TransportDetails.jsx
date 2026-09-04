import { ArrowLeft, MapPin } from 'lucide-react'
import { Link, useParams } from 'react-router-dom'
import { useEffect, useState } from 'react'
import api from '../services/api'
import ErrorState from '../components/ErrorState'
import LoadingSpinner from '../components/LoadingSpinner'
import TrackingMap from '../components/TrackingMap'
export default function TransportDetails({ type }) {
  const { id } = useParams(); const [item, setItem] = useState(null); const [tracking, setTracking] = useState(null); const [error, setError] = useState(''); const [paid, setPaid] = useState(false); const base = type === 'parcel' ? 'parcels' : 'rides'
  useEffect(() => { const load = () => Promise.all([api.get(`/api/${base}/${id}`), api.get(`/api/tracking/${type}/${id}`)]).then(([itemResponse, trackingResponse]) => { setItem(itemResponse.data); setTracking(trackingResponse.data) }).catch(() => setError(`${type} not found.`)); load(); const refresh = event => { if (String(event.detail?.entity_id) === String(id)) load() }; window.addEventListener('changu:tracking', refresh); const timer = setInterval(load, 30000); return () => { clearInterval(timer); window.removeEventListener('changu:tracking', refresh) } }, [base, id, type])
  async function cancel() { try { const { data } = await api.post(`/api/${base}/${id}/cancel`); setItem(data) } catch (requestError) { setError(requestError.response?.data?.detail || `Unable to cancel ${type}.`) } }
  async function pay() { try { await api.post(`/api/payments/services/${type.toUpperCase()}/${id}/success`); setPaid(true); setItem(current => ({ ...current, payment_status: 'PAID' })) } catch (requestError) { setError(requestError.response?.data?.detail || `Unable to record ${type} payment.`) } }
  if (error && !item) return <ErrorState message={error} />; if (!item) return <LoadingSpinner label={`Loading ${type}...`} />
  const location = tracking?.location
  const mapUrl = location ? `https://www.openstreetmap.org/?mlat=${location.latitude}&mlon=${location.longitude}#map=16/${location.latitude}/${location.longitude}` : ''
  const parcelPaymentPending = type === 'parcel' && item.payment_status === 'PENDING' && item.status !== 'CANCELLED'
  const ridePaymentPending = type === 'ride' && item.status === 'RIDE_COMPLETED' && item.payment_status === 'PENDING'
  return <div className="simple-page"><Link to={`/${base}`} className="back-link"><ArrowLeft size={15} /> Back</Link><span className="section-kicker">{type} status</span><h1>#{item.id}</h1><div className="profile-card"><h2>{item.status.replaceAll('_', ' ')}</h2><p>{type === 'parcel' ? `${item.pickup_address} to ${item.drop_address}` : `${item.pickup_address} to ${item.destination}`}</p><strong>₹{Number(item.price || item.fare).toFixed(0)}</strong>{<small>Payment: {item.payment_status}</small>}</div><TrackingMap location={location} label={`${type} driver location`} /><div className="tracking-panel"><MapPin size={22}/><strong>{location ? 'Driver location available' : 'Driver location unavailable'}</strong>{location ? <a href={mapUrl} target="_blank" rel="noreferrer">Open current location</a> : <span>Location will appear after the assigned driver shares it.</span>}</div>{error && <p className="form-error" role="alert">{error}</p>}{['PENDING','REQUESTED','ACCEPTED','DRIVER_ASSIGNED'].includes(item.status) && item.payment_status !== 'PAID' && <button className="auth-submit" type="button" onClick={cancel}>Cancel {type}</button>}{(parcelPaymentPending || ridePaymentPending) && <button className="auth-submit" type="button" onClick={pay} disabled={paid}>{paid ? 'Payment recorded' : `Pay for ${type}`}</button>}</div>
}

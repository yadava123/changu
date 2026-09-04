import { useEffect, useState } from 'react'
import { ArrowLeft, Car } from 'lucide-react'
import { Link, useNavigate } from 'react-router-dom'
import api from '../services/api'
import EmptyState from '../components/EmptyState'
import ErrorState from '../components/ErrorState'
import LoadingSpinner from '../components/LoadingSpinner'
export default function Rides() {
  const [rides, setRides] = useState(null); const [form, setForm] = useState({ pickup_address: '', destination: '', ride_type: 'STANDARD' }); const [error, setError] = useState(''); const [saving, setSaving] = useState(false); const navigate = useNavigate()
  useEffect(() => { api.get('/api/rides').then(({ data }) => setRides(data)).catch(() => setError('Unable to load rides.')) }, [])
  async function submit(event) { event.preventDefault(); setSaving(true); setError(''); try { const { data } = await api.post('/api/rides', form); navigate(`/rides/${data.id}`) } catch (requestError) { setError(requestError.response?.data?.detail || 'Unable to request ride.') } finally { setSaving(false) } }
  if (error && !rides) return <ErrorState message={error} />; if (!rides) return <LoadingSpinner label="Loading rides..." />
  return <div className="form-page"><Link to="/home" className="back-link"><ArrowLeft size={15} /> Home</Link><span className="section-kicker">City travel</span><h1><Car size={28} /> Request a ride</h1>{error && <p className="form-error" role="alert">{error}</p>}<form className="vendor-form" onSubmit={submit}><label>Pickup location<input value={form.pickup_address} onChange={(event) => setForm({ ...form, pickup_address: event.target.value })} required /></label><label>Destination<input value={form.destination} onChange={(event) => setForm({ ...form, destination: event.target.value })} required /></label><label>Ride type<select value={form.ride_type} onChange={(event) => setForm({ ...form, ride_type: event.target.value })}><option>STANDARD</option><option>PREMIUM</option><option>XL</option></select></label><button className="auth-submit" disabled={saving}>{saving ? 'Requesting...' : 'Request ride'}</button></form><h2>Ride history</h2>{!rides.length ? <EmptyState title="No rides yet." /> : rides.map((item) => <Link className="order-row" to={`/rides/${item.id}`} key={item.id}><span><strong>Ride #{item.id}</strong><small>{item.pickup_address} to {item.destination}</small></span><span><b>₹{Number(item.fare).toFixed(0)}</b><small>{item.status.replaceAll('_',' ')}</small></span></Link>)}</div>
}

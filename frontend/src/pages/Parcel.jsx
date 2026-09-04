import { useEffect, useState } from 'react'
import { ArrowLeft, Box } from 'lucide-react'
import { Link, useNavigate } from 'react-router-dom'
import api from '../services/api'
import EmptyState from '../components/EmptyState'
import ErrorState from '../components/ErrorState'
import LoadingSpinner from '../components/LoadingSpinner'

const initial = { pickup_address: '', drop_address: '', sender_name: '', receiver_name: '', parcel_type: 'PACKAGE', weight_kg: 1 }
export default function Parcel() {
  const [parcels, setParcels] = useState(null); const [form, setForm] = useState(initial); const [error, setError] = useState(''); const [saving, setSaving] = useState(false); const navigate = useNavigate()
  useEffect(() => { api.get('/api/parcels').then(({ data }) => setParcels(data)).catch(() => setError('Unable to load parcels.')) }, [])
  async function submit(event) { event.preventDefault(); setSaving(true); setError(''); try { const { data } = await api.post('/api/parcels', { ...form, weight_kg: Number(form.weight_kg) }); navigate(`/parcel/${data.id}`) } catch (requestError) { setError(requestError.response?.data?.detail || 'Unable to create parcel.') } finally { setSaving(false) } }
  if (error && !parcels) return <ErrorState message={error} />; if (!parcels) return <LoadingSpinner label="Loading parcels..." />
  return <div className="form-page"><Link to="/home" className="back-link"><ArrowLeft size={15} /> Home</Link><span className="section-kicker">Local delivery</span><h1><Box size={28} /> Send a parcel</h1>{error && <p className="form-error" role="alert">{error}</p>}<form className="vendor-form" onSubmit={submit}>{[['pickup_address','Pickup location'],['drop_address','Drop location'],['sender_name','Sender name'],['receiver_name','Receiver name'],['parcel_type','Parcel type']].map(([key,label]) => <label key={key}>{label}<input value={form[key]} onChange={(event) => setForm({ ...form, [key]: event.target.value })} required /></label>)}<label>Weight in kg<input type="number" min="0.1" max="100" step="0.1" value={form.weight_kg} onChange={(event) => setForm({ ...form, weight_kg: event.target.value })} required /></label><button className="auth-submit" disabled={saving}>{saving ? 'Creating...' : 'Get estimate and create parcel'}</button></form><h2>Your parcels</h2>{!parcels.length ? <EmptyState title="No parcels yet." /> : parcels.map((item) => <Link className="order-row" to={`/parcel/${item.id}`} key={item.id}><span><strong>Parcel #{item.id}</strong><small>{item.pickup_address} to {item.drop_address}</small></span><span><b>₹{Number(item.price).toFixed(0)}</b><small>{item.status.replaceAll('_',' ')}</small></span></Link>)}</div>
}

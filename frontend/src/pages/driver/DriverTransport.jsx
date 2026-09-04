import { useEffect, useState } from 'react'
import { Box, Car } from 'lucide-react'
import api from '../../services/api'
import LoadingSpinner from '../../components/LoadingSpinner'

const parcelSteps = { ACCEPTED: ['pickup', 'transit', 'out-for-delivery', 'complete'], PICKED_UP: ['transit', 'out-for-delivery', 'complete'], IN_TRANSIT: ['out-for-delivery', 'complete'], OUT_FOR_DELIVERY: ['complete'] }
const rideSteps = { DRIVER_ASSIGNED: ['arriving', 'arrived', 'start', 'complete'], DRIVER_ARRIVING: ['arrived', 'start', 'complete'], DRIVER_ARRIVED: ['start', 'complete'], RIDE_STARTED: ['complete'] }
export default function DriverTransport() {
  const [parcels, setParcels] = useState(null); const [rides, setRides] = useState(null); const [error, setError] = useState('')
  const load = () => Promise.all([api.get('/api/driver/parcels/available'), api.get('/api/driver/rides/available')]).then(([parcelResponse, rideResponse]) => { setParcels(parcelResponse.data); setRides(rideResponse.data) }).catch((requestError) => setError(requestError.response?.data?.detail || 'Go online to view transport requests.'))
  useEffect(() => { load() }, [])
  async function accept(kind, id) { try { await api.post(`/api/driver/${kind}/${id}/accept`); load() } catch (requestError) { setError(requestError.response?.data?.detail || 'Request is no longer available.') } }
  async function advance(kind, id, action) { try { await api.post(`/api/driver/${kind}/${id}/${action}`); load() } catch (requestError) { setError(requestError.response?.data?.detail || 'Unable to update request.') } }
  if (!parcels || !rides) return <LoadingSpinner label="Loading transport requests..." />
  return <><span className="section-kicker">Transport work</span><h1 className="vendor-title">Parcel & rides</h1>{error && <p className="form-error" role="alert">{error}</p>}<h2 className="vendor-section-title"><Box size={18} /> Parcels</h2>{parcels.length ? parcels.map((item) => <Request key={item.id} kind="parcels" item={item} accept={accept} advance={advance} steps={parcelSteps[item.status] || []} />) : <p>No parcel requests available.</p>}<h2 className="vendor-section-title"><Car size={18} /> Rides</h2>{rides.length ? rides.map((item) => <Request key={item.id} kind="rides" item={item} accept={accept} advance={advance} steps={rideSteps[item.status] || []} />) : <p>No ride requests available.</p>}</>
}
function Request({ kind, item, accept, advance, steps }) { const label = kind === 'parcels' ? `${item.pickup_address} to ${item.drop_address}` : `${item.pickup_address} to ${item.destination}`; return <div className="vendor-order"><div><strong>#{item.id} · {kind === 'parcels' ? 'Parcel' : 'Ride'}</strong><small>{label}</small><small>₹{Number(item.price || item.fare).toFixed(0)} · {item.status.replaceAll('_', ' ')}</small></div>{item.status === 'PENDING' || item.status === 'REQUESTED' ? <button className="auth-submit" onClick={() => accept(kind, item.id)}>Accept</button> : steps.map((step) => <button key={step} className="auth-submit" onClick={() => advance(kind, item.id, step)}>{step.replaceAll('_', ' ')}</button>)}</div> }

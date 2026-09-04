import { useState } from 'react'
import { ArrowLeft, Star } from 'lucide-react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import api from '../services/api'

export default function Review() {
  const { orderId } = useParams(); const navigate = useNavigate(); const [rating, setRating] = useState(5); const [comment, setComment] = useState(''); const [error, setError] = useState(''); const [saving, setSaving] = useState(false)
  async function submit(event) { event.preventDefault(); setSaving(true); setError(''); try { await api.post(`/api/reviews/orders/${orderId}`, { rating, comment }); navigate(`/orders/${orderId}`) } catch (requestError) { setError(requestError.response?.data?.detail || 'Unable to submit review.') } finally { setSaving(false) } }
  return <div className="form-page"><Link to={`/orders/${orderId}`} className="back-link"><ArrowLeft size={15} /> Order</Link><span className="section-kicker">Your experience</span><h1>Review order</h1>{error && <p className="form-error" role="alert">{error}</p>}<form className="vendor-form" onSubmit={submit}><label>Rating<select value={rating} onChange={(event) => setRating(Number(event.target.value))}>{[5, 4, 3, 2, 1].map((value) => <option value={value} key={value}>{value} {value === 1 ? 'star' : 'stars'}</option>)}</select></label><label>Comment<textarea value={comment} onChange={(event) => setComment(event.target.value)} minLength="1" maxLength="1000" required /></label><button className="auth-submit" disabled={saving}><Star size={16} /> {saving ? 'Submitting...' : 'Submit review'}</button></form></div>
}

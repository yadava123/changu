import { useEffect, useState } from 'react'
import { ArrowLeft, CreditCard } from 'lucide-react'
import { Link } from 'react-router-dom'
import api from '../services/api'
import EmptyState from '../components/EmptyState'
import ErrorState from '../components/ErrorState'
import LoadingSpinner from '../components/LoadingSpinner'

export default function Payments() {
  const [items, setItems] = useState(null)
  const [error, setError] = useState('')
  useEffect(() => { api.get('/api/payments').then(({ data }) => setItems(data)).catch((requestError) => setError(requestError.response?.data?.detail || 'Unable to load payment history.')) }, [])
  if (error) return <ErrorState message={error} />
  if (!items) return <LoadingSpinner label="Loading payment history..." />
  return <div className="simple-page"><Link to="/customer/dashboard" className="back-link"><ArrowLeft size={15} /> Dashboard</Link><span className="section-kicker">Finance</span><h1>Payment history</h1>{!items.length ? <EmptyState title="No payments yet." detail="Verified payments will appear here after checkout or service completion." /> : <div className="vendor-table">{items.map(item => <div className="vendor-row" key={item.transaction_id}><CreditCard size={16} /><strong>{item.transaction_id}</strong><span>{item.service_type}</span><span>₹{Number(item.amount).toFixed(2)}</span><span>{item.status}</span></div>)}</div>}</div>
}
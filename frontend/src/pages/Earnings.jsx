import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import api from '../services/api'
import LoadingSpinner from '../components/LoadingSpinner'
import ErrorState from '../components/ErrorState'

export default function Earnings() {
  const [data, setData] = useState(null); const [error, setError] = useState('')
  useEffect(() => { api.get('/api/earnings').then(({ data: result }) => setData(result)).catch(() => setError('Earnings are unavailable.')) }, [])
  if (error) return <ErrorState message={error} />
  if (!data) return <LoadingSpinner label="Loading earnings..." />
  return <div className="simple-page"><span className="section-kicker">Finance</span><h1>Earnings</h1><div className="profile-card"><h2>₹{Number(data.earnings || 0).toFixed(2)}</h2><p>{data.completed_items} completed services</p><div className="profile-details"><span><small>Today</small><strong>₹{Number(data.today_earnings || 0).toFixed(2)}</strong></span><span><small>This week</small><strong>₹{Number(data.weekly_earnings || 0).toFixed(2)}</strong></span><span><small>Wallet balance</small><strong>₹{Number(data.wallet_balance || 0).toFixed(2)}</strong></span></div></div><h2 className="vendor-section-title">Recent earnings</h2>{data.records?.length ? <div className="vendor-table">{data.records.map(item => <div className="vendor-row" key={item.id}><strong>{item.source_type} #{item.source_id}</strong><span>Gross ₹{Number(item.gross_amount).toFixed(2)}</span><span>Commission ₹{Number(item.commission_amount).toFixed(2)}</span><span>Net ₹{Number(item.net_amount).toFixed(2)}</span></div>)}</div> : <p>No completed earnings yet.</p>}<Link to="/home" className="back-link">Return home</Link></div>
}

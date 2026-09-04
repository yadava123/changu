import { useEffect, useState } from 'react'
import api from '../../services/api'
import LoadingSpinner from '../../components/LoadingSpinner'

export default function Financials() {
  const [summary, setSummary] = useState(null)
  const [transactions, setTransactions] = useState(null)
  const [query, setQuery] = useState('')
  const [error, setError] = useState('')
  function load() {
    Promise.all([api.get('/api/admin/financial-summary'), api.get('/api/admin/financial-transactions', { params: query ? { transaction_id: query } : {} })])
      .then(([summaryResponse, transactionResponse]) => { setSummary(summaryResponse.data); setTransactions(transactionResponse.data.items); setError('') })
      .catch((requestError) => setError(requestError.response?.data?.detail || 'Unable to load financial records.'))
  }
  useEffect(() => { load() }, [])
  if (error) return <div className="state-panel error-state"><strong>{error}</strong><button onClick={load}>Retry</button></div>
  if (!summary || !transactions) return <LoadingSpinner label="Loading financial records..." />
  const cards = [['Total revenue', summary.total_revenue], ['Today revenue', summary.revenue_today], ['Successful payments', summary.successful_payments], ['Failed payments', summary.failed_payments], ['Refunded payments', summary.refunded_payments], ['Commission', summary.total_commission], ['Partner earnings', summary.total_earnings]]
  return <div><span className="section-kicker">Finance control</span><h1 className="admin-title">Financial records.</h1><div className="admin-stats">{cards.map(([label, value]) => <div className="admin-stat" key={label}><small>{label}</small><strong>{label.includes('revenue') || label === 'Commission' || label === 'Partner earnings' ? `₹${Number(value).toFixed(2)}` : value}</strong></div>)}</div><section className="admin-overview"><div className="section-heading"><h2>Transactions</h2><form onSubmit={event => { event.preventDefault(); load() }}><input value={query} onChange={event => setQuery(event.target.value)} placeholder="Search transaction ID" /><button type="submit">Search</button></form></div>{transactions.length ? <div className="vendor-table">{transactions.map(item => <div className="vendor-row" key={item.transaction_id}><strong>{item.transaction_id}</strong><span>{item.service_type}</span><span>₹{Number(item.amount).toFixed(2)}</span><span>{item.status}</span><span>{item.created_at ? new Date(item.created_at).toLocaleString() : ''}</span></div>)}</div> : <p>No financial transactions found.</p>}</section></div>
}

import { useEffect, useState } from 'react'

import LoadingSpinner from '../../components/LoadingSpinner'
import api from '../../services/api'

const queues = [
  { key: 'vendors', label: 'Vendors', endpoint: '/api/admin/vendor-applications' },
  { key: 'drivers', label: 'Drivers', endpoint: '/api/admin/driver-applications' },
  { key: 'providers', label: 'Providers', endpoint: '/api/admin/provider-applications' },
]

export default function Approvals() {
  const [applications, setApplications] = useState(null)
  const [error, setError] = useState('')
  const [saving, setSaving] = useState(null)

  async function load() {
    try {
      const responses = await Promise.all(queues.map(queue => api.get(queue.endpoint)))
      setApplications(Object.fromEntries(queues.map((queue, index) => [queue.key, responses[index].data])))
      setError('')
    } catch (requestError) {
      setError(requestError.response?.data?.detail || 'Unable to load approval applications.')
    }
  }

  useEffect(() => { load() }, [])

  async function decide(queue, application, status) {
    const subject = application.business_name || application.full_name || application.contact_name || 'this application'
    if (!window.confirm(`${status === 'APPROVED' ? 'Approve' : 'Reject'} ${subject}?`)) return
    setSaving(`${queue.key}-${application.id}`)
    try {
      await api.patch(`${queue.endpoint}/${application.id}`, { status })
      await load()
    } catch (requestError) {
      setError(requestError.response?.data?.detail || 'Unable to update this application.')
    } finally {
      setSaving(null)
    }
  }

  if (!applications && !error) return <LoadingSpinner label="Loading approval applications..." />

  return <div className="admin-page">
    <span className="section-kicker">Governance</span>
    <h1 className="admin-title">Approval center</h1>
    {error && <div className="form-error" role="alert">{error}<button type="button" onClick={load}>Retry</button></div>}
    {applications && queues.map(queue => <section className="admin-section" key={queue.key}>
      <div className="section-heading"><h2>{queue.label}</h2><span>{applications[queue.key].filter(item => item.status === 'PENDING').length} pending</span></div>
      <div className="admin-table">{applications[queue.key].map(application => {
        const pending = application.status === 'PENDING'
        const id = `${queue.key}-${application.id}`
        return <div className="admin-row" key={application.id}>
          <strong>{application.business_name || application.full_name || application.contact_name}</strong>
          <span>{application.business_type || application.vehicle_type || application.provider_type}</span>
          <span>{application.city || application.area}</span>
          <span>{application.status}</span>
          {pending && <div className="admin-actions"><button type="button" disabled={saving === id} onClick={() => decide(queue, application, 'APPROVED')}>Approve</button><button type="button" disabled={saving === id} onClick={() => decide(queue, application, 'REJECTED')}>Reject</button></div>}
        </div>
      })}</div>
    </section>)}
  </div>
}

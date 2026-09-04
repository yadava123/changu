import { useEffect, useState } from 'react'
import { Gift, Star } from 'lucide-react'
import api from '../services/api'
import ErrorState from '../components/ErrorState'
import LoadingSpinner from '../components/LoadingSpinner'

export default function Rewards() {
  const [loyalty, setLoyalty] = useState(null); const [referral, setReferral] = useState(null); const [code, setCode] = useState(''); const [notice, setNotice] = useState(''); const [error, setError] = useState('')
  useEffect(() => { Promise.all([api.get('/api/loyalty'), api.get('/api/referrals')]).then(([points, invite]) => { setLoyalty(points.data); setReferral(invite.data) }).catch(() => setError('Rewards are unavailable.')) }, [])
  async function apply(event) { event.preventDefault(); setError(''); setNotice(''); try { await api.post('/api/referrals/apply', { code }); setNotice('Referral applied.'); setCode('') } catch (requestError) { setError(requestError.response?.data?.detail || 'Unable to apply referral.') } }
  if (error && !loyalty) return <ErrorState message={error} />
  if (!loyalty || !referral) return <LoadingSpinner label="Loading rewards..." />
  return <div className="simple-page"><span className="section-kicker">Rewards</span><h1>Your rewards</h1><div className="profile-card"><Gift size={24} /><h2>{loyalty.points} points</h2><p>Earn 1 point for every ₹10 in a delivered order.</p></div><section className="form-page"><h2><Star size={18} /> Invite friends</h2><p>Your referral code: <strong>{referral.code}</strong></p><form className="vendor-form" onSubmit={apply}><label>Referral code<input value={code} onChange={(event) => setCode(event.target.value.toUpperCase())} minLength="3" maxLength="40" required /></label><button className="auth-submit">Apply referral</button></form>{notice && <p className="form-success" role="status">{notice}</p>}{error && <p className="form-error" role="alert">{error}</p>}</section></div>
}

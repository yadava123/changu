import { ArrowLeft, Sparkles } from 'lucide-react'
import { Link, useLocation } from 'react-router-dom'

export default function ComingSoon() {
  const location = useLocation()
  const title = location.pathname.slice(1) || 'module'
  return <div className="simple-page coming-module"><span className="empty-icon"><Sparkles size={24} /></span><span className="section-kicker">ChanGu {title}</span><h1>Coming Soon</h1><p>This ChanGu module will be implemented in a future phase.</p><Link to="/home" className="back-link"><ArrowLeft size={15} /> Return home</Link></div>
}

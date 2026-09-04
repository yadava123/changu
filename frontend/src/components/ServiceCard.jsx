import { ArrowUpRight } from 'lucide-react'
import { Link } from 'react-router-dom'

export default function ServiceCard({ service }) {
  const Icon = service.icon
  return <Link to={service.route} className={`discovery-service-card ${service.status}`}><span className="service-icon"><Icon size={21} /></span><span className="service-card-copy"><strong>{service.name}</strong><small>{service.description}</small></span>{service.status === 'active' ? <ArrowUpRight className="card-arrow" size={17} /> : <small className="coming-label">Coming soon</small>}</Link>
}

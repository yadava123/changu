import { useEffect,useState } from 'react'
import { Link } from 'react-router-dom'
import api from '../services/api'
import LoadingSpinner from '../components/LoadingSpinner'
import ErrorState from '../components/ErrorState'
export default function DriverApplicationStatus(){const [app,setApp]=useState(null);const [error,setError]=useState('');useEffect(()=>{api.get('/api/driver/applications/me').then(({data})=>setApp(data)).catch(()=>setError('No driver application found.'))},[]);if(!app&&!error)return <LoadingSpinner label="Loading application..."/>;if(error)return <ErrorState message={error}/>;return <div className="simple-page"><span className="section-kicker">ChanGu Delivery Partner</span><h1>Driver Partner Application</h1><div className={`application-status ${app.status.toLowerCase()}`}>{app.status}</div>{app.admin_notes&&<p>Reason: {app.admin_notes}</p>}{app.status==='APPROVED'&&<Link to="/driver/dashboard" className="auth-submit">Open Driver Dashboard</Link>}{app.status==='REJECTED'&&<Link to="/become-driver" className="back-link">Update Application</Link>}</div>}

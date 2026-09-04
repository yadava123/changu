import { Link } from 'react-router-dom'
import { useEffect,useState } from 'react'
import api from '../services/api'
import LoadingSpinner from '../components/LoadingSpinner'
import ErrorState from '../components/ErrorState'
export default function VendorApplicationStatus(){const [app,setApp]=useState(null);const [error,setError]=useState('');useEffect(()=>{api.get('/api/vendor/applications/me').then(({data})=>setApp(data)).catch(()=>setError('No vendor application found.'))},[]);if(!app&&!error)return <LoadingSpinner label="Loading application..."/>;if(error)return <ErrorState message={error}/>;return <div className="simple-page"><span className="section-kicker">ChanGu Partner Program</span><h1>Your Partner Application</h1><p>Business: {app.business_name}</p><div className={`application-status ${app.status.toLowerCase()}`}>{app.status==='APPROVED'?'Approved':app.status==='REJECTED'?'Rejected':'Pending Review'}</div>{app.admin_notes&&<p>Reason: {app.admin_notes}</p>}{app.status==='APPROVED'&&<Link className="auth-submit" to="/vendor/dashboard">Open Vendor Dashboard</Link>}{app.status==='REJECTED'&&<Link className="back-link" to="/become-vendor">Update Application</Link>}</div>}

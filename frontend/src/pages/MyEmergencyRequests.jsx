import { useEffect,useState } from 'react'
import { Link } from 'react-router-dom'
import api from '../services/api'
import LoadingSpinner from '../components/LoadingSpinner'
export default function MyEmergencyRequests(){const [items,setItems]=useState(null);useEffect(()=>{api.get('/api/emergency/requests').then(({data})=>setItems(data))},[]);if(!items)return <LoadingSpinner/>;return <div className="simple-page"><span className="section-kicker">ChanGu Siren</span><h1>Emergency History</h1>{items.length?items.map(item=><Link className="order-row" to={`/emergency/requests/${item.id}`} key={item.id}><span><strong>{item.request_number}</strong><small>{item.emergency_type.replaceAll('_',' ')}</small></span><span>{item.status}</span></Link>):<p>No Siren requests yet.</p>}</div>}

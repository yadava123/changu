import { useEffect,useState } from 'react'
import api from '../../services/api'
import LoadingSpinner from '../../components/LoadingSpinner'
export default function EmergencyRequests(){const [items,setItems]=useState(null);useEffect(()=>{api.get('/api/admin/emergency').then(({data})=>setItems(data))},[]);if(!items)return <LoadingSpinner/>;return <div className="simple-page"><span className="section-kicker">Administration</span><h1>Emergency Requests</h1><div className="vendor-table">{items.map(item=><div className="vendor-row" key={item.id}><strong>{item.request_number}</strong><span>{item.emergency_type}</span><span>{item.priority}</span><span>{item.city}</span><span>{item.status}</span></div>)}</div></div>}

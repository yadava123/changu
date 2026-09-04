import { useEffect,useState } from 'react'
import { ArrowLeft } from 'lucide-react'
import { Link,useParams } from 'react-router-dom'
import api from '../services/api'
import LoadingSpinner from '../components/LoadingSpinner'
import SirenTimeline from '../components/SirenTimeline'
export default function EmergencyRequestDetails(){const {id}=useParams();const [request,setRequest]=useState(null);const load=()=>api.get(`/api/emergency/requests/${id}`).then(({data})=>setRequest(data));useEffect(load,[id]);async function cancel(){if(confirm('Cancel this request?')){await api.post(`/api/emergency/requests/${id}/cancel`);load()}}if(!request)return <LoadingSpinner label="Loading Siren request..."/>;return <div className="simple-page"><Link to="/emergency/requests" className="back-link"><ArrowLeft size={15}/> Siren history</Link><span className="section-kicker">Siren Request</span><h1>{request.request_number}</h1><p>{request.emergency_type.replaceAll('_',' ')}</p><div className="order-detail-card"><SirenTimeline status={request.status}/>{request.provider_id&&<div className="application-status approved">Provider Assigned</div>}<p>{request.description}<br/>{request.address}, {request.area}, {request.city}</p>{!['ARRIVED','RESOLVED','CANCELLED'].includes(request.status)&&<button className="cancel-order" onClick={cancel}>Cancel Request</button>}</div></div>}

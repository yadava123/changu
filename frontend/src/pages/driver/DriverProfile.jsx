import { useEffect,useState } from 'react'
import api from '../../services/api'
import LoadingSpinner from '../../components/LoadingSpinner'
export default function DriverProfile(){const [driver,setDriver]=useState(null);useEffect(()=>{api.get('/api/driver/status').then(()=>api.get('/api/driver/applications/me')).then(({data})=>setDriver(data))},[]);if(!driver)return <LoadingSpinner/>;return <div className="simple-page"><span className="section-kicker">Delivery partner</span><h1>{driver.full_name}</h1><p>{driver.email}<br/>{driver.phone}<br/>{driver.vehicle_type} · {driver.vehicle_number}<br/>{driver.city}, {driver.state}</p><div className="application-status approved">Approved driver</div></div>}

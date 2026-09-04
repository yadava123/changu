import { useEffect,useState } from 'react'
import api from '../../services/api'
import LoadingSpinner from '../../components/LoadingSpinner'
export default function DeliveryHistory(){const [items,setItems]=useState(null);useEffect(()=>{api.get('/api/driver/deliveries').then(({data})=>setItems(data.filter(item=>['DELIVERED','CANCELLED'].includes(item.status))))},[]);if(!items)return <LoadingSpinner/>;return <><span className="section-kicker">Completed work</span><h1 className="vendor-title">Delivery History</h1><div className="vendor-table">{items.map(item=><div className="vendor-row" key={item.id}><strong>DLV{String(item.id).padStart(5,'0')}</strong><span>Order #{item.order_id}</span><span>{item.status}</span><span>₹{item.delivery_earning}</span></div>)}</div></>}

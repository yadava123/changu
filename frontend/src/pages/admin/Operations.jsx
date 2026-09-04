import { useEffect,useState } from 'react'
import api from '../../services/api'
import LoadingSpinner from '../../components/LoadingSpinner'
export default function Operations({type}){
	const [items,setItems]=useState(null)
	const endpoint=type==='vendors'?'/api/admin/vendors':type==='deliveries'?'/api/admin/deliveries':type==='parcels'?'/api/admin/parcels':type==='rides'?'/api/admin/rides':type==='siren'?'/api/admin/siren':type==='products'?'/api/admin/products':type==='ai'?'/api/ai/analytics':'/api/admin/orders'
	useEffect(()=>{api.get(endpoint).then(({data})=>setItems(data.items||data))},[endpoint])
	async function toggleStatus(item){
		const nextActive=!item.is_active
		const label=type==='products'?'product':'vendor'
		if(!window.confirm(`${nextActive?'Activate':'Deactivate'} this ${label}?`)) return
		const resource=type==='products'?'products':'vendors'
		await api.patch(`/api/admin/${resource}/${item.id}/status`,{is_active:nextActive})
		setItems(current=>current.map(currentItem=>currentItem.id===item.id?{...currentItem,is_active:nextActive,is_available:type==='products'?nextActive:currentItem.is_available}:currentItem))
	}
	if(!items)return <LoadingSpinner label={`Loading ${type}...`}/>
	if(type==='ai')return <div className="admin-page"><span className="section-kicker">Intelligence</span><h1 className="admin-title">AI Analytics</h1><div className="admin-table"><div className="admin-row"><strong>Total requests</strong><span>{items.total_requests}</span></div><div className="admin-row"><strong>Successful requests</strong><span>{items.successful_requests}</span></div><div className="admin-row"><strong>Failed requests</strong><span>{items.failed_requests}</span></div><div className="admin-row"><strong>Average latency</strong><span>{items.average_latency_ms} ms</span></div></div></div>
	return <div className="admin-page"><span className="section-kicker">Operations</span><h1 className="admin-title">{type[0].toUpperCase()+type.slice(1)}</h1><div className="admin-table">{items.map(item=>type==='vendors'?<div className="admin-row" key={item.id}><strong>{item.business_name}</strong><span>{item.business_type}</span><span>{item.city}</span><span>{item.is_active?'ACTIVE':'INACTIVE'}</span><button type="button" onClick={()=>toggleStatus(item)}>{item.is_active?'Deactivate':'Activate'}</button></div>:type==='products'?<div className="admin-row" key={item.id}><strong>{item.name}</strong><span>{item.category}</span><span>₹{item.price}</span><span>{item.is_available?'AVAILABLE':'UNAVAILABLE'}</span><button type="button" onClick={()=>toggleStatus({...item,is_active:item.is_available})}>{item.is_available?'Deactivate':'Activate'}</button></div>:<div className="admin-row" key={item.id}><strong>{item.order_number||item.request_number||item.name||`#${item.id}`}</strong><span>{item.status||item.category||''}</span><span>{item.city||item.delivery_address||''}</span><span>{item.total_amount?`₹${item.total_amount}`:''}</span></div>)}</div></div>
}

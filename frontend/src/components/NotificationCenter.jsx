import { Bell } from 'lucide-react'
import { useEffect,useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import api from '../services/api'
import { useAuth } from '../context/AuthContext'

export default function NotificationCenter(){
	const [count,setCount]=useState(0)
	const [toast,setToast]=useState(null)
	const navigate=useNavigate()
	const { token } = useAuth()
	useEffect(()=>{
		const load=()=>api.get('/api/notifications/unread-count').then(({data})=>setCount(data.count)).catch(()=>{})
		load()
		const timer=setInterval(load,30000)
		if (!token) return ()=>clearInterval(timer)
		const apiUrl=import.meta.env.VITE_API_URL || window.location.origin
		const socketUrl=`${apiUrl.replace(/^http/, 'ws')}/ws?token=${encodeURIComponent(token)}`
		const retryDelays=[1000,2000,5000,10000,30000]
		let socket
		let retryIndex=0
		let retryTimer
		let stopped=false
		const connect=()=>{
			if(stopped)return
			socket=new WebSocket(socketUrl)
			socket.onopen=()=>{retryIndex=0}
			socket.onmessage=(event)=>{
				try{
					const message=JSON.parse(event.data)
					if(message.type==='LOCATION_UPDATED') window.dispatchEvent(new CustomEvent('changu:tracking', { detail: message }))
					if(message.type==='NOTIFICATION'){
						setCount((current)=>current+(!message.data?.is_read?1:0))
						setToast(message)
						setTimeout(()=>setToast(null),6000)
						window.dispatchEvent(new CustomEvent('changu:notification', { detail: message }))
					}
				}catch{}
			}
			socket.onclose=()=>{
				if(stopped)return
				const delay=retryDelays[Math.min(retryIndex,retryDelays.length-1)]
				retryIndex+=1
				retryTimer=setTimeout(connect,delay)
			}
			socket.onerror=()=>socket.close()
		}
		connect()
		return ()=>{stopped=true;clearInterval(timer);clearTimeout(retryTimer);socket?.close()}
	},[token])
	function viewToast(){
		const routes={ORDER:`/orders/${toast?.entity_id}`,DELIVERY:`/orders/${toast?.entity_id}/tracking`,PARCEL:`/parcel/${toast?.entity_id}`,RIDE:`/rides/${toast?.entity_id}`,SIREN:`/emergency/requests/${toast?.entity_id}`,PAYMENT:'/payments'}
		navigate(routes[toast?.entity_type] || '/notifications'); setToast(null)
	}
	return <><Link className="notification-bell" to="/notifications" aria-label={`Notifications${count>0?`, ${count} unread`:''}`}><Bell size={19}/>{count>0&&<span>{count}</span>}</Link>{toast&&<div className="notification-toast" role="status"><strong>{toast.data.title}</strong><span>{toast.data.message}</span><button type="button" onClick={viewToast}>View</button></div>}</>
}

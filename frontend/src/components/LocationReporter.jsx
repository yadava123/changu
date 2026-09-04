import { useEffect, useState } from 'react'
import api from '../services/api'

export default function LocationReporter({ endpoint, active }) {
  const [state, setState] = useState('idle')
  useEffect(() => {
    if (!active) { setState('offline'); return undefined }
    if (!navigator.geolocation) { setState('unavailable'); return undefined }
    let stopped = false
    const report = () => navigator.geolocation.getCurrentPosition(async position => {
      if (stopped) return
      try { await api.post(endpoint, { latitude: position.coords.latitude, longitude: position.coords.longitude }); setState('sharing') } catch { setState('error') }
    }, () => setState('denied'), { enableHighAccuracy: true, maximumAge: 15000, timeout: 10000 })
    report()
    const timer = setInterval(report, 30000)
    return () => { stopped = true; clearInterval(timer) }
  }, [endpoint, active])
  if (state === 'sharing') return <small className="location-status">Location sharing active</small>
  if (state === 'denied') return <small className="location-status">Location permission denied</small>
  if (state === 'unavailable') return <small className="location-status">Location unavailable on this device</small>
  if (state === 'error') return <small className="location-status">Unable to share location</small>
  return null
}
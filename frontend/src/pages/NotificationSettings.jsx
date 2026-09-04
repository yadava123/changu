import { useEffect, useState } from 'react'
import api from '../services/api'

const fields = [
  ['order_updates', 'Order Updates'],
  ['delivery_updates', 'Delivery Updates'],
  ['payment_updates', 'Payment Updates'],
  ['promotions', 'Promotions'],
  ['loyalty', 'Rewards'],
  ['referrals', 'Referral Updates'],
  ['system_notifications', 'System Notifications'],
]

export default function NotificationSettings() {
  const [settings, setSettings] = useState(null)
  const [saved, setSaved] = useState(false)
  useEffect(() => { api.get('/api/notification-preferences').then(({ data }) => setSettings(data)) }, [])
  async function save(event) {
    event.preventDefault()
    await api.patch('/api/notification-preferences', settings)
    setSaved(true)
  }
  if (!settings) return <div className="simple-page"><h1>Notification Settings</h1><p>Loading...</p></div>
  return <div className="form-page"><span className="section-kicker">Alerts</span><h1>Notification Settings</h1><form className="vendor-form" onSubmit={save}>
    {fields.map(([key, label]) => <label className="toggle" key={key}><span>{label}</span><input type="checkbox" checked={settings[key]} onChange={(event) => setSettings({ ...settings, [key]: event.target.checked })} /></label>)}
    <button className="auth-submit" type="submit">Save Preferences</button>
    {saved && <p role="status">Preferences saved.</p>}
  </form></div>
}

import { Navigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function VendorRoute({ children }) {
  const { user, loading } = useAuth()
  if (loading) return <div className="auth-loading">Loading vendor account...</div>
  if (user?.role !== 'VENDOR') return <Navigate to="/home" replace />
  return children
}

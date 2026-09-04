import { Navigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function AdminRoute({ children }) {
  const { user, loading } = useAuth()
  if (loading) return <div className="auth-loading">Loading admin account...</div>
  if (user?.role !== 'ADMIN') return <Navigate to="/home" replace />
  return children
}

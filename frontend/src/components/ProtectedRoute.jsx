import { Navigate, useLocation } from 'react-router-dom'

import { useAuth } from '../context/AuthContext'

export default function ProtectedRoute({ children }) {
  const { user, isAuthenticated, loading } = useAuth()
  const location = useLocation()

  if (loading) return <div className="auth-loading">Restoring your ChanGu session...</div>
  if (!isAuthenticated) return <Navigate to="/customer/login" replace state={{ from: location }} />
  if (user?.role !== 'CUSTOMER') return <Navigate to={user?.role === 'VENDOR' ? '/vendor/dashboard' : user?.role === 'DRIVER' ? '/driver/dashboard' : user?.role === 'EMERGENCY_PROVIDER' ? '/provider/dashboard' : '/admin/dashboard'} replace />
  return children
}

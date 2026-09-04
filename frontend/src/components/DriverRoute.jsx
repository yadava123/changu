import { Navigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
export default function DriverRoute({ children }) { const { user, loading } = useAuth(); if (loading) return <div className="auth-loading">Loading driver account...</div>; return user?.role === 'DRIVER' ? children : <Navigate to="/home" replace /> }

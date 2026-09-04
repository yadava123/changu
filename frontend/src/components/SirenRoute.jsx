import { Navigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
export default function SirenRoute({children}){const {user,loading}=useAuth();if(loading)return <div className="auth-loading">Loading provider account...</div>;return user?.role==='EMERGENCY_PROVIDER'?children:<Navigate to="/home" replace/>}

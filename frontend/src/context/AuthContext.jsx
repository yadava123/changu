import { createContext, useContext, useEffect, useState } from 'react'

import api from '../services/api'

const TOKEN_KEY = 'changu_access_token'
const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem(TOKEN_KEY))
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(Boolean(token))

  useEffect(() => {
    if (!token) {
      setLoading(false)
      return undefined
    }
    api.get('/api/auth/me')
      .then(({ data }) => setUser(data))
      .catch(() => {
        localStorage.removeItem(TOKEN_KEY)
        setToken(null)
        setUser(null)
      })
      .finally(() => setLoading(false))
  }, [token])

  useEffect(() => {
    function handleAuthExpired() {
      setToken(null)
      setUser(null)
    }
    window.addEventListener('changu:auth-expired', handleAuthExpired)
    return () => window.removeEventListener('changu:auth-expired', handleAuthExpired)
  }, [])

  async function login(credentials, role) {
    const { data } = await api.post(role ? `/api/auth/login/${role}` : '/api/auth/login', credentials)
    localStorage.setItem(TOKEN_KEY, data.access_token)
    setUser(data.user)
    setToken(data.access_token)
    return data
  }

  async function register(details, role = 'customer') {
    const { data } = await api.post(`/api/auth/register/${role}`, details)
    return data
  }

  function logout() {
    localStorage.removeItem(TOKEN_KEY)
    setToken(null)
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, token, isAuthenticated: Boolean(user && token), loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) throw new Error('useAuth must be used within AuthProvider')
  return context
}

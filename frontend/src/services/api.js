import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || window.location.origin,
  timeout: 5000,
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('changu_access_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401 && !error.config?.url?.includes('/api/auth/login')) {
      localStorage.removeItem('changu_access_token')
      window.dispatchEvent(new Event('changu:auth-expired'))
    }
    return Promise.reject(error)
  },
)

export const getHealth = () => api.get('/api/health')

export default api

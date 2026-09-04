import api from './api'

export const getProducts = (params = {}) => api.get('/api/products', { params })
export const getProduct = (id) => api.get(`/api/products/${id}`)

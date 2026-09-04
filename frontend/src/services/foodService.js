import api from './api'

export const getFood = (params = {}) => api.get('/api/food', { params })
export const getFoodItem = (id) => api.get(`/api/food/${id}`)

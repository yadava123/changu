import api from './api'

export const getRestaurants = (params = {}) => api.get('/api/restaurants', { params })
export const getRestaurant = (id) => api.get(`/api/restaurants/${id}`)

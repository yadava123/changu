import api from './api'

export const searchCatalog = (params = {}) => api.get('/api/search', { params })

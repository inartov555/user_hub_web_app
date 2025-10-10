import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_BASE || 'http://127.0.0.1:8000/api'

export const api = axios.create({ baseURL: API_BASE })

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

export const login = async (username, password) => {
  const { data } = await api.post('/auth/token/', { username, password })
  localStorage.setItem('token', data.access)
  localStorage.setItem('refresh', data.refresh)
  return data
}

export const signup = (payload) => api.post('/auth/signup/', payload).then(r => r.data)
export const getMe = () => api.get('/me/').then(r => r.data)
export const updateMe = (formData) => api.put('/me/', formData, { headers: { 'Content-Type': 'multipart/form-data' }}).then(r => r.data)
export const changePassword = (payload) => api.put('/me/change-password/', payload).then(r => r.data)
export const importExcel = (file) => {
  const fd = new FormData()
  fd.append('file', file)
  return api.post('/me/import-excel/', fd, { headers: { 'Content-Type': 'multipart/form-data' }}).then(r => r.data)
}

export const fetchUsers = async ({ page=1, pageSize=20, ordering='', filters={} }) => {
  const params = { page, page_size: pageSize }
  if (ordering) params.ordering = ordering
  for (const [k, v] of Object.entries(filters)) if (v) params[k] = v
  const { data } = await api.get('/users/', { params })
  return data
}

export const fetchStats = () => api.get('/users/stats/').then(r => r.data)

import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 120000, // 2 min for AI processing
})

api.interceptors.response.use(
  (res) => res,
  (err) => {
    const msg = err.response?.data?.detail || err.message || 'Request failed'
    return Promise.reject(new Error(msg))
  }
)

export const uploadDocuments = async (files, whatIfScenario = null) => {
  const formData = new FormData()
  files.forEach((file) => formData.append('files', file))
  if (whatIfScenario) formData.append('what_if_scenario', whatIfScenario)
  const res = await api.post('/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return res.data
}

export const approveVendor = async (payload) => {
  const res = await api.post('/approve', payload)
  return res.data
}

export const getHistory = async (limit = 50) => {
  const res = await api.get('/history', { params: { limit } })
  return res.data
}

export const whatIfAnalysis = async (payload) => {
  const res = await api.post('/whatif', payload)
  return res.data
}

export default api

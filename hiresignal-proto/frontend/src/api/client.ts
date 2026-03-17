import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const client = axios.create({
  baseURL: API_BASE_URL,
})

// Add token to headers
client.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export const authAPI = {
  login: (email: string, password: string) =>
    client.post('/api/auth/login', { email, password }),
  getMe: () => client.get('/api/auth/me'),
}

export const jobsAPI = {
  list: () => client.get('/api/jobs'),
  get: (jobId: string) => client.get(`/api/jobs/${jobId}`),
  create: (data: any) => client.post('/api/jobs', data),
  uploadResumes: (jobId: string, formData: FormData) =>
    client.post(`/api/jobs/${jobId}/upload`, formData),
  previewJD: (jdText: string) => {
    const formData = new FormData()
    formData.append('jd_text', jdText)
    return client.post('/api/jobs/preview-jd', formData)
  },
  getResults: (jobId: string) => client.get(`/api/jobs/${jobId}/results`),
  getSummary: (jobId: string) => client.get(`/api/jobs/${jobId}/summary`),
}

export const screeningAPI = {
  singleScreen: (formData: FormData) =>
    client.post('/api/screen/single', formData),
}

export const feedbackAPI = {
  create: (data: any) => client.post('/api/feedback', data),
  getForJob: (jobId: string) => client.get(`/api/feedback/job/${jobId}`),
}

export const exportAPI = {
  csv: (jobId: string) =>
    client.get(`/api/export/${jobId}/csv`, { responseType: 'blob' }),
  excel: (jobId: string) =>
    client.get(`/api/export/${jobId}/excel`, { responseType: 'blob' }),
}

export const analyticsAPI = {
  getOverview: () => client.get('/api/analytics/overview'),
  getScoreTrend: () => client.get('/api/analytics/score-trend'),
  getSkills: () => client.get('/api/analytics/skills'),
}

export default client

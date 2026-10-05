import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
  timeout: 60000
})

// Ingest module
export const uploadDocument = (file, onProgress) => {
  const formData = new FormData()
  formData.append('file', file)
  return api.post('/ingest/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: onProgress
  })
}
export const getDocuments = () => api.get('/ingest/documents')
export const getNeedsReview = () => api.get('/ingest/needs-review')
export const triggerSeedIngestion = () => api.post('/ingest/seed')

// Reports module
export const generateReport = (docIds, reportType = 'mine_status_summary') =>
  api.post('/reports/generate', { doc_ids: docIds, report_type: reportType })
export const downloadReport = (reportHtml, format = 'docx') =>
  api.post('/reports/download', { report_html: reportHtml, format }, { responseType: 'blob' })

// Word cloud module
export const getWordCloudData = (docIds = []) => {
  const params = docIds.length ? `?doc_ids=${docIds.join(',')}` : ''
  return api.get(`/wordcloud/data${params}`)
}

// Chat module
export const sendChatQuery = (question, previousInteractionId = null) =>
  api.post('/chat/query', { question, previous_interaction_id: previousInteractionId })

// Validation module
export const getConflicts = () => api.get('/validation/conflicts')
export const runValidation = () => api.post('/validation/run')
export const approveConflict = (conflictId) =>
  api.post(`/validation/approve/${conflictId}`, {}, { headers: { 'X-User-Role': 'admin' } })

// Audit module
export const getAuditLog = () => api.get('/audit/log')

// Clearance module
export const getClearanceTimeline = () => api.get('/clearance/timeline')

// Health check
export const healthCheck = () => api.get('/health')

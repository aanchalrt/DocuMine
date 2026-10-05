import React, { useState, useEffect, useCallback, useRef } from 'react'
import { getDocuments, uploadDocument, triggerSeedIngestion, getNeedsReview } from '../services/api.js'

const DOC_TYPE_COLORS = {
  geological_report: 'bg-blue-100 text-blue-800',
  production_log: 'bg-green-100 text-green-800',
  environmental_compliance: 'bg-teal-100 text-teal-800',
  mine_plan: 'bg-indigo-100 text-indigo-800',
  lease_document: 'bg-purple-100 text-purple-800',
}

function ConfidenceBar({ value }) {
  const pct = Math.round((value || 0) * 100)
  const color = value >= 0.8 ? 'bg-green-500' : value >= 0.6 ? 'bg-yellow-400' : 'bg-red-500'
  return (
    <div className="flex items-center gap-2">
      <div className="w-24 h-2 bg-gray-200 rounded-full overflow-hidden">
        <div className={`h-full rounded-full ${color}`} style={{ width: `${pct}%` }} />
      </div>
      <span className="text-xs text-gray-500">{pct}%</span>
    </div>
  )
}

function DocTypeBadge({ type }) {
  const cls = DOC_TYPE_COLORS[type] || 'bg-gray-100 text-gray-700'
  return (
    <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${cls}`}>
      {(type || 'unknown').replace(/_/g, ' ')}
    </span>
  )
}

export default function Ingestion() {
  const [documents, setDocuments] = useState([])
  const [selectedDoc, setSelectedDoc] = useState(null)
  const [uploading, setUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [dragging, setDragging] = useState(false)
  const [loadingDocs, setLoadingDocs] = useState(false)
  const [seeding, setSeeding] = useState(false)
  const [error, setError] = useState(null)
  const [uploadError, setUploadError] = useState(null)
  const fileInputRef = useRef(null)

  const fetchDocs = useCallback(async () => {
    setLoadingDocs(true)
    setError(null)
    try {
      const res = await getDocuments()
      const data = res.data
      if (Array.isArray(data)) setDocuments(data)
      else if (data && Array.isArray(data.documents)) setDocuments(data.documents)
      else setDocuments([])
    } catch (e) {
      setError('Could not load documents. Is the backend running?')
    } finally {
      setLoadingDocs(false)
    }
  }, [])

  useEffect(() => { fetchDocs() }, [fetchDocs])

  const handleFile = async (file) => {
    const allowed = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'image/png', 'image/jpeg']
    if (!allowed.includes(file.type)) {
      setUploadError('Unsupported file type. Use PDF, DOCX, XLSX, PNG, or JPG.')
      return
    }
    setUploading(true)
    setUploadProgress(0)
    setUploadError(null)
    try {
      const res = await uploadDocument(file, (evt) => {
        if (evt.total) setUploadProgress(Math.round((evt.loaded / evt.total) * 100))
      })
      await fetchDocs()
      const uploaded = res.data
      if (uploaded && uploaded.document_id) {
        const fresh = documents.find(d => d.document_id === uploaded.document_id) || uploaded
        setSelectedDoc(fresh)
      }
    } catch (e) {
      setUploadError(e.response?.data?.detail || 'Upload failed. Please try again.')
    } finally {
      setUploading(false)
      setUploadProgress(0)
    }
  }

  const onDropZoneClick = () => fileInputRef.current?.click()

  const onFileChange = (e) => {
    const f = e.target.files?.[0]
    if (f) handleFile(f)
    e.target.value = ''
  }

  const onDrop = (e) => {
    e.preventDefault()
    setDragging(false)
    const f = e.dataTransfer.files?.[0]
    if (f) handleFile(f)
  }

  const handleSeed = async () => {
    setSeeding(true)
    setError(null)
    try {
      await triggerSeedIngestion()
      await fetchDocs()
    } catch (e) {
      setError('Seed ingestion failed or already seeded.')
    } finally {
      setSeeding(false)
    }
  }

  const docId = (d) => d?.document_id || d?.id
  const fields = selectedDoc ? (selectedDoc.extracted_fields || selectedDoc.fields || []) : []
  const needsReview = fields.filter(f => f.flag === 'needs_review' || (f.confidence !== undefined && f.confidence < 0.6))

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div>
          <h1 className="text-2xl font-bold text-gray-800">📄 Smart Document Ingestion</h1>
          <p className="text-sm text-gray-500 mt-0.5">Extract structured fields from geological reports, production logs, and more.</p>
        </div>
        <button
          onClick={handleSeed}
          disabled={seeding}
          className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-60 text-white text-sm font-medium px-4 py-2 rounded-lg shadow transition"
        >
          {seeding ? <span className="animate-spin">⏳</span> : '🌱'}
          {seeding ? 'Seeding…' : 'Load Seed Data'}
        </button>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 text-sm rounded-xl px-4 py-3">{error}</div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left: Document list */}
        <div className="lg:col-span-1 space-y-4">
          {/* Upload zone */}
          <div
            onClick={onDropZoneClick}
            onDragOver={(e) => { e.preventDefault(); setDragging(true) }}
            onDragLeave={() => setDragging(false)}
            onDrop={onDrop}
            className={`border-2 border-dashed rounded-xl p-6 text-center cursor-pointer transition-all
              ${dragging ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-blue-400 hover:bg-gray-50'}`}
          >
            <div className="text-4xl mb-2">☁️</div>
            <div className="text-sm font-medium text-gray-700">Drop file here or click to upload</div>
            <div className="text-xs text-gray-400 mt-1">PDF, DOCX, XLSX, PNG, JPG</div>
            <input ref={fileInputRef} type="file" className="hidden" accept=".pdf,.docx,.xlsx,.png,.jpg,.jpeg" onChange={onFileChange} />
          </div>

          {uploading && (
            <div className="space-y-1">
              <div className="text-sm text-gray-600 flex justify-between">
                <span>Uploading…</span><span>{uploadProgress}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div className="bg-blue-600 h-2 rounded-full transition-all" style={{ width: `${uploadProgress}%` }} />
              </div>
            </div>
          )}
          {uploadError && (
            <div className="text-sm text-red-600 bg-red-50 rounded-lg px-3 py-2 border border-red-200">{uploadError}</div>
          )}

          {/* Doc list */}
          <div className="bg-white rounded-xl shadow-md overflow-hidden">
            <div className="px-4 py-3 border-b border-gray-100 flex items-center justify-between">
              <span className="text-sm font-semibold text-gray-700">Ingested Documents</span>
              <span className="text-xs bg-blue-100 text-blue-700 rounded-full px-2 py-0.5">{documents.length}</span>
            </div>
            {loadingDocs ? (
              <div className="p-4 space-y-3">
                {[1,2,3].map(i => <div key={i} className="h-12 bg-gray-100 rounded-lg animate-pulse" />)}
              </div>
            ) : documents.length === 0 ? (
              <div className="p-6 text-center text-sm text-gray-400">No documents yet. Upload a file or load seed data.</div>
            ) : (
              <ul className="divide-y divide-gray-50">
                {documents.map(doc => {
                  const id = docId(doc)
                  return (
                    <li key={id}>
                      <button
                        onClick={() => setSelectedDoc(doc)}
                        className={`w-full text-left px-4 py-3 hover:bg-blue-50 transition ${docId(selectedDoc) === id ? 'bg-blue-50 border-l-4 border-blue-600' : ''}`}
                      >
                        <div className="text-sm font-medium text-gray-800 truncate">{doc.filename || id}</div>
                        <div className="mt-1">
                          <DocTypeBadge type={doc.doc_type} />
                        </div>
                      </button>
                    </li>
                  )
                })}
              </ul>
            )}
          </div>
        </div>

        {/* Right: Extracted fields */}
        <div className="lg:col-span-2 space-y-4">
          {!selectedDoc ? (
            <div className="bg-white rounded-xl shadow-md p-12 text-center">
              <div className="text-5xl mb-3">📋</div>
              <div className="text-gray-500 text-sm">Select a document on the left to view its extracted fields.</div>
            </div>
          ) : (
            <>
              <div className="bg-white rounded-xl shadow-md overflow-hidden">
                <div className="px-5 py-4 border-b border-gray-100">
                  <div className="flex items-center justify-between flex-wrap gap-2">
                    <div>
                      <h2 className="text-base font-semibold text-gray-800">{selectedDoc.filename || docId(selectedDoc)}</h2>
                      <div className="flex items-center gap-2 mt-1">
                        <DocTypeBadge type={selectedDoc.doc_type} />
                        {needsReview.length > 0 && (
                          <span className="text-xs bg-orange-100 text-orange-700 rounded-full px-2 py-0.5">
                            ⚠️ {needsReview.length} need review
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                </div>

                {fields.length === 0 ? (
                  <div className="p-8 text-center text-sm text-gray-400">No extracted fields available.</div>
                ) : (
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead>
                        <tr className="bg-gray-50 text-left">
                          <th className="px-4 py-3 font-semibold text-gray-600 text-xs uppercase tracking-wider">Field</th>
                          <th className="px-4 py-3 font-semibold text-gray-600 text-xs uppercase tracking-wider">Value</th>
                          <th className="px-4 py-3 font-semibold text-gray-600 text-xs uppercase tracking-wider">Unit</th>
                          <th className="px-4 py-3 font-semibold text-gray-600 text-xs uppercase tracking-wider">Confidence</th>
                          <th className="px-4 py-3 font-semibold text-gray-600 text-xs uppercase tracking-wider">Status</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-gray-50">
                        {fields.map((field, idx) => {
                          const needsRev = field.flag === 'needs_review' || (field.confidence !== undefined && field.confidence < 0.6)
                          const fieldName = field.field_name || field.name || 'field'
                          return (
                            <tr key={idx} className={needsRev ? 'needs-review' : 'hover:bg-gray-50'}>
                              <td className="px-4 py-2.5 font-medium text-gray-700">{fieldName}</td>
                              <td className="px-4 py-2.5 text-gray-900 font-semibold">{String(field.value ?? '—')}</td>
                              <td className="px-4 py-2.5 text-gray-500">{field.unit || '—'}</td>
                              <td className="px-4 py-2.5"><ConfidenceBar value={field.confidence} /></td>
                              <td className="px-4 py-2.5">
                                {needsRev ? (
                                  <span className="text-xs bg-orange-100 text-orange-700 rounded-full px-2 py-0.5 font-medium">⚠ Review</span>
                                ) : (
                                  <span className="text-xs bg-green-100 text-green-700 rounded-full px-2 py-0.5 font-medium">✓ OK</span>
                                )}
                              </td>
                            </tr>
                          )
                        })}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>

              {needsReview.length > 0 && (
                <div className="bg-orange-50 border border-orange-200 rounded-xl p-4">
                  <h3 className="text-sm font-semibold text-orange-800 mb-3">⚠️ Fields Needing Review</h3>
                  <div className="space-y-2">
                    {needsReview.map((f, idx) => {
                      const fieldName = f.field_name || f.name || 'field'
                      return (
                        <div key={idx} className="bg-white rounded-lg px-4 py-2.5 border border-orange-200 flex items-start justify-between gap-4">
                          <div>
                            <div className="text-sm font-medium text-gray-800">{fieldName}</div>
                            <div className="text-xs text-gray-500 mt-0.5">Value: <span className="font-semibold text-gray-700">{String(f.value ?? '—')}</span> {f.unit || ''}</div>
                          </div>
                          <ConfidenceBar value={f.confidence} />
                        </div>
                      )
                    })}
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  )
}

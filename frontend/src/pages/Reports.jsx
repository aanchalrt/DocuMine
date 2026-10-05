import React, { useState, useEffect, useCallback } from 'react'
import { getDocuments, generateReport, downloadReport } from '../services/api.js'
import { useRole } from '../App.jsx'

function CitationTag({ docName, field }) {
  const [showTip, setShowTip] = useState(false)
  return (
    <span
      className="citation-tag relative"
      onMouseEnter={() => setShowTip(true)}
      onMouseLeave={() => setShowTip(false)}
    >
      [{docName}]
      {showTip && (
        <span className="absolute bottom-full left-0 mb-1 z-50 bg-gray-800 text-white text-xs rounded px-2 py-1 whitespace-nowrap shadow-lg">
          {docName}{field ? ` · ${field}` : ''}
        </span>
      )}
    </span>
  )
}

function renderHtmlWithCitations(html) {
  if (!html) return null
  // Replace [DocA] style citations with CitationTag components
  const parts = html.split(/(\[[^\]]+\])/g)
  return parts.map((part, i) => {
    const match = part.match(/^\[([^\]]+)\]$/)
    if (match) {
      return <CitationTag key={i} docName={match[1]} field={null} />
    }
    return <span key={i} dangerouslySetInnerHTML={{ __html: part }} />
  })
}

export default function Reports() {
  const { role } = useRole()
  const [documents, setDocuments] = useState([])
  const [selectedIds, setSelectedIds] = useState([])
  const [loadingDocs, setLoadingDocs] = useState(false)
  const [generating, setGenerating] = useState(false)
  const [reportHtml, setReportHtml] = useState(null)
  const [reportTitle, setReportTitle] = useState('')
  const [error, setError] = useState(null)
  const [downloading, setDownloading] = useState(false)

  const fetchDocs = useCallback(async () => {
    setLoadingDocs(true)
    try {
      const res = await getDocuments()
      const data = res.data
      const docs = Array.isArray(data) ? data : (data?.documents || [])
      setDocuments(docs)
      const docId = d => d.id || d.document_id
      setSelectedIds(docs.map(docId))
    } catch (e) {
      setError('Failed to load documents.')
    } finally {
      setLoadingDocs(false)
    }
  }, [])

  useEffect(() => { fetchDocs() }, [fetchDocs])

  const toggleAll = () => {
    const docId = d => d.id || d.document_id
    if (selectedIds.length === documents.length) setSelectedIds([])
    else setSelectedIds(documents.map(docId))
  }

  const toggleDoc = (id) => {
    setSelectedIds(prev => prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id])
  }

  const handleGenerate = async () => {
    if (selectedIds.length === 0) { setError('Please select at least one document.'); return }
    setGenerating(true)
    setError(null)
    setReportHtml(null)
    try {
      const res = await generateReport(selectedIds, 'mine_status_summary')
      const data = res.data
      setReportHtml(data.report_html || data.html || data.report || JSON.stringify(data, null, 2))
      setReportTitle(data.title || 'Mine Status Summary Report')
    } catch (e) {
      setError(e.response?.data?.detail || 'Report generation failed. Please try again.')
    } finally {
      setGenerating(false)
    }
  }

  const handleDownload = async () => {
    if (!reportHtml) return
    setDownloading(true)
    try {
      const res = await downloadReport(reportHtml, 'docx')
      const blob = new Blob([res.data], { type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = 'DocuMine_Report.docx'
      a.click()
      URL.revokeObjectURL(url)
    } catch (e) {
      setError('Download failed.')
    } finally {
      setDownloading(false)
    }
  }

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-800">📊 Automated Report Generation</h1>
        <p className="text-sm text-gray-500 mt-0.5">Generate Mine Status Summary Reports with AI-powered citations from ingested documents.</p>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 text-sm rounded-xl px-4 py-3 flex justify-between items-center">
          <span>{error}</span>
          <button onClick={() => setError(null)} className="text-red-400 hover:text-red-600 ml-4">✕</button>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left panel */}
        <div className="lg:col-span-1 space-y-4">
          <div className="bg-white rounded-xl shadow-md overflow-hidden">
            <div className="px-4 py-3 border-b border-gray-100 flex items-center justify-between">
              <span className="text-sm font-semibold text-gray-700">Select Documents</span>
              <span className="text-xs text-blue-600">{selectedIds.length}/{documents.length}</span>
            </div>
            <div className="px-4 py-2 border-b border-gray-50 flex gap-2">
              <button onClick={toggleAll} className="text-xs text-blue-600 hover:underline">
                {selectedIds.length === documents.length ? 'Deselect All' : 'Select All'}
              </button>
            </div>
            {loadingDocs ? (
              <div className="p-4 space-y-3">
                {[1,2,3].map(i => <div key={i} className="h-10 bg-gray-100 rounded animate-pulse" />)}
              </div>
            ) : documents.length === 0 ? (
              <div className="p-6 text-center text-sm text-gray-400">No documents ingested yet.</div>
            ) : (
              <ul className="divide-y divide-gray-50 max-h-64 overflow-y-auto">
                {documents.map(doc => {
                  const id = doc.id || doc.document_id
                  return (
                    <li key={id}>
                      <label className="flex items-center gap-3 px-4 py-3 hover:bg-blue-50 cursor-pointer">
                        <input
                          type="checkbox"
                          className="accent-blue-600"
                          checked={selectedIds.includes(id)}
                          onChange={() => toggleDoc(id)}
                        />
                        <div className="min-w-0">
                          <div className="text-sm text-gray-800 truncate">{doc.filename || id}</div>
                          <div className="text-xs text-gray-400">{(doc.doc_type || '').replace(/_/g, ' ')}</div>
                        </div>
                      </label>
                    </li>
                  )
                })}
              </ul>
            )}
          </div>

          {/* Report type */}
          <div className="bg-white rounded-xl shadow-md p-4 space-y-3">
            <div className="text-sm font-semibold text-gray-700">Report Type</div>
            <select className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm text-gray-800 focus:outline-none focus:ring-2 focus:ring-blue-400">
              <option value="mine_status_summary">Mine Status Summary Report</option>
            </select>

            {role === 'viewer' ? (
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg px-3 py-2 text-xs text-yellow-700">
                ⚠️ Report generation requires Admin role.
              </div>
            ) : (
              <button
                onClick={handleGenerate}
                disabled={generating || selectedIds.length === 0}
                className="w-full flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white font-medium text-sm py-2.5 rounded-lg transition shadow"
              >
                {generating ? (
                  <>
                    <svg className="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"/>
                    </svg>
                    Generating…
                  </>
                ) : '📊 Generate Report'}
              </button>
            )}
          </div>
        </div>

        {/* Right: Report view */}
        <div className="lg:col-span-2">
          {generating && (
            <div className="bg-white rounded-xl shadow-md p-12 flex flex-col items-center justify-center gap-4">
              <svg className="animate-spin h-10 w-10 text-blue-600" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"/>
              </svg>
              <div className="text-gray-500 text-sm text-center">
                Generating report… This may take 10–15 seconds.
              </div>
            </div>
          )}

          {!generating && !reportHtml && (
            <div className="bg-white rounded-xl shadow-md p-12 text-center">
              <div className="text-5xl mb-3">📄</div>
              <div className="text-gray-400 text-sm">Select documents and click Generate Report to see the output here.</div>
            </div>
          )}

          {!generating && reportHtml && (
            <div className="bg-white rounded-xl shadow-md overflow-hidden">
              <div className="px-5 py-4 border-b border-gray-100 flex items-center justify-between flex-wrap gap-3">
                <div>
                  <h2 className="text-base font-semibold text-gray-800">{reportTitle || 'Mine Status Summary Report'}</h2>
                  <div className="text-xs text-gray-400 mt-0.5">Citations shown as <span className="citation-tag">[Doc]</span> — hover to see source</div>
                </div>
                <button
                  onClick={handleDownload}
                  disabled={downloading}
                  className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white text-sm font-medium px-4 py-2 rounded-lg shadow transition"
                >
                  {downloading ? '⏳ Downloading…' : '⬇️ Download as Word'}
                </button>
              </div>
              <div className="p-6 prose prose-sm max-w-none text-gray-700 leading-relaxed overflow-y-auto max-h-[70vh]">
                {renderHtmlWithCitations(reportHtml)}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

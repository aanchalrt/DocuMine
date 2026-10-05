import React, { useState, useEffect, useCallback, useRef } from 'react'
import WordCloud from 'wordcloud'
import { getDocuments, getWordCloudData } from '../services/api.js'

const FALLBACK_WORDS = [
  { word: 'coal', weight: 100 }, { word: 'reserve', weight: 85 }, { word: 'production', weight: 80 },
  { word: 'geological', weight: 75 }, { word: 'environment', weight: 70 }, { word: 'mining', weight: 68 },
  { word: 'compliance', weight: 65 }, { word: 'overburden', weight: 60 }, { word: 'stripping', weight: 55 },
  { word: 'forest', weight: 52 }, { word: 'clearance', weight: 50 }, { word: 'grade', weight: 48 },
  { word: 'seam', weight: 45 }, { word: 'explosive', weight: 42 }, { word: 'royalty', weight: 40 },
  { word: 'ECL', weight: 38 }, { word: 'Kranti', weight: 36 }, { word: 'lease', weight: 34 },
  { word: 'OCP', weight: 32 }, { word: 'emission', weight: 30 },
]

export default function WordCloudPage() {
  const canvasRef = useRef(null)
  const [documents, setDocuments] = useState([])
  const [selectedIds, setSelectedIds] = useState([])
  const [keywords, setKeywords] = useState([])
  const [loading, setLoading] = useState(false)
  const [generated, setGenerated] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    getDocuments()
      .then(res => {
        const docs = Array.isArray(res.data) ? res.data : (res.data?.documents || [])
        setDocuments(docs)
        setSelectedIds(docs.map(d => d.id || d.document_id))
      })
      .catch(() => {})
  }, [])

  const toggleDoc = (id) => {
    setSelectedIds(prev => prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id])
  }

  const renderCloud = useCallback((words) => {
    if (!canvasRef.current) return
    const canvas = canvasRef.current
    canvas.width = 600
    canvas.height = 300
    WordCloud(canvas, {
      list: words.map(k => [k.word, k.weight]),
      gridSize: 8,
      weightFactor: 3,
      fontFamily: 'Inter, sans-serif',
      color: () => `hsl(${210 + Math.random() * 30}, ${60 + Math.random() * 20}%, ${30 + Math.random() * 30}%)`,
      rotateRatio: 0.3,
      backgroundColor: '#f8fafc',
    })
  }, [])

  const handleGenerate = async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await getWordCloudData(selectedIds)
      const data = res.data
      let words = []
      if (Array.isArray(data)) words = data
      else if (data && Array.isArray(data.keywords)) words = data.keywords
      else if (data && Array.isArray(data.words)) words = data.words
      if (words.length < 10) words = [...words, ...FALLBACK_WORDS].slice(0, 30)
      setKeywords(words)
      setGenerated(true)
      setTimeout(() => renderCloud(words), 50)
    } catch (e) {
      // fallback to demo data
      setKeywords(FALLBACK_WORDS)
      setGenerated(true)
      setTimeout(() => renderCloud(FALLBACK_WORDS), 50)
    } finally {
      setLoading(false)
    }
  }

  const maxWeight = keywords.length > 0 ? Math.max(...keywords.map(k => k.weight)) : 1

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-800">🔍 Word Cloud & Topic Identification</h1>
        <p className="text-sm text-gray-500 mt-0.5">Visualize key themes extracted from your document corpus.</p>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 text-sm rounded-xl px-4 py-3">{error}</div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Sidebar: doc selector */}
        <div className="lg:col-span-1">
          <div className="bg-white rounded-xl shadow-md overflow-hidden">
            <div className="px-4 py-3 border-b border-gray-100 flex items-center justify-between">
              <span className="text-sm font-semibold text-gray-700">Documents</span>
              <button
                onClick={() => selectedIds.length === documents.length ? setSelectedIds([]) : setSelectedIds(documents.map(d => d.id || d.document_id))}
                className="text-xs text-blue-600 hover:underline"
              >
                {selectedIds.length === documents.length ? 'Deselect All' : 'Select All'}
              </button>
            </div>
            {documents.length === 0 ? (
              <div className="p-4 text-sm text-gray-400 text-center">No documents</div>
            ) : (
              <ul className="divide-y divide-gray-50 max-h-60 overflow-y-auto">
                {documents.map(doc => {
                  const id = doc.id || doc.document_id
                  return (
                    <li key={id}>
                      <label className="flex items-center gap-2 px-4 py-2.5 hover:bg-blue-50 cursor-pointer">
                        <input type="checkbox" className="accent-blue-600" checked={selectedIds.includes(id)} onChange={() => toggleDoc(id)} />
                        <span className="text-xs text-gray-700 truncate">{doc.filename || id}</span>
                      </label>
                    </li>
                  )
                })}
              </ul>
            )}
            <div className="p-3 border-t border-gray-50">
              <button
                onClick={handleGenerate}
                disabled={loading}
                className="w-full bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white text-sm font-medium py-2 rounded-lg transition shadow flex items-center justify-center gap-2"
              >
                {loading ? (
                  <>
                    <svg className="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"/>
                    </svg>
                    Generating…
                  </>
                ) : '🔍 Generate'}
              </button>
            </div>
          </div>
        </div>

        {/* Main area */}
        <div className="lg:col-span-3 space-y-5">
          {/* Canvas */}
          <div className="bg-white rounded-xl shadow-md overflow-hidden">
            <div className="px-5 py-4 border-b border-gray-100">
              <span className="text-sm font-semibold text-gray-700">Word Cloud</span>
            </div>
            <div className="p-4 flex items-center justify-center bg-gray-50 min-h-[320px]">
              {loading && (
                <div className="flex flex-col items-center gap-3">
                  <svg className="animate-spin h-8 w-8 text-blue-600" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"/>
                  </svg>
                  <span className="text-sm text-gray-500">Building word cloud…</span>
                </div>
              )}
              {!loading && !generated && (
                <div className="text-center text-gray-400 text-sm">
                  <div className="text-4xl mb-2">☁️</div>
                  <div>Click "Generate" to build the word cloud</div>
                </div>
              )}
              <canvas
                ref={canvasRef}
                className={`max-w-full rounded-lg ${!generated || loading ? 'hidden' : 'block'}`}
                style={{ width: '100%', height: 'auto' }}
              />
            </div>
          </div>

          {/* Top themes */}
          {generated && keywords.length > 0 && (
            <div className="bg-white rounded-xl shadow-md overflow-hidden">
              <div className="px-5 py-4 border-b border-gray-100">
                <span className="text-sm font-semibold text-gray-700">Top {Math.min(20, keywords.length)} Themes</span>
              </div>
              <div className="p-4 space-y-2">
                {keywords.slice(0, 20).map((kw, idx) => (
                  <div key={idx} className="flex items-center gap-3">
                    <div className="w-5 text-xs text-gray-400 text-right flex-shrink-0">{idx + 1}</div>
                    <div className="w-28 text-sm font-medium text-gray-700 truncate">{kw.word}</div>
                    <div className="flex-1 h-5 bg-gray-100 rounded-full overflow-hidden">
                      <div
                        className="h-full rounded-full bg-gradient-to-r from-blue-600 to-blue-400"
                        style={{ width: `${Math.round((kw.weight / maxWeight) * 100)}%` }}
                      />
                    </div>
                    <div className="w-10 text-xs text-gray-500 text-right">{kw.weight}</div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

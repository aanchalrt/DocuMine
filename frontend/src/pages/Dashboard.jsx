import React, { useState, useEffect, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { getDocuments, getNeedsReview, getConflicts, getAuditLog } from '../services/api.js'

const MODULE_CARDS = [
  {
    path: '/ingest',
    icon: '📄',
    title: 'Smart Ingestion',
    desc: 'Upload and extract structured fields from PDFs, DOCX, XLSX, and images using AI-powered OCR and NLP.',
    color: 'blue',
  },
  {
    path: '/reports',
    icon: '📊',
    title: 'Report Generation',
    desc: 'Auto-generate Mine Status Summary Reports with citations from ingested documents.',
    color: 'indigo',
  },
  {
    path: '/wordcloud',
    icon: '🔍',
    title: 'Word Cloud & Topics',
    desc: 'Visualize key themes and ranked terminology extracted from your document corpus.',
    color: 'cyan',
  },
  {
    path: '/chat',
    icon: '💬',
    title: 'AI Chat Interface',
    desc: 'Query documents in natural language (English & Hindi) with cited, traceable AI responses.',
    color: 'violet',
  },
  {
    path: '/validation',
    icon: '⚠️',
    title: 'Conflict Detection',
    desc: 'Cross-validate data across documents to detect variance, method changes, and sum mismatches.',
    color: 'amber',
  },
  {
    path: '/audit',
    icon: '📋',
    title: 'Audit & Traceability',
    desc: 'Full role-based audit log of all actions: uploads, queries, report generations, and approvals.',
    color: 'gray',
  },
  {
    path: '/clearance',
    icon: '🌿',
    title: 'Clearance Tracker',
    desc: 'Track land & forest clearance lifecycle, detect bottlenecks, and monitor correspondence timelines.',
    color: 'green',
  },
]

const colorMap = {
  blue: 'bg-blue-50 border-blue-200 hover:border-blue-400',
  indigo: 'bg-indigo-50 border-indigo-200 hover:border-indigo-400',
  cyan: 'bg-cyan-50 border-cyan-200 hover:border-cyan-400',
  violet: 'bg-violet-50 border-violet-200 hover:border-violet-400',
  amber: 'bg-amber-50 border-amber-200 hover:border-amber-400',
  gray: 'bg-gray-50 border-gray-200 hover:border-gray-400',
  green: 'bg-green-50 border-green-200 hover:border-green-400',
}

function StatCard({ icon, label, value, loading, colorClass, bgClass }) {
  return (
    <div className={`rounded-xl shadow-md p-5 flex items-center gap-4 border ${bgClass}`}>
      <div className={`text-3xl w-12 h-12 flex items-center justify-center rounded-full bg-white shadow-sm`}>
        {icon}
      </div>
      <div className="flex-1 min-w-0">
        <div className="text-xs font-semibold uppercase tracking-wider text-gray-500 mb-1">{label}</div>
        {loading ? (
          <div className="h-7 w-16 bg-gray-200 rounded animate-pulse" />
        ) : (
          <div className={`text-3xl font-bold ${colorClass}`}>{value}</div>
        )}
      </div>
    </div>
  )
}

export default function Dashboard() {
  const navigate = useNavigate()
  const [stats, setStats] = useState({ docs: null, review: null, conflicts: null, audit: null })
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const fetchStats = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const [docsRes, reviewRes, conflictsRes, auditRes] = await Promise.allSettled([
        getDocuments(),
        getNeedsReview(),
        getConflicts(),
        getAuditLog(),
      ])

      const safeLen = (res) => {
        if (res.status === 'fulfilled') {
          const d = res.value.data
          if (Array.isArray(d)) return d.length
          if (d && typeof d === 'object') {
            if (typeof d.total === 'number') return d.total
            if (Array.isArray(d.documents)) return d.documents.length
            if (Array.isArray(d.conflicts)) return d.conflicts.length
            if (Array.isArray(d.entries)) return d.entries.length
            if (Array.isArray(d.fields)) return d.fields.length
            const k = Object.keys(d)[0]
            if (Array.isArray(d[k])) return d[k].length
          }
        }
        return '—'
      }

      setStats({
        docs: safeLen(docsRes),
        review: safeLen(reviewRes),
        conflicts: safeLen(conflictsRes),
        audit: safeLen(auditRes),
      })
    } catch (e) {
      setError('Failed to load statistics. Backend may not be running.')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { fetchStats() }, [fetchStats])

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      {/* Hero header */}
      <div className="bg-gradient-to-r from-blue-700 to-blue-900 rounded-2xl p-8 text-white shadow-xl">
        <div className="flex items-center gap-3 mb-2">
          <div className="w-10 h-10 bg-white rounded-xl flex items-center justify-center shadow">
            <svg viewBox="0 0 24 24" className="w-6 h-6 text-blue-700" fill="currentColor">
              <path d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4z"/>
            </svg>
          </div>
          <h1 className="text-3xl font-bold tracking-tight">DocuMine</h1>
        </div>
        <p className="text-blue-100 text-base mb-3">AI-Powered Document Intelligence Platform</p>
        <div className="inline-flex items-center gap-2 bg-blue-600 bg-opacity-50 rounded-lg px-4 py-2 text-sm font-medium border border-blue-400">
          <span>⛏️</span>
          <span>Kranti Opencast Project (OCP) — Eastern Coalfields Limited (ECL)</span>
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-4 flex items-center justify-between">
          <span className="text-red-700 text-sm">{error}</span>
          <button
            onClick={fetchStats}
            className="ml-4 text-sm bg-red-600 text-white px-4 py-1.5 rounded-lg hover:bg-red-700 transition"
          >
            Retry
          </button>
        </div>
      )}

      {/* Stat cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          icon="📄" label="Documents Ingested"
          value={stats.docs} loading={loading}
          colorClass="text-blue-700" bgClass="bg-blue-50 border border-blue-200"
        />
        <StatCard
          icon="🔶" label="Fields Needing Review"
          value={stats.review} loading={loading}
          colorClass="text-orange-600" bgClass="bg-orange-50 border border-orange-200"
        />
        <StatCard
          icon="⚠️" label="Conflicts Detected"
          value={stats.conflicts} loading={loading}
          colorClass="text-red-600" bgClass="bg-red-50 border border-red-200"
        />
        <StatCard
          icon="📋" label="Audit Log Entries"
          value={stats.audit} loading={loading}
          colorClass="text-gray-700" bgClass="bg-gray-50 border border-gray-200"
        />
      </div>

      {/* Module quick-access */}
      <div>
        <h2 className="text-lg font-semibold text-gray-800 mb-4">Modules</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {MODULE_CARDS.map(m => (
            <button
              key={m.path}
              onClick={() => navigate(m.path)}
              className={`text-left rounded-xl border-2 p-5 transition-all duration-150 shadow-sm hover:shadow-md ${colorMap[m.color]}`}
            >
              <div className="text-2xl mb-2">{m.icon}</div>
              <div className="font-semibold text-gray-800 mb-1">{m.title}</div>
              <div className="text-sm text-gray-500 leading-relaxed">{m.desc}</div>
            </button>
          ))}
        </div>
      </div>

      {/* Footer note */}
      <div className="text-center text-xs text-gray-400 pb-4">
        DocuMine v1.0 · Built for Smart India Hackathon 2024 · Ministry of Coal
      </div>
    </div>
  )
}

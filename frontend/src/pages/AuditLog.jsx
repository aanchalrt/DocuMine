import React, { useState, useEffect, useCallback } from 'react'
import { getAuditLog } from '../services/api.js'
import { useRole } from '../App.jsx'

const ACTION_STYLES = {
  document_uploaded: { badge: 'bg-green-100 text-green-800 border-green-300', label: 'Uploaded' },
  report_generated: { badge: 'bg-blue-100 text-blue-800 border-blue-300', label: 'Report' },
  query_asked: { badge: 'bg-purple-100 text-purple-800 border-purple-300', label: 'Query' },
  conflict_flagged: { badge: 'bg-red-100 text-red-800 border-red-300', label: 'Conflict' },
  conflict_approved: { badge: 'bg-teal-100 text-teal-800 border-teal-300', label: 'Approved' },
  seed_triggered: { badge: 'bg-amber-100 text-amber-800 border-amber-300', label: 'Seed' },
  validation_run: { badge: 'bg-indigo-100 text-indigo-800 border-indigo-300', label: 'Validation' },
}

const ALL_ACTIONS = ['all', ...Object.keys(ACTION_STYLES)]

function ActionBadge({ action }) {
  const style = ACTION_STYLES[action] || { badge: 'bg-gray-100 text-gray-700 border-gray-300', label: action }
  return (
    <span className={`text-xs font-medium px-2 py-0.5 rounded-full border ${style.badge}`}>
      {style.label}
    </span>
  )
}

function formatTimestamp(ts) {
  if (!ts) return '—'
  try {
    return new Date(ts).toLocaleString('en-IN', {
      day: '2-digit', month: 'short', year: 'numeric',
      hour: '2-digit', minute: '2-digit', second: '2-digit',
    })
  } catch {
    return ts
  }
}

export default function AuditLog() {
  const { role } = useRole()
  const [logs, setLogs] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [filter, setFilter] = useState('all')

  const fetchLogs = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await getAuditLog()
      const data = res.data
      const list = Array.isArray(data) ? data : (data?.entries || data?.logs || data?.audit_log || [])
      // newest first
      list.sort((a, b) => new Date(b.timestamp || 0) - new Date(a.timestamp || 0))
      setLogs(list)
    } catch (e) {
      setError('Could not load audit log.')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { fetchLogs() }, [fetchLogs])

  const filtered = filter === 'all' ? logs : logs.filter(l => l.action === filter)

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div>
          <h1 className="text-2xl font-bold text-gray-800">📋 Audit & Traceability Log</h1>
          <p className="text-sm text-gray-500 mt-0.5">Complete tamper-evident audit trail of all actions in the system.</p>
        </div>
        <button
          onClick={fetchLogs}
          disabled={loading}
          className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-60 text-white text-sm font-medium px-4 py-2 rounded-lg shadow transition"
        >
          {loading ? (
            <><svg className="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"/></svg> Refreshing…</>
          ) : '🔄 Refresh'}
        </button>
      </div>

      {/* Role-based access note */}
      <div className="bg-blue-50 border border-blue-200 rounded-xl px-4 py-3 text-sm text-blue-800">
        <strong>Access Policy:</strong> Admin sees all log entries including system actions.
        Viewer has read-only access to document-level events only.
        {role === 'viewer' && ' You are currently in Viewer mode.'}
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 text-sm rounded-xl px-4 py-3">{error}</div>
      )}

      {/* Filter */}
      <div className="flex items-center gap-3 flex-wrap">
        <span className="text-sm text-gray-600 font-medium">Filter by action:</span>
        <select
          value={filter}
          onChange={e => setFilter(e.target.value)}
          className="border border-gray-200 rounded-lg px-3 py-1.5 text-sm text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-400"
        >
          {ALL_ACTIONS.map(a => (
            <option key={a} value={a}>{a === 'all' ? 'All Actions' : (ACTION_STYLES[a]?.label || a)}</option>
          ))}
        </select>
        <span className="text-xs text-gray-400">{filtered.length} entries</span>
      </div>

      {/* Table */}
      <div className="bg-white rounded-xl shadow-md overflow-hidden">
        {loading ? (
          <div className="p-8 space-y-3">
            {[1,2,3,4,5].map(i => <div key={i} className="h-10 bg-gray-100 rounded animate-pulse" />)}
          </div>
        ) : filtered.length === 0 ? (
          <div className="p-12 text-center">
            <div className="text-4xl mb-2">📋</div>
            <div className="text-sm text-gray-400">No audit log entries found.</div>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-gray-50 border-b border-gray-100">
                  <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">Timestamp</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">Action</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">User Role</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">Document</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">Details</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-50">
                {filtered.map((log, idx) => (
                  <tr key={log.log_id || idx} className="hover:bg-gray-50 transition">
                    <td className="px-4 py-3 text-xs text-gray-500 font-mono whitespace-nowrap">{formatTimestamp(log.timestamp)}</td>
                    <td className="px-4 py-3"><ActionBadge action={log.action} /></td>
                    <td className="px-4 py-3">
                      <span className={`text-xs px-2 py-0.5 rounded-full font-medium border
                        ${log.user_role === 'admin' ? 'bg-blue-100 text-blue-700 border-blue-300' : 'bg-gray-100 text-gray-600 border-gray-300'}`}>
                        {log.user_role || 'system'}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-xs text-gray-700 max-w-[180px] truncate" title={log.document_name}>
                      {log.document_name || '—'}
                    </td>
                    <td className="px-4 py-3 text-xs text-gray-500 max-w-[260px]">
                      <span className="truncate block" title={log.details}>{log.details || '—'}</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}

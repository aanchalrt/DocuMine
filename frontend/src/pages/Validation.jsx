import React, { useState, useEffect, useCallback } from 'react'
import { getConflicts, runValidation, approveConflict } from '../services/api.js'
import { useRole } from '../App.jsx'

const SEVERITY_STYLES = {
  HIGH: { badge: 'bg-red-100 text-red-800 border-red-300', border: 'conflict-high', label: 'HIGH' },
  MEDIUM: { badge: 'bg-amber-100 text-amber-800 border-amber-300', border: 'conflict-medium', label: 'MED' },
  LOW: { badge: 'bg-blue-100 text-blue-700 border-blue-300', border: 'conflict-low', label: 'LOW' },
}

const CONFLICT_TYPE_LABELS = {
  unexplained_variance: 'Unexplained Variance',
  method_change: 'Method Change',
  sum_mismatch: 'Sum Mismatch',
  low_confidence: 'Low Confidence',
}

function ConflictCard({ conflict, onApprove, isAdmin }) {
  const sev = SEVERITY_STYLES[conflict.severity?.toUpperCase()] || SEVERITY_STYLES.LOW
  const [approving, setApproving] = useState(false)
  const [approved, setApproved] = useState(false)

  const handleApprove = async () => {
    setApproving(true)
    try {
      await onApprove(conflict.id || conflict.conflict_id)
      setApproved(true)
    } catch (e) {
      alert('Approval failed.')
    } finally {
      setApproving(false)
    }
  }

  if (approved) {
    return (
      <div className="bg-green-50 border border-green-200 rounded-xl p-4 flex items-center gap-3">
        <span className="text-green-600 text-xl">✅</span>
        <span className="text-sm text-green-700 font-medium">Conflict "{conflict.parameter}" approved and dismissed.</span>
      </div>
    )
  }

  return (
    <div className={`bg-white rounded-xl shadow-sm border-l-4 overflow-hidden ${sev.border}`}>
      <div className="p-5">
        {/* Header */}
        <div className="flex items-start justify-between flex-wrap gap-3 mb-4">
          <div>
            <h3 className="text-sm font-bold text-gray-800 font-mono">{conflict.parameter}</h3>
            <div className="flex items-center gap-2 mt-1.5 flex-wrap">
              <span className={`text-xs font-semibold px-2 py-0.5 rounded-full border ${sev.badge}`}>
                {conflict.severity?.toUpperCase()}
              </span>
              <span className="text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded-full border border-gray-200">
                {CONFLICT_TYPE_LABELS[conflict.conflict_type] || conflict.conflict_type}
              </span>
            </div>
          </div>
          {isAdmin && (
            <button
              onClick={handleApprove}
              disabled={approving}
              className="text-xs bg-green-600 hover:bg-green-700 disabled:opacity-50 text-white px-3 py-1.5 rounded-lg shadow transition font-medium"
            >
              {approving ? '⏳ Approving…' : '✅ Approve'}
            </button>
          )}
        </div>

        {/* Side-by-side comparison */}
        {(() => {
          const vals = conflict.values || conflict.conflicting_values || []
          if (!vals || vals.length < 2) return null
          return (
            <div className="grid grid-cols-2 gap-3 mb-4">
              {vals.slice(0, 2).map((v, idx) => (
                <div key={idx} className={`rounded-lg p-3 border ${idx === 0 ? 'bg-red-50 border-red-200' : 'bg-blue-50 border-blue-200'}`}>
                  <div className="text-xs font-semibold text-gray-500 truncate mb-1">{v.doc_name || v.source_document || `Source ${idx + 1}`}</div>
                  <div className="text-lg font-bold text-gray-800">{String(v.value ?? '—')}</div>
                  {v.unit && <div className="text-xs text-gray-500">{v.unit}</div>}
                  {v.date && <div className="text-xs text-gray-400 mt-1">{v.date}</div>}
                </div>
              ))}
            </div>
          )
        })()}

        {/* Note */}
        {conflict.note && (
          <div className="bg-gray-50 border border-gray-200 rounded-lg px-3 py-2">
            <div className="text-xs font-semibold text-gray-500 mb-0.5">Note</div>
            <div className="text-sm text-gray-700">{conflict.note}</div>
          </div>
        )}
      </div>
    </div>
  )
}

export default function Validation() {
  const { role } = useRole()
  const [conflicts, setConflicts] = useState([])
  const [loading, setLoading] = useState(false)
  const [running, setRunning] = useState(false)
  const [error, setError] = useState(null)

  const fetchConflicts = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await getConflicts()
      const data = res.data
      const list = Array.isArray(data) ? data : (data?.conflicts || [])
      // Sort HIGH first
      const order = { HIGH: 0, MEDIUM: 1, LOW: 2 }
      list.sort((a, b) => (order[a.severity?.toUpperCase()] ?? 3) - (order[b.severity?.toUpperCase()] ?? 3))
      setConflicts(list)
    } catch (e) {
      setError('Failed to load conflicts.')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { fetchConflicts() }, [fetchConflicts])

  const handleRunValidation = async () => {
    setRunning(true)
    setError(null)
    try {
      await runValidation()
      await fetchConflicts()
    } catch (e) {
      setError('Validation run failed.')
    } finally {
      setRunning(false)
    }
  }

  const handleApprove = async (conflictId) => {
    await approveConflict(conflictId)
  }

  const high = conflicts.filter(c => c.severity?.toUpperCase() === 'HIGH').length
  const medium = conflicts.filter(c => c.severity?.toUpperCase() === 'MEDIUM').length
  const low = conflicts.filter(c => c.severity?.toUpperCase() === 'LOW').length

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div>
          <h1 className="text-2xl font-bold text-gray-800">⚠️ Cross-Document Validation</h1>
          <p className="text-sm text-gray-500 mt-0.5">Detect data conflicts, variance, and inconsistencies across ingested documents.</p>
        </div>
        <button
          onClick={handleRunValidation}
          disabled={running}
          className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-60 text-white text-sm font-medium px-4 py-2 rounded-lg shadow transition"
        >
          {running ? (
            <><svg className="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"/></svg> Running…</>
          ) : '🔄 Run Validation'}
        </button>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 text-sm rounded-xl px-4 py-3">{error}</div>
      )}

      {/* Summary bar */}
      <div className="grid grid-cols-4 gap-4">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4 text-center">
          <div className="text-2xl font-bold text-gray-800">{conflicts.length}</div>
          <div className="text-xs text-gray-500 mt-0.5">Total</div>
        </div>
        <div className="bg-red-50 rounded-xl shadow-sm border border-red-200 p-4 text-center">
          <div className="text-2xl font-bold text-red-700">{high}</div>
          <div className="text-xs text-red-600 mt-0.5">High</div>
        </div>
        <div className="bg-amber-50 rounded-xl shadow-sm border border-amber-200 p-4 text-center">
          <div className="text-2xl font-bold text-amber-700">{medium}</div>
          <div className="text-xs text-amber-600 mt-0.5">Medium</div>
        </div>
        <div className="bg-blue-50 rounded-xl shadow-sm border border-blue-200 p-4 text-center">
          <div className="text-2xl font-bold text-blue-700">{low}</div>
          <div className="text-xs text-blue-600 mt-0.5">Low</div>
        </div>
      </div>

      {/* Role note */}
      {role === 'viewer' && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-xl px-4 py-3 text-sm text-yellow-800">
          👁️ You are in <strong>Viewer</strong> mode. The "Approve" button is only available to Admins.
        </div>
      )}

      {/* Conflict cards */}
      {loading ? (
        <div className="space-y-4">
          {[1,2,3].map(i => <div key={i} className="h-36 bg-gray-100 rounded-xl animate-pulse" />)}
        </div>
      ) : conflicts.length === 0 ? (
        <div className="bg-white rounded-xl shadow-md p-12 text-center">
          <div className="text-5xl mb-3">✅</div>
          <div className="text-gray-500 text-sm">No conflicts detected. All documents are consistent.</div>
        </div>
      ) : (
        <div className="space-y-4">
          {conflicts.map(c => (
            <ConflictCard
              key={c.conflict_id}
              conflict={c}
              onApprove={handleApprove}
              isAdmin={role === 'admin'}
            />
          ))}
        </div>
      )}
    </div>
  )
}

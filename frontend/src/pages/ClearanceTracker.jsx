import React, { useState, useEffect, useCallback } from 'react'
import { getClearanceTimeline } from '../services/api.js'

const STATUS_STYLES = {
  pending: { badge: 'bg-orange-100 text-orange-800 border-orange-300', dot: 'bg-orange-400', label: 'Pending' },
  resolved: { badge: 'bg-green-100 text-green-800 border-green-300', dot: 'bg-green-500', label: 'Resolved' },
  escalated: { badge: 'bg-red-100 text-red-800 border-red-300', dot: 'bg-red-500', label: 'Escalated' },
}

function StatusBadge({ status }) {
  const s = STATUS_STYLES[status?.toLowerCase()] || STATUS_STYLES.pending
  return (
    <span className={`text-xs font-medium px-2 py-0.5 rounded-full border ${s.badge}`}>{s.label}</span>
  )
}

function formatDate(d) {
  if (!d) return '—'
  try { return new Date(d).toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' }) }
  catch { return d }
}

function TimelineNode({ item, isBottleneck, isLast }) {
  const sStyle = STATUS_STYLES[item.status?.toLowerCase()] || STATUS_STYLES.pending
  return (
    <div className="flex items-start gap-0 flex-shrink-0">
      {/* Node card */}
      <div className={`w-52 rounded-xl border-2 p-3 shadow-sm bg-white flex-shrink-0
        ${isBottleneck ? 'bottleneck-pulse border-red-500' : 'border-gray-200'}`}>
        <div className="flex items-center gap-1.5 mb-2">
          <div className={`w-2 h-2 rounded-full ${sStyle.dot}`} />
          <StatusBadge status={item.status} />
          {isBottleneck && (
            <span className="text-xs bg-red-600 text-white rounded-full px-1.5 font-bold">!</span>
          )}
        </div>
        <div className="text-xs font-semibold text-gray-700 mb-1 truncate" title={item.sender_office || item.from_office}>
          {item.sender_office || item.from_office || 'Office'}
        </div>
        <div className="flex items-center gap-1 text-xs text-gray-400 mb-1">
          <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
          </svg>
          <span className="truncate font-medium text-gray-600" title={item.recipient_office || item.to_office}>{item.recipient_office || item.to_office}</span>
        </div>
        <div className="text-xs text-gray-400 mb-1">{formatDate(item.date)}</div>
        <div className="text-xs text-gray-600 leading-relaxed line-clamp-2" title={item.subject}>
          {item.subject}
        </div>
        {item.days_pending > 0 && (
          <div className={`mt-2 text-xs font-medium px-1.5 py-0.5 rounded inline-block
            ${item.days_pending > 60 ? 'bg-red-100 text-red-700' : item.days_pending > 30 ? 'bg-amber-100 text-amber-700' : 'bg-gray-100 text-gray-600'}`}>
            {item.days_pending}d pending
          </div>
        )}
      </div>

      {/* Arrow connector */}
      {!isLast && (
        <div className="flex items-center self-center px-1 flex-shrink-0">
          <div className="w-8 h-0.5 bg-gray-300" />
          <svg className="w-3 h-3 text-gray-400 -ml-1" fill="currentColor" viewBox="0 0 20 20">
            <path d="M10.293 3.293a1 1 0 011.414 0l6 6a1 1 0 010 1.414l-6 6a1 1 0 01-1.414-1.414L14.586 11H3a1 1 0 110-2h11.586l-4.293-4.293a1 1 0 010-1.414z" />
          </svg>
        </div>
      )}
    </div>
  )
}

export default function ClearanceTracker() {
  const [timeline, setTimeline] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const fetchTimeline = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await getClearanceTimeline()
      const data = res.data
      const list = Array.isArray(data) ? data : (data?.timeline || data?.correspondences || [])
      setTimeline(list)
    } catch (e) {
      setError('Could not load clearance timeline.')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { fetchTimeline() }, [fetchTimeline])

  // Find bottleneck: highest days_pending
  const bottleneckIdx = timeline.length > 0
    ? timeline.reduce((maxIdx, item, idx, arr) => (item.days_pending > arr[maxIdx].days_pending ? idx : maxIdx), 0)
    : -1

  const bottleneck = bottleneckIdx >= 0 ? timeline[bottleneckIdx] : null

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-800">🌿 Land & Clearance Lifecycle Tracker</h1>
        <p className="text-sm text-gray-500 mt-0.5">Land & Forest Clearance Lifecycle — Kranti OCP Expansion</p>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 text-sm rounded-xl px-4 py-3 flex justify-between">
          <span>{error}</span>
          <button onClick={fetchTimeline} className="text-red-600 underline ml-4 hover:text-red-800">Retry</button>
        </div>
      )}

      {/* Bottleneck alert */}
      {!loading && bottleneck && bottleneck.days_pending > 0 && (
        <div className="bg-red-50 border-l-4 border-red-600 rounded-xl px-5 py-4 flex items-start gap-3">
          <span className="text-red-600 text-xl mt-0.5">🚨</span>
          <div>
            <div className="text-sm font-bold text-red-800">Bottleneck Detected</div>
            <div className="text-sm text-red-700 mt-0.5">
              Correspondence from <strong>{bottleneck.sender_office || bottleneck.from_office}</strong> to <strong>{bottleneck.recipient_office || bottleneck.to_office}</strong> has been pending for <strong>{bottleneck.days_pending} days</strong>.
            </div>
            <div className="text-xs text-red-600 mt-1">Subject: {bottleneck.subject}</div>
          </div>
        </div>
      )}

      {/* Timeline */}
      <div className="bg-white rounded-2xl shadow-md overflow-hidden">
        <div className="px-5 py-4 border-b border-gray-100">
          <h2 className="text-sm font-semibold text-gray-700">Clearance Pipeline</h2>
        </div>

        {loading ? (
          <div className="p-8 flex items-center justify-center gap-3">
            <svg className="animate-spin h-7 w-7 text-blue-600" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"/>
            </svg>
            <span className="text-sm text-gray-500">Loading timeline…</span>
          </div>
        ) : timeline.length === 0 ? (
          <div className="p-12 text-center">
            <div className="text-4xl mb-2">🌿</div>
            <div className="text-sm text-gray-400">No clearance data available. Ensure seed data is loaded.</div>
          </div>
        ) : (
          <div className="p-5 overflow-x-auto">
            <div className="flex items-start gap-0 min-w-max pb-2">
              {timeline.map((item, idx) => (
                <TimelineNode
                  key={item.id || item.correspondence_id || idx}
                  item={item}
                  isBottleneck={item.is_bottleneck || idx === bottleneckIdx}
                  isLast={idx === timeline.length - 1}
                />
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Detail table */}
      {!loading && timeline.length > 0 && (
        <div className="bg-white rounded-2xl shadow-md overflow-hidden">
          <div className="px-5 py-4 border-b border-gray-100">
            <h2 className="text-sm font-semibold text-gray-700">Correspondence Details</h2>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-gray-50 border-b border-gray-100">
                  <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">#</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">From</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">To</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">Date</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">Subject</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">Status</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">Days Pending</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-50">
                {timeline.map((item, idx) => (
                  <tr key={item.id || item.correspondence_id || idx} className={`hover:bg-gray-50 ${item.is_bottleneck || idx === bottleneckIdx ? 'bg-red-50' : ''}`}>
                    <td className="px-4 py-3 text-xs text-gray-500">{idx + 1}</td>
                    <td className="px-4 py-3 text-xs text-gray-700 max-w-[140px] truncate" title={item.sender_office || item.from_office}>{item.sender_office || item.from_office || '—'}</td>
                    <td className="px-4 py-3 text-xs text-gray-700 max-w-[140px] truncate" title={item.recipient_office || item.to_office}>{item.recipient_office || item.to_office || '—'}</td>
                    <td className="px-4 py-3 text-xs text-gray-500 whitespace-nowrap">{formatDate(item.date)}</td>
                    <td className="px-4 py-3 text-xs text-gray-700 max-w-[220px] truncate" title={item.subject}>{item.subject || '—'}</td>
                    <td className="px-4 py-3"><StatusBadge status={item.status} /></td>
                    <td className="px-4 py-3">
                      <span className={`text-xs font-medium ${item.days_pending > 60 ? 'text-red-600 font-bold' : item.days_pending > 30 ? 'text-amber-600' : 'text-gray-500'}`}>
                        {item.days_pending > 0 ? `${item.days_pending}d` : '—'}
                      </span>
                      {(item.is_bottleneck || idx === bottleneckIdx) && item.days_pending > 0 && (
                        <span className="ml-2 text-xs bg-red-600 text-white rounded-full px-1.5 font-bold">⚠</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}

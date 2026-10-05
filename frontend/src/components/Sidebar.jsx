import React from 'react'
import { useNavigate, useLocation } from 'react-router-dom'

const NAV_ITEMS = [
  { path: '/',           icon: '🏠', label: 'Dashboard' },
  { path: '/ingest',     icon: '📄', label: 'Ingestion' },
  { path: '/reports',    icon: '📊', label: 'Reports' },
  { path: '/wordcloud',  icon: '🔍', label: 'Word Cloud' },
  { path: '/chat',       icon: '💬', label: 'AI Chat' },
  { path: '/validation', icon: '⚠️', label: 'Validation' },
  { path: '/audit',      icon: '📋', label: 'Audit Log' },
  { path: '/clearance',  icon: '🌿', label: 'Clearance' },
]

export default function Sidebar({ currentRole, onRoleChange }) {
  const navigate = useNavigate()
  const location = useLocation()

  return (
    <aside className="w-16 md:w-60 bg-blue-800 flex flex-col h-full flex-shrink-0 shadow-xl">
      {/* Logo */}
      <div className="px-3 md:px-4 py-5 border-b border-blue-700">
        <div className="flex items-center gap-2">
          <div className="flex-shrink-0 w-8 h-8 bg-white rounded-lg flex items-center justify-center shadow">
            <svg viewBox="0 0 24 24" className="w-5 h-5 text-blue-700" fill="currentColor">
              <path d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4z"/>
            </svg>
          </div>
          <div className="hidden md:block">
            <div className="text-white font-bold text-lg leading-tight">DocuMine</div>
            <div className="text-blue-300 text-xs leading-tight">AI Doc Intelligence</div>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 py-4 overflow-y-auto">
        <ul className="space-y-1 px-2">
          {NAV_ITEMS.map(item => {
            const isActive = location.pathname === item.path
            return (
              <li key={item.path}>
                <button
                  onClick={() => navigate(item.path)}
                  className={`w-full flex items-center gap-3 px-2 py-2.5 rounded-lg text-sm font-medium transition-all duration-150
                    ${isActive
                      ? 'bg-blue-600 text-white shadow-md'
                      : 'text-blue-200 hover:bg-blue-700 hover:text-white'
                    }`}
                >
                  <span className="text-base flex-shrink-0 w-6 text-center">{item.icon}</span>
                  <span className="hidden md:block truncate">{item.label}</span>
                </button>
              </li>
            )
          })}
        </ul>
      </nav>

      {/* Role Selector */}
      <div className="px-3 py-4 border-t border-blue-700">
        <div className="hidden md:block text-blue-300 text-xs font-semibold uppercase tracking-wider mb-2">
          Access Role
        </div>
        <div className="flex items-center gap-2">
          <span className="text-blue-300 text-base flex-shrink-0 md:hidden">👤</span>
          <select
            value={currentRole}
            onChange={e => onRoleChange(e.target.value)}
            className="hidden md:block w-full bg-blue-700 text-white text-sm rounded-lg px-3 py-2 border border-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-400 cursor-pointer"
          >
            <option value="admin">Admin</option>
            <option value="viewer">Viewer</option>
          </select>
        </div>
        <div className="hidden md:block mt-2 text-xs text-blue-400">
          {currentRole === 'admin' ? '✅ Full Access' : '👁️ Read-Only'}
        </div>
      </div>
    </aside>
  )
}

import React, { useState, useEffect, createContext, useContext } from 'react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Sidebar from './components/Sidebar.jsx'
import Dashboard from './pages/Dashboard.jsx'
import Ingestion from './pages/Ingestion.jsx'
import Reports from './pages/Reports.jsx'
import WordCloud from './pages/WordCloud.jsx'
import Chat from './pages/Chat.jsx'
import Validation from './pages/Validation.jsx'
import AuditLog from './pages/AuditLog.jsx'
import ClearanceTracker from './pages/ClearanceTracker.jsx'
import { healthCheck, triggerSeedIngestion } from './services/api.js'

export const RoleContext = createContext({ role: 'admin', setRole: () => {} })
export const useRole = () => useContext(RoleContext)

export default function App() {
  const [role, setRole] = useState('admin')
  const [backendStatus, setBackendStatus] = useState('checking') // 'ok' | 'error' | 'checking'

  useEffect(() => {
    const init = async () => {
      try {
        await healthCheck()
        setBackendStatus('ok')
        try {
          await triggerSeedIngestion()
        } catch (_) {
          // seed may already exist, ignore error
        }
      } catch (_) {
        setBackendStatus('error')
      }
    }
    init()
  }, [])

  return (
    <RoleContext.Provider value={{ role, setRole }}>
      <BrowserRouter>
        <div className="flex h-screen overflow-hidden bg-gray-50">
          <Sidebar currentRole={role} onRoleChange={setRole} />
          <div className="flex-1 flex flex-col overflow-hidden">
            {backendStatus === 'error' && (
              <div className="bg-red-600 text-white text-sm px-4 py-2 flex items-center gap-2">
                <span>⚠️</span>
                <span>Backend not reachable at localhost:8080. Running in demo mode.</span>
              </div>
            )}
            {backendStatus === 'checking' && (
              <div className="bg-blue-600 text-white text-sm px-4 py-2 flex items-center gap-2">
                <span className="animate-pulse">●</span>
                <span>Connecting to backend…</span>
              </div>
            )}
            <main className="flex-1 overflow-y-auto p-6">
              <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/ingest" element={<Ingestion />} />
                <Route path="/reports" element={<Reports />} />
                <Route path="/wordcloud" element={<WordCloud />} />
                <Route path="/chat" element={<Chat />} />
                <Route path="/validation" element={<Validation />} />
                <Route path="/audit" element={<AuditLog />} />
                <Route path="/clearance" element={<ClearanceTracker />} />
              </Routes>
            </main>
          </div>
        </div>
      </BrowserRouter>
    </RoleContext.Provider>
  )
}

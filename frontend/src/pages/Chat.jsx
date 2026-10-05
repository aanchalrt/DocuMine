import React, { useState, useEffect, useRef, useCallback } from 'react'
import { sendChatQuery } from '../services/api.js'

const QUICK_QUESTIONS = [
  'What is the coal reserve of Kranti OCP?',
  'What is the coal grade classification?',
  'What are the environmental compliance parameters?',
  'कोयला उत्पादन कितना है?',
  'What are the detected conflicts?',
]

function detectLanguage(text) {
  return /[\u0900-\u097F]/.test(text) ? 'हिं' : 'EN'
}

function TypingIndicator() {
  return (
    <div className="flex items-end gap-2 mb-4">
      <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center text-sm flex-shrink-0">🤖</div>
      <div className="bg-white border border-gray-200 rounded-2xl rounded-bl-sm px-4 py-3 shadow-sm">
        <div className="flex gap-1 items-center h-4">
          {[0,1,2].map(i => (
            <div
              key={i}
              className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
              style={{ animationDelay: `${i * 0.15}s` }}
            />
          ))}
        </div>
      </div>
    </div>
  )
}

function CitationTags({ citations }) {
  if (!citations || !Array.isArray(citations) || citations.length === 0) return null
  return (
    <div className="flex flex-wrap gap-1 mt-2">
      {citations.map((c, i) => {
        const docLabel = (typeof c === 'object' && c !== null)
          ? (c.doc_id || c.document || c.field || 'Source')
          : String(c)
        const tooltip = (typeof c === 'object' && c !== null)
          ? (c.field ? `${c.doc_id || c.document || 'Doc'}: ${c.field}` : (c.doc_id || c.document || 'Source'))
          : String(c)
        return (
          <span key={i} className="citation-tag" title={tooltip}>
            [{docLabel}]
          </span>
        )
      })}
    </div>
  )
}

export default function Chat() {
  const [messages, setMessages] = useState([
    {
      id: 0,
      role: 'assistant',
      text: 'Hello! I\'m DocuMine AI. Ask me anything about the Kranti OCP documents — coal reserves, production, compliance, or clearance status. You can also ask in Hindi (हिंदी).',
      citations: [],
      lang: 'EN',
    }
  ])
  const [input, setInput] = useState('')
  const [typing, setTyping] = useState(false)
  const [lastInteractionId, setLastInteractionId] = useState(null)
  const bottomRef = useRef(null)
  const inputRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, typing])

  const sendMessage = useCallback(async (question) => {
    if (!question.trim()) return
    const lang = detectLanguage(question)
    const userMsg = { id: Date.now(), role: 'user', text: question, lang }
    setMessages(prev => [...prev, userMsg])
    setInput('')
    setTyping(true)

    try {
      const res = await sendChatQuery(question, lastInteractionId)
      const data = res.data
      const answerText = data.answer || data.response || data.text || JSON.stringify(data)
      const citations = data.citations || data.sources || []
      const interactionId = data.interaction_id || data.id || null
      setLastInteractionId(interactionId)

      const aiMsg = {
        id: Date.now() + 1,
        role: 'assistant',
        text: answerText,
        citations,
        lang: detectLanguage(answerText),
      }
      setMessages(prev => [...prev, aiMsg])
    } catch (e) {
      const errMsg = {
        id: Date.now() + 1,
        role: 'assistant',
        text: 'Sorry, I could not process your query. Please ensure the backend is running and try again.',
        citations: [],
        lang: 'EN',
      }
      setMessages(prev => [...prev, errMsg])
    } finally {
      setTyping(false)
    }
  }, [lastInteractionId])

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage(input)
    }
  }

  return (
    <div className="max-w-4xl mx-auto flex flex-col h-full" style={{ minHeight: 'calc(100vh - 120px)' }}>
      {/* Header */}
      <div className="mb-4">
        <h1 className="text-2xl font-bold text-gray-800">💬 AI Query & Response System</h1>
        <p className="text-sm text-gray-500 mt-0.5">Ask questions in English or Hindi. All answers are cited from ingested documents.</p>
      </div>

      {/* Quick questions */}
      <div className="flex flex-wrap gap-2 mb-4">
        {QUICK_QUESTIONS.map((q, i) => (
          <button
            key={i}
            onClick={() => sendMessage(q)}
            disabled={typing}
            className="text-xs bg-blue-50 hover:bg-blue-100 text-blue-700 border border-blue-200 rounded-full px-3 py-1.5 transition disabled:opacity-50"
          >
            {q}
          </button>
        ))}
      </div>

      {/* Chat area */}
      <div className="flex-1 bg-white rounded-2xl shadow-md overflow-hidden flex flex-col">
        <div className="flex-1 overflow-y-auto p-5 space-y-1">
          {messages.map(msg => (
            <div key={msg.id} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'} mb-3`}>
              {msg.role === 'assistant' && (
                <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center text-sm flex-shrink-0 mr-2 mt-0.5">🤖</div>
              )}
              <div className={`max-w-[75%] ${msg.role === 'user' ? 'order-2' : ''}`}>
                <div className={`rounded-2xl px-4 py-3 text-sm leading-relaxed shadow-sm
                  ${msg.role === 'user'
                    ? 'bg-blue-600 text-white rounded-br-sm'
                    : 'bg-white border border-gray-200 text-gray-800 rounded-bl-sm'
                  }`}
                >
                  <div className="whitespace-pre-wrap">{msg.text}</div>
                  {msg.role === 'assistant' && <CitationTags citations={msg.citations} />}
                </div>
                <div className={`flex items-center gap-2 mt-1 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <span className={`text-xs px-1.5 py-0.5 rounded font-medium
                    ${msg.lang === 'हिं' ? 'bg-orange-100 text-orange-700' : 'bg-gray-100 text-gray-500'}`}>
                    {msg.lang}
                  </span>
                </div>
              </div>
              {msg.role === 'user' && (
                <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center text-sm flex-shrink-0 ml-2 mt-0.5 text-white">👤</div>
              )}
            </div>
          ))}
          {typing && <TypingIndicator />}
          <div ref={bottomRef} />
        </div>

        {/* Input bar */}
        <div className="border-t border-gray-100 p-4">
          <div className="flex gap-3">
            <textarea
              ref={inputRef}
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask anything about Kranti OCP documents… (Enter to send)"
              disabled={typing}
              rows={1}
              className="flex-1 border border-gray-200 rounded-xl px-4 py-2.5 text-sm text-gray-800 resize-none focus:outline-none focus:ring-2 focus:ring-blue-400 disabled:opacity-50"
              style={{ maxHeight: '100px', overflowY: 'auto' }}
            />
            <button
              onClick={() => sendMessage(input)}
              disabled={typing || !input.trim()}
              className="flex-shrink-0 w-11 h-11 bg-blue-600 hover:bg-blue-700 disabled:opacity-40 text-white rounded-xl flex items-center justify-center shadow transition"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
              </svg>
            </button>
          </div>
          <div className="text-xs text-gray-400 mt-1 ml-1">Press Enter to send · Shift+Enter for new line</div>
        </div>
      </div>
    </div>
  )
}

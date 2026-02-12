
import { useState, useEffect, useRef } from 'react'
import { Send, Upload, User, Bot, Sparkles, Terminal } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import axios from 'axios'
import clsx from 'clsx'

const API_URL = import.meta.env.DEV ? 'http://localhost:8000/chat' : '/api/chat';

function App() {
  const [input, setInput] = useState('')
  const [messages, setMessages] = useState([
    { role: 'assistant', content: 'Olá Fabrício! Sou o Agente NEXUS. Estou conectado e pronto para criar.' }
  ])
  const [isLoading, setIsLoading] = useState(false)
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!input.trim() || isLoading) return

    const userMsg = { role: 'user', content: input }
    setMessages(prev => [...prev, userMsg])
    setInput('')
    setIsLoading(true)

    try {
      const response = await axios.post(API_URL, {
        messages: [...messages, userMsg].map(m => ({
          role: m.role,
          content: m.content
        }))
      })

      const botMsg = { role: 'assistant', content: response.data.reply }
      setMessages(prev => [...prev, botMsg])
    } catch (error) {
      console.error(error)
      setMessages(prev => [...prev, { role: 'assistant', content: '⚠️ Erro ao conectar com o servidor.' }])
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="flex h-screen bg-nexus-900 text-slate-200 font-sans selection:bg-nexus-500/30">

      {/* Sidebar (Menu Simples) */}
      <aside className="w-20 lg:w-64 border-r border-white/5 bg-nexus-800/50 hidden md:flex flex-col">
        <div className="h-16 flex items-center justify-center lg:justify-start lg:px-6 border-b border-white/5">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-violet-500 to-fuchsia-600 flex items-center justify-center shadow-lg shadow-violet-500/20">
            <Sparkles className="w-5 h-5 text-white" />
          </div>
          <span className="ml-3 font-bold text-lg tracking-tight hidden lg:block bg-clip-text text-transparent bg-gradient-to-r from-white to-slate-400">
            NEXUS Lab
          </span>
        </div>

        <nav className="flex-1 p-4 space-y-2">
          <button className="w-full flex items-center gap-3 p-3 rounded-xl bg-white/5 text-slate-100 hover:bg-white/10 transition-colors">
            <Terminal className="w-5 h-5 text-violet-400" />
            <span className="hidden lg:block">Novo Chat</span>
          </button>
        </nav>

        <div className="p-4 border-t border-white/5">
          <div className="flex items-center gap-3 p-2 rounded-lg hover:bg-white/5 cursor-pointer transition-colors">
            <div className="w-8 h-8 rounded-full bg-slate-700 flex items-center justify-center">
              <User className="w-4 h-4 text-slate-400" />
            </div>
            <div className="hidden lg:block">
              <p className="text-sm font-medium">Fabrício</p>
              <p className="text-xs text-slate-500">Admin</p>
            </div>
          </div>
        </div>
      </aside>

      {/* Main Chat Area */}
      <main className="flex-1 flex flex-col relative overflow-hidden bg-grid-white/[0.02]">

        {/* Messages List */}
        <div className="flex-1 overflow-y-auto p-4 lg:p-8 space-y-6">
          <AnimatePresence initial={false}>
            {messages.map((msg, idx) => (
              <motion.div
                key={idx}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className={clsx(
                  "flex gap-4 max-w-3xl mx-auto",
                  msg.role === 'user' ? "flex-row-reverse" : ""
                )}
              >
                {/* Avatar */}
                <div className={clsx(
                  "w-8 h-8 rounded-lg flex-shrink-0 flex items-center justify-center shadow-lg",
                  msg.role === 'user'
                    ? "bg-slate-700"
                    : "bg-gradient-to-br from-violet-600 to-indigo-600"
                )}>
                  {msg.role === 'user' ? <User size={16} /> : <Bot size={16} />}
                </div>

                {/* Bubble */}
                <div className={clsx(
                  "p-4 rounded-2xl shadow-sm text-sm lg:text-base leading-relaxed whitespace-pre-wrap",
                  msg.role === 'user'
                    ? "bg-slate-800 text-slate-100 rounded-tr-sm ring-1 ring-white/10"
                    : "bg-none text-slate-300 pl-0 pt-2"
                )}>
                  {msg.content}
                </div>
              </motion.div>
            ))}
          </AnimatePresence>

          {isLoading && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="flex gap-4 max-w-3xl mx-auto"
            >
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-violet-600 to-indigo-600 flex items-center justify-center animate-pulse">
                <Bot size={16} />
              </div>
              <div className="p-2 text-sm text-slate-400 flex items-center gap-2">
                <span className="w-2 h-2 bg-violet-500 rounded-full animate-bounce"></span>
                <span className="w-2 h-2 bg-violet-500 rounded-full animate-bounce delay-75"></span>
                <span className="w-2 h-2 bg-violet-500 rounded-full animate-bounce delay-150"></span>
              </div>
            </motion.div>
          )}

          <div ref={bottomRef} className="h-4" />
        </div>

        {/* Input Area */}
        <div className="p-4 lg:p-6 bg-nexus-900/80 backdrop-blur-xl border-t border-white/5">
          <div className="max-w-3xl mx-auto relative group">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSubmit(e)}
              placeholder="Pergunte ao Agente..."
              className="w-full bg-slate-800/50 border border-white/10 rounded-xl px-4 py-4 pr-12 text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-violet-500/50 focus:border-violet-500/50 transition-all shadow-lg"
              disabled={isLoading}
            />
            <button
              onClick={handleSubmit}
              className="absolute right-2 top-2 p-2 rounded-lg bg-violet-600 text-white hover:bg-violet-500 transition-colors disabled:opacity-50 disabled:cursor-not-allowed group-focus-within:shadow-lg shadow-violet-500/25"
              disabled={!input.trim() || isLoading}
            >
              <Send size={18} />
            </button>
          </div>
          <p className="text-center text-xs text-slate-600 mt-2">
            NEXUS Agent + Antigravity Kit v2.0
          </p>
        </div>

      </main>
    </div>
  )
}

export default App

import { useState, useCallback, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { Upload, FileText, X, Zap, AlertCircle } from 'lucide-react'
import { uploadDocuments } from '../lib/api'
import AgentTimeline from '../components/AgentTimeline'

export default function UploadPage() {
  const navigate = useNavigate()
  const [files, setFiles] = useState([])
  const [dragging, setDragging] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [agentSteps, setAgentSteps] = useState([])
  const fileInputRef = useRef()

  const addFiles = useCallback((newFiles) => {
    const pdfs = Array.from(newFiles).filter((f) => f.type === 'application/pdf' || f.name.endsWith('.pdf'))
    if (pdfs.length === 0) {
      setError('Only PDF files are accepted.')
      return
    }
    setError('')
    setFiles((prev) => {
      const existing = new Set(prev.map((f) => f.name))
      return [...prev, ...pdfs.filter((f) => !existing.has(f.name))]
    })
  }, [])

  const onDrop = useCallback((e) => {
    e.preventDefault()
    setDragging(false)
    addFiles(e.dataTransfer.files)
  }, [addFiles])

  const onDragOver = (e) => { e.preventDefault(); setDragging(true) }
  const onDragLeave = () => setDragging(false)
  const removeFile = (name) => setFiles((prev) => prev.filter((f) => f.name !== name))

  const handleAnalyze = async () => {
    if (files.length === 0) {
      setError('Please upload at least one PDF document.')
      return
    }
    setLoading(true)
    setError('')
    setAgentSteps([])

    const agentNames = ['Planner', 'Document Analysis', 'Policy Retrieval', 'Compliance Check', 'Risk Assessment', 'Decision']
    let stepIndex = 0
    const interval = setInterval(() => {
      if (stepIndex < agentNames.length) {
        setAgentSteps((prev) => [
          ...prev,
          { agent: agentNames[stepIndex], status: 'completed', duration_ms: Math.floor(Math.random() * 400) + 100 },
        ])
        stepIndex++
      }
    }, 650)

    try {
      const result = await uploadDocuments(files)
      clearInterval(interval)
      sessionStorage.setItem('vendoriq_result', JSON.stringify(result))
      navigate('/dashboard')
    } catch (e) {
      clearInterval(interval)
      setError(e.message)
      setLoading(false)
    }
  }

  return (
    <div className="max-w-5xl mx-auto px-6 py-10">
      <div className="grid gap-8 lg:grid-cols-[1.9fr_1fr]">
        <section className="space-y-6">
          <div className="rounded-[1.25rem] bg-slate-950/5 dark:bg-white/5 border border-slate-200 dark:border-slate-800 p-8">
            <p className="text-sm font-semibold section-heading">VendorIQ Workflow</p>
            <h1 className="mt-3 text-3xl font-semibold tracking-tight text-slate-900 dark:text-white">
              Formalize vendor onboarding with elegant AI-driven decisions.
            </h1>
            <p className="mt-3 max-w-2xl text-sm text-slate-600 dark:text-slate-300 leading-7">
              Upload procurement documents and let the platform extract vendor profiles, match policy requirements, assess risk, and recommend the best next step.
            </p>
          </div>

          <div className="card p-8">
            <div className="flex items-center justify-between gap-4">
              <div>
                <p className="text-sm font-semibold section-heading">Secure Document Upload</p>
                <p className="mt-2 text-sm text-slate-600 dark:text-slate-300 leading-6">
                  Drop multiple PDFs at once. Supports GST, PAN, ISO, audit reports, banking details, and more.
                </p>
              </div>
              <div className="flex h-12 w-12 items-center justify-center rounded-3xl bg-indigo-50 dark:bg-indigo-900/20 text-indigo-600 dark:text-indigo-300">
                <Upload size={20} />
              </div>
            </div>

            <div
              onDrop={onDrop}
              onDragOver={onDragOver}
              onDragLeave={onDragLeave}
              onClick={() => fileInputRef.current?.click()}
              className={`mt-6 rounded-[1rem] border-2 border-dashed p-10 text-center cursor-pointer transition-all duration-200 ${dragging ? 'border-indigo-500 bg-indigo-50/50 dark:bg-indigo-900/20' : 'border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-950 hover:border-indigo-400 dark:hover:border-indigo-500'}`}
            >
              <input
                ref={fileInputRef}
                type="file"
                multiple
                accept=".pdf"
                className="hidden"
                onChange={(e) => addFiles(e.target.files)}
              />
              <div className="flex flex-col items-center gap-4">
                <div className={`flex h-14 w-14 items-center justify-center rounded-3xl transition ${dragging ? 'bg-indigo-100 dark:bg-indigo-900/40' : 'bg-slate-100 dark:bg-slate-800'}`}>
                  <Upload size={24} className={dragging ? 'text-indigo-600' : 'text-slate-400'} />
                </div>
                <div className="space-y-2">
                  <p className="text-base font-semibold text-slate-900 dark:text-white">Drag & drop files here</p>
                  <p className="text-sm text-slate-500 dark:text-slate-400">
                    or <span className="font-semibold text-indigo-600 dark:text-indigo-300">browse files</span> to upload vendor documents securely.
                  </p>
                </div>
              </div>
            </div>

            {files.length > 0 && (
              <div className="mt-6 overflow-hidden rounded-[1rem] border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-950">
                <div className="flex items-center justify-between px-5 py-4 border-b border-slate-200 dark:border-slate-800">
                  <div>
                    <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500 dark:text-slate-400">Selected Documents</p>
                    <p className="text-sm text-slate-600 dark:text-slate-300 mt-1">{files.length} file{files.length !== 1 ? 's' : ''}</p>
                  </div>
                  <button type="button" onClick={() => setFiles([])} className="text-xs font-semibold text-indigo-600 dark:text-indigo-300 hover:text-indigo-700 transition-colors">
                    Clear all
                  </button>
                </div>
                <div className="divide-y divide-slate-200 dark:divide-slate-800">
                  {files.map((file) => (
                    <div key={file.name} className="flex items-center gap-3 px-5 py-4">
                      <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300">
                        <FileText size={18} />
                      </div>
                      <div className="min-w-0 flex-1">
                        <p className="text-sm font-medium text-slate-900 dark:text-white truncate">{file.name}</p>
                        <p className="text-xs text-slate-500 dark:text-slate-400">{(file.size / 1024).toFixed(1)} KB</p>
                      </div>
                      <button type="button" onClick={() => removeFile(file.name)} className="text-slate-400 hover:text-red-500 transition-colors">
                        <X size={16} />
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {error && (
              <div className="mt-4 flex items-start gap-3 rounded-3xl border border-red-200 bg-red-50/80 p-4 text-sm text-red-700 dark:border-red-800 dark:bg-red-900/20 dark:text-red-200">
                <AlertCircle size={18} className="shrink-0" />
                <p>{error}</p>
              </div>
            )}

            <button
              type="button"
              onClick={handleAnalyze}
              disabled={loading || files.length === 0}
              className="mt-6 inline-flex w-full items-center justify-center gap-2 rounded-full bg-indigo-600 px-6 py-3 text-sm font-semibold text-white shadow-lg shadow-indigo-500/20 transition hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {loading ? (
                <>
                  <div className="h-4 w-4 animate-spin rounded-full border-2 border-white/50 border-t-white" />
                  Processing analysis
                </>
              ) : (
                <>
                  <Zap size={18} />
                  Start analysis
                </>
              )}
            </button>
          </div>
        </section>

        <aside className="space-y-6">
          <AgentTimeline timeline={agentSteps} isProcessing={loading} />

          <div className="card p-6">
            <p className="text-xs font-semibold section-heading">Why VendorIQ</p>
            <h2 className="mt-3 text-xl font-semibold text-slate-900 dark:text-white">Formal insight, simplified execution.</h2>
            <ul className="mt-5 space-y-3 text-sm text-slate-600 dark:text-slate-300">
              {[
                'AI-assisted compliance checks with audit-ready reporting',
                'RAG-driven policy retrieval for accurate recommendations',
                'Clear risk scoring and evidence-based outcomes',
                'Responsive light and dark themes with refined visuals',
              ].map((item) => (
                <li key={item} className="flex gap-3">
                  <span className="mt-1 inline-flex h-2.5 w-2.5 rounded-full bg-indigo-500" />
                  <span>{item}</span>
                </li>
              ))}
            </ul>
          </div>
        </aside>
      </div>
    </div>
  )
}

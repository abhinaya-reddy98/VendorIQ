import { useState } from 'react'
import { FlaskConical, ArrowRight, Loader } from 'lucide-react'
import { whatIfAnalysis } from '../lib/api'

const SCENARIOS = [
  'The vendor uploads a renewed ISO certificate valid for 3 years',
  'The vendor improves their factory audit score to 92/100',
  'The vendor provides all missing documents',
  'The vendor obtains ISO 27001 security certification',
]

export default function WhatIfAnalysis({ vendorName, currentAnalysis, vendorInfo }) {
  const [scenario, setScenario] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleAnalyze = async () => {
    if (!scenario.trim()) return
    setLoading(true)
    setError('')
    setResult(null)
    try {
      const data = await whatIfAnalysis({
        vendor_name: vendorName,
        scenario,
        current_analysis: currentAnalysis,
        vendor_info: vendorInfo,
      })
      setResult(data)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="card p-5">
      <div className="flex items-center gap-2 mb-4">
        <div className="w-7 h-7 bg-violet-100 dark:bg-violet-900/30 rounded-lg flex items-center justify-center">
          <FlaskConical size={14} className="text-violet-600 dark:text-violet-400" />
        </div>
        <h3 className="text-sm font-semibold text-slate-800 dark:text-slate-200">What-If Analysis</h3>
      </div>

      <p className="text-[11px] text-slate-500 dark:text-slate-400 mb-3">
        Simulate how changes to the vendor's submission would affect the recommendation.
      </p>

      {/* Quick scenarios */}
      <div className="flex flex-wrap gap-1.5 mb-3">
        {SCENARIOS.map((s) => (
          <button
            key={s}
            onClick={() => setScenario(s)}
            className="text-[10px] px-2 py-1 bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 rounded-md hover:bg-violet-50 dark:hover:bg-violet-900/20 hover:text-violet-700 dark:hover:text-violet-400 transition-colors"
          >
            {s}
          </button>
        ))}
      </div>

      <div className="flex gap-2">
        <textarea
          value={scenario}
          onChange={(e) => setScenario(e.target.value)}
          placeholder="Describe the hypothetical change..."
          rows={2}
          className="flex-1 text-xs p-2.5 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 text-slate-800 dark:text-slate-200 placeholder:text-slate-400 resize-none focus:outline-none focus:ring-2 focus:ring-violet-500/30"
        />
        <button
          onClick={handleAnalyze}
          disabled={!scenario.trim() || loading}
          className="px-3 py-2 bg-violet-600 text-white text-xs font-medium rounded-lg hover:bg-violet-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-1.5 self-end"
        >
          {loading ? <Loader size={12} className="animate-spin" /> : <ArrowRight size={12} />}
          {loading ? 'Analyzing...' : 'Simulate'}
        </button>
      </div>

      {error && (
        <p className="mt-3 text-xs text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-900/10 p-2 rounded-lg">{error}</p>
      )}

      {result && (
        <div className="mt-4 p-3 bg-violet-50 dark:bg-violet-900/20 rounded-lg border border-violet-100 dark:border-violet-900/40 space-y-2">
          <p className="text-[11px] font-semibold text-violet-700 dark:text-violet-300 uppercase tracking-wide">Simulation Result</p>
          <div className="flex items-center gap-2">
            <span className="text-[11px] text-slate-500">Original:</span>
            <span className="text-xs font-medium text-slate-700 dark:text-slate-300">{result.original_recommendation}</span>
            <ArrowRight size={10} className="text-slate-400" />
            <span className="text-xs font-semibold text-violet-700 dark:text-violet-300">{result.what_if_recommendation}</span>
          </div>
          {result.what_if_analysis && (
            <p className="text-[11px] text-slate-600 dark:text-slate-400 leading-relaxed">{result.what_if_analysis}</p>
          )}
        </div>
      )}
    </div>
  )
}

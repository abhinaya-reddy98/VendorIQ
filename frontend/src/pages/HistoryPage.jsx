import { useState, useEffect } from 'react'
import { Clock, RefreshCw, AlertCircle, TrendingUp, TrendingDown, Minus } from 'lucide-react'
import { getHistory } from '../lib/api'
import { getRiskColor, getRecommendationColor, formatDate, formatTime } from '../lib/utils'

const humanDecisionStyle = {
  Approved: 'bg-emerald-50 text-emerald-700 dark:bg-emerald-900/20 dark:text-emerald-400',
  Rejected: 'bg-red-50 text-red-700 dark:bg-red-900/20 dark:text-red-400',
  Deferred: 'bg-amber-50 text-amber-700 dark:bg-amber-900/20 dark:text-amber-400',
}

const HumanDecisionIcon = ({ decision }) => {
  if (decision === 'Approved') return <TrendingUp size={12} />
  if (decision === 'Rejected') return <TrendingDown size={12} />
  return <Minus size={12} />
}

export default function HistoryPage() {
  const [records, setRecords] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const loadHistory = async () => {
    setLoading(true)
    setError('')
    try {
      const data = await getHistory()
      setRecords(data.records || [])
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { loadHistory() }, [])

  const approved = records.filter((r) => r.human_decision === 'Approved').length
  const rejected = records.filter((r) => r.human_decision === 'Rejected').length
  const avgConfidence = records.length
    ? Math.round(records.reduce((a, r) => a + (r.confidence_score || 0), 0) / records.length * 100)
    : 0

  return (
    <div className="max-w-7xl mx-auto px-6 py-10">
      <div className="flex flex-col gap-6 md:flex-row md:items-center md:justify-between mb-6">
        <div>
          <h1 className="text-3xl font-semibold text-slate-900 dark:text-white tracking-tight">Vendor History</h1>
          <p className="mt-2 text-sm text-slate-500 dark:text-slate-400">All vendor onboarding decisions recorded by VendorIQ.</p>
        </div>
        <button
          type="button"
          onClick={loadHistory}
          className="inline-flex items-center gap-2 rounded-2xl border border-slate-200 dark:border-slate-700 bg-slate-100 dark:bg-slate-900 px-4 py-2 text-sm text-slate-600 dark:text-slate-300 transition hover:border-indigo-300 dark:hover:border-indigo-500"
        >
          <RefreshCw size={16} className={loading ? 'animate-spin' : ''} />
          Refresh
        </button>
      </div>

      <div className="grid grid-cols-2 gap-4 md:grid-cols-4 mb-6">
        {[
          { label: 'Total analyzed', value: records.length, color: 'text-slate-700 dark:text-slate-300' },
          { label: 'Approved', value: approved, color: 'text-emerald-600' },
          { label: 'Rejected', value: rejected, color: 'text-red-600' },
          { label: 'Avg confidence', value: `${avgConfidence}%`, color: 'text-indigo-600' },
        ].map(({ label, value, color }) => (
          <div key={label} className="card p-5">
            <p className="text-[10px] font-semibold uppercase tracking-[0.2em] text-slate-400 mb-2">{label}</p>
            <p className={`text-2xl font-semibold ${color}`}>{value}</p>
          </div>
        ))}
      </div>

      {loading ? (
        <div className="card p-12 text-center">
          <div className="mx-auto mb-3 flex h-12 w-12 items-center justify-center rounded-full border-4 border-indigo-200 border-t-indigo-600 animate-spin text-indigo-600" />
          <p className="text-sm text-slate-500">Loading history...</p>
        </div>
      ) : error ? (
        <div className="card p-8 text-center">
          <AlertCircle size={32} className="text-red-400 mx-auto mb-3" />
          <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
          <button onClick={loadHistory} className="mt-3 text-sm text-indigo-600 hover:underline">Retry</button>
        </div>
      ) : records.length === 0 ? (
        <div className="card p-12 text-center">
          <Clock size={36} className="text-slate-300 dark:text-slate-600 mx-auto mb-3" />
          <p className="text-sm text-slate-500 dark:text-slate-400">No vendor decisions yet.</p>
          <p className="text-xs text-slate-400 mt-2">Upload and analyze documents to get started.</p>
        </div>
      ) : (
        <div className="card overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-slate-100 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/50">
                  {['Vendor', 'AI recommendation', 'Human decision', 'Risk', 'Confidence', 'Compliance', 'Date'].map((h) => (
                    <th key={h} className="text-left px-4 py-3 text-[11px] font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wide whitespace-nowrap">
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {records.map((record, i) => {
                  const riskColors = getRiskColor(record.risk_level)
                  const recColors = getRecommendationColor(record.recommendation)
                  return (
                    <tr
                      key={record.id || i}
                      className="border-b border-slate-50 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-800/30 transition-colors"
                    >
                      <td className="px-4 py-3">
                        <p className="font-medium text-slate-800 dark:text-slate-200 text-xs">{record.vendor_name}</p>
                        {record.notes && (
                          <p className="text-[10px] text-slate-400 mt-0.5 max-w-[140px] truncate">{record.notes}</p>
                        )}
                      </td>
                      <td className="px-4 py-3">
                        <span className={`inline-flex rounded-full px-2 py-1 text-[11px] font-semibold ${recColors.light} ${recColors.text}`}>
                          {record.recommendation}
                        </span>
                      </td>
                      <td className="px-4 py-3">
                        {record.human_decision ? (
                          <span className={`inline-flex items-center gap-1 rounded-full px-2 py-1 text-[11px] font-semibold ${humanDecisionStyle[record.human_decision] || ''}`}>
                            <HumanDecisionIcon decision={record.human_decision} />
                            {record.human_decision}
                          </span>
                        ) : (
                          <span className="text-[11px] text-slate-400">Pending</span>
                        )}
                      </td>
                      <td className="px-4 py-3">
                        <span className={`inline-flex rounded-full px-2 py-1 text-[11px] font-semibold ${riskColors.bg} ${riskColors.text}`}>
                          {record.risk_level}
                        </span>
                      </td>
                      <td className="px-4 py-3">
                        <div className="flex items-center gap-2">
                          <div className="h-1.5 w-16 overflow-hidden rounded-full bg-slate-100 dark:bg-slate-800">
                            <div className="h-full rounded-full bg-indigo-500" style={{ width: `${Math.round((record.confidence_score || 0) * 100)}%` }} />
                          </div>
                          <span className="text-[11px] text-slate-600 dark:text-slate-400">{Math.round((record.confidence_score || 0) * 100)}%</span>
                        </div>
                      </td>
                      <td className="px-4 py-3">
                        <span className={`text-[11px] font-semibold ${record.compliance_score >= 80 ? 'text-emerald-600' : 'text-red-600'}`}>
                          {record.compliance_score}%
                        </span>
                      </td>
                      <td className="px-4 py-3 whitespace-nowrap">
                        <p className="text-[11px] text-slate-600 dark:text-slate-400">{formatDate(record.timestamp)}</p>
                        <p className="text-[10px] text-slate-400">{formatTime(record.timestamp)}</p>
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}

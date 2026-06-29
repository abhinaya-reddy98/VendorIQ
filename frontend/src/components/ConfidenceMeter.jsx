export default function ConfidenceMeter({ score = 0 }) {
  const pct = Math.round(score * 100)
  const radius = 38
  const circumference = 2 * Math.PI * radius
  const offset = circumference - (pct / 100) * circumference

  const color = pct >= 80 ? '#10b981' : pct >= 60 ? '#f59e0b' : '#ef4444'
  const label = pct >= 80 ? 'High confidence' : pct >= 60 ? 'Moderate confidence' : 'Low confidence'

  return (
    <div className="card p-5 flex flex-col items-center gap-3">
      <h3 className="text-sm font-semibold text-slate-800 dark:text-slate-200 self-start">
        Confidence Score
      </h3>
      <div className="relative w-28 h-28">
        <svg className="w-28 h-28 -rotate-90" viewBox="0 0 92 92">
          <circle
            cx="46" cy="46" r={radius}
            fill="none"
            stroke="currentColor"
            strokeWidth="7"
            className="text-slate-100 dark:text-slate-800"
          />
          <circle
            cx="46" cy="46" r={radius}
            fill="none"
            stroke={color}
            strokeWidth="7"
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            style={{ transition: 'stroke-dashoffset 1s ease' }}
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-2xl font-bold text-slate-900 dark:text-white">{pct}%</span>
        </div>
      </div>
      <div className="text-center">
        <p className="text-xs font-medium" style={{ color }}>{label}</p>
        <p className="text-[11px] text-slate-400 dark:text-slate-500 mt-1">
          Based on document completeness,<br />policy alignment, and risk factors.
        </p>
      </div>
    </div>
  )
}

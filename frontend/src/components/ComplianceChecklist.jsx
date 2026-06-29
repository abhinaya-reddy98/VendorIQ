import { CheckCircle2, XCircle, FileText } from 'lucide-react'

export default function ComplianceChecklist({ checklist = [], score = 0 }) {
  return (
    <div className="card p-5">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-semibold text-slate-800 dark:text-slate-200">
          Compliance Checklist
        </h3>
        <div className="flex items-center gap-2">
          <div className="h-1.5 w-24 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
            <div
              className={`h-full rounded-full transition-all duration-700 ${
                score >= 80 ? 'bg-emerald-500' : score >= 60 ? 'bg-amber-500' : 'bg-red-500'
              }`}
              style={{ width: `${score}%` }}
            />
          </div>
          <span className={`text-xs font-semibold ${
            score >= 80 ? 'text-emerald-600' : score >= 60 ? 'text-amber-600' : 'text-red-600'
          }`}>{score}%</span>
        </div>
      </div>

      <div className="space-y-2">
        {checklist.map((item, i) => (
          <div
            key={i}
            className={`flex gap-3 p-3 rounded-lg border transition-colors ${
              item.status
                ? 'bg-emerald-50 dark:bg-emerald-900/10 border-emerald-100 dark:border-emerald-900/30'
                : 'bg-red-50 dark:bg-red-900/10 border-red-100 dark:border-red-900/30'
            }`}
          >
            {item.status ? (
              <CheckCircle2 size={16} className="text-emerald-600 dark:text-emerald-400 flex-shrink-0 mt-0.5" />
            ) : (
              <XCircle size={16} className="text-red-500 dark:text-red-400 flex-shrink-0 mt-0.5" />
            )}
            <div className="min-w-0">
              <p className={`text-xs font-semibold ${
                item.status ? 'text-emerald-800 dark:text-emerald-300' : 'text-red-800 dark:text-red-300'
              }`}>
                {item.check}
              </p>
              <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-0.5 leading-relaxed">
                {item.detail}
              </p>
              {item.policy_reference && (
                <div className="flex items-center gap-1 mt-1">
                  <FileText size={9} className="text-slate-400" />
                  <p className="text-[10px] text-slate-400">{item.policy_reference}</p>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      {checklist.length === 0 && (
        <p className="text-sm text-slate-400 text-center py-6">No compliance data available</p>
      )}
    </div>
  )
}

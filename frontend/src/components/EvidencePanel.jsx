import { BookOpen, Lightbulb, Shield } from 'lucide-react'

export default function EvidencePanel({ evidence = [], policyExcerpts = [], reason = '', supportingPolicy = '' }) {
  return (
    <div className="card p-5 space-y-4">
      <h3 className="text-sm font-semibold text-slate-800 dark:text-slate-200">Evidence & Policy</h3>

      {/* Reason */}
      {reason && (
        <div className="flex gap-3 p-3 bg-indigo-50 dark:bg-indigo-900/20 rounded-lg border border-indigo-100 dark:border-indigo-900/40">
          <Lightbulb size={15} className="text-indigo-600 dark:text-indigo-400 flex-shrink-0 mt-0.5" />
          <div>
            <p className="text-[11px] font-semibold text-indigo-700 dark:text-indigo-300 uppercase tracking-wide mb-1">AI Reasoning</p>
            <p className="text-xs text-slate-700 dark:text-slate-300 leading-relaxed">{reason}</p>
          </div>
        </div>
      )}

      {/* Evidence points */}
      {evidence.length > 0 && (
        <div>
          <p className="text-[11px] font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wide mb-2">Key Evidence</p>
          <ul className="space-y-1.5">
            {evidence.map((e, i) => (
              <li key={i} className="flex gap-2 items-start">
                <span className="w-4 h-4 rounded-full bg-slate-100 dark:bg-slate-800 text-[9px] font-bold text-slate-500 flex items-center justify-center flex-shrink-0 mt-0.5">{i + 1}</span>
                <span className="text-xs text-slate-600 dark:text-slate-400">{e}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Supporting policy */}
      {supportingPolicy && (
        <div className="flex gap-3 p-3 bg-slate-50 dark:bg-slate-800/50 rounded-lg border border-slate-200 dark:border-slate-700">
          <Shield size={14} className="text-slate-500 flex-shrink-0 mt-0.5" />
          <div>
            <p className="text-[11px] font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wide mb-1">Supporting Policy</p>
            <p className="text-xs text-slate-700 dark:text-slate-300">{supportingPolicy}</p>
          </div>
        </div>
      )}

      {/* Policy excerpts */}
      {policyExcerpts.length > 0 && (
        <div>
          <p className="text-[11px] font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wide mb-2">Retrieved Policy Sections</p>
          <div className="space-y-2 max-h-48 overflow-y-auto pr-1">
            {policyExcerpts.map((excerpt, i) => (
              <div key={i} className="flex gap-2 p-2.5 bg-slate-50 dark:bg-slate-800/50 rounded-lg border border-slate-100 dark:border-slate-800">
                <BookOpen size={11} className="text-slate-400 flex-shrink-0 mt-0.5" />
                <p className="text-[11px] text-slate-500 dark:text-slate-400 leading-relaxed">{excerpt}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

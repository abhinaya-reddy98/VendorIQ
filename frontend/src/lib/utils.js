export function clsx(...classes) {
  return classes.filter(Boolean).join(' ')
}

export function getRiskColor(risk) {
  switch (risk?.toLowerCase()) {
    case 'low': return { bg: 'bg-emerald-50', text: 'text-emerald-700', border: 'border-emerald-200', dot: 'bg-emerald-500' }
    case 'medium': return { bg: 'bg-amber-50', text: 'text-amber-700', border: 'border-amber-200', dot: 'bg-amber-500' }
    case 'high': return { bg: 'bg-red-50', text: 'text-red-700', border: 'border-red-200', dot: 'bg-red-500' }
    default: return { bg: 'bg-slate-50', text: 'text-slate-700', border: 'border-slate-200', dot: 'bg-slate-500' }
  }
}

export function getRecommendationColor(rec) {
  switch (rec) {
    case 'Approve Vendor': return { bg: 'bg-emerald-500', light: 'bg-emerald-50', text: 'text-emerald-700' }
    case 'Reject Vendor': return { bg: 'bg-red-500', light: 'bg-red-50', text: 'text-red-700' }
    case 'Request Missing Documents': return { bg: 'bg-amber-500', light: 'bg-amber-50', text: 'text-amber-700' }
    case 'Escalate for Manual Review': return { bg: 'bg-indigo-500', light: 'bg-indigo-50', text: 'text-indigo-700' }
    default: return { bg: 'bg-slate-500', light: 'bg-slate-50', text: 'text-slate-700' }
  }
}

export function formatDate(dateStr) {
  if (!dateStr) return '—'
  const d = new Date(dateStr)
  if (isNaN(d)) return dateStr
  return d.toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' })
}

export function formatTime(dateStr) {
  if (!dateStr) return '—'
  const d = new Date(dateStr)
  if (isNaN(d)) return dateStr
  return d.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' })
}

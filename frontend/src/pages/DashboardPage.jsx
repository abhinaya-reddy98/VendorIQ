import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Building2,
  AlertTriangle,
  ArrowLeft,
  ThumbsUp,
  ThumbsDown,
  Clock,
  ChevronRight,
} from 'lucide-react'
import { approveVendor } from '../lib/api'
import ComplianceChecklist from '../components/ComplianceChecklist'
import ConfidenceMeter from '../components/ConfidenceMeter'
import EvidencePanel from '../components/EvidencePanel'
import AgentTimeline from '../components/AgentTimeline'
import WhatIfAnalysis from '../components/WhatIfAnalysis'
import { getRiskColor, getRecommendationColor } from '../lib/utils'

export default function DashboardPage() {
  const navigate = useNavigate()
  const [result, setResult] = useState(null)
  const [approvalStatus, setApprovalStatus] = useState(null)
  const [approving, setApproving] = useState(false)
  const [notes, setNotes] = useState('')
  const [activeTab, setActiveTab] = useState('overview')

  useEffect(() => {
    const stored = sessionStorage.getItem('vendoriq_result')
    if (stored) {
      setResult(JSON.parse(stored))
    } else {
      navigate('/')
    }
  }, [navigate])

  if (!result) return null

  const { vendor_info, compliance, risk, decision, policy_excerpts, agent_timeline } = result
  const riskColors = getRiskColor(risk.risk_level)
  const recColors = getRecommendationColor(decision.recommendation)

  const handleHumanDecision = async (humanDecision) => {
    setApproving(true)
    try {
      await approveVendor({
        vendor_name: vendor_info.company_name || 'Unknown Vendor',
        recommendation: decision.recommendation,
        human_decision: humanDecision,
        notes,
        confidence_score: decision.confidence_score,
        risk_level: risk.risk_level,
        compliance_score: compliance.compliance_score,
      })
      setApprovalStatus(humanDecision)
    } catch (e) {
      console.error(e)
    } finally {
      setApproving(false)
    }
  }

  const tabs = ['overview', 'compliance', 'evidence', 'timeline', 'what-if']

  return (
    <div className="max-w-7xl mx-auto px-6 py-10">
      <div className="flex flex-col gap-6 lg:flex-row lg:items-center lg:justify-between">
        <div>
          <button
            type="button"
            onClick={() => navigate('/')}
            className="inline-flex items-center gap-2 rounded-full border border-slate-200 dark:border-slate-800 bg-slate-100 dark:bg-slate-900 px-4 py-2 text-sm text-slate-600 dark:text-slate-300 transition hover:border-indigo-300 dark:hover:border-indigo-500"
          >
            <ArrowLeft size={14} />
            New analysis
          </button>
          <div className="mt-4">
            <p className="text-xs font-semibold section-heading">Decision summary</p>
            <h1 className="mt-3 text-3xl font-semibold tracking-tight text-slate-900 dark:text-white">
              {vendor_info.company_name || 'Unknown Vendor'}
            </h1>
          </div>
        </div>

        <div className="rounded-3xl border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-950 px-5 py-4 shadow-sm">
          <div className="flex items-center gap-3">
            <div className="flex h-12 w-12 items-center justify-center rounded-3xl bg-indigo-100 dark:bg-indigo-900/30 text-indigo-700 dark:text-indigo-300">
              <Building2 size={18} />
            </div>
            <div>
              <p className="text-xs uppercase tracking-[0.24em] text-slate-500 dark:text-slate-400">Vendor profile</p>
              <p className="mt-2 text-sm text-slate-600 dark:text-slate-300">{vendor_info.company_name || 'No company name available'}</p>
            </div>
          </div>
        </div>
      </div>

      <div className="grid gap-4 mt-6 sm:grid-cols-2 xl:grid-cols-[1.5fr_1fr]">
        <div className="rounded-[1.25rem] bg-gradient-to-br from-indigo-600 to-violet-500 p-6 text-white shadow-[0_18px_60px_rgba(79,70,229,0.18)]">
          <p className="text-xs uppercase tracking-[0.24em] opacity-90">Recommended action</p>
          <p className="mt-4 text-lg font-semibold">{decision.recommendation}</p>
          <p className="mt-3 text-sm leading-6 text-indigo-100 opacity-90">{decision.reason}</p>
          <div className="mt-6 inline-flex items-center gap-2 rounded-full bg-white/10 px-3 py-2 text-sm font-semibold">
            <span className={`inline-flex h-2.5 w-2.5 rounded-full ${recColors.bg}`} />
            Confidence {Math.round(decision.confidence_score * 100)}%
          </div>
        </div>

        <div className="grid gap-4">
          <div className="card p-5">
            <p className="text-xs font-semibold section-heading">Compliance score</p>
            <p className="mt-3 text-3xl font-semibold text-slate-900 dark:text-white">{compliance.compliance_score}%</p>
            <p className="mt-2 text-sm text-slate-500 dark:text-slate-400">Policy compliance and document validation.</p>
          </div>
          <div className="card p-5">
            <p className="text-xs font-semibold section-heading">Risk assessment</p>
            <p className="mt-3 text-3xl font-semibold text-slate-900 dark:text-white">{risk.risk_level}</p>
            <p className="mt-2 text-sm text-slate-500 dark:text-slate-400">{risk.reasons.length} risk factor{risk.reasons.length === 1 ? '' : 's'} identified.</p>
          </div>
        </div>
      </div>

      <div className="mt-8 rounded-3xl bg-slate-100 dark:bg-slate-950 p-3 shadow-sm">
        <div className="flex flex-wrap gap-2">
          {tabs.map((tab) => (
            <button
              type="button"
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`rounded-2xl px-4 py-2 text-sm font-semibold transition ${
                activeTab === tab
                  ? 'bg-white dark:bg-slate-800 text-slate-900 dark:text-white shadow-sm'
                  : 'text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
              }`}
            >
              {tab === 'what-if' ? 'What-If' : tab.charAt(0).toUpperCase() + tab.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {activeTab === 'overview' && (
        <div className="grid gap-5 xl:grid-cols-[2fr_1fr] mt-5">
          <div className="space-y-5">
            <div className="card p-6">
              <h2 className="text-base font-semibold text-slate-900 dark:text-white">Vendor information</h2>
              <dl className="mt-5 grid grid-cols-2 gap-x-6 gap-y-4 text-sm text-slate-600 dark:text-slate-300">
                {[
                  ['Company', vendor_info.company_name],
                  ['GST Number', vendor_info.gst_number],
                  ['PAN Number', vendor_info.pan_number],
                  ['ISO Expiry', vendor_info.iso_certificate_expiry],
                  ['Audit Score', vendor_info.audit_score ? `${vendor_info.audit_score}/100` : '—'],
                  ['Bank', vendor_info.bank_name],
                  ['IFSC Code', vendor_info.ifsc_code],
                  ['Email', vendor_info.contact_email],
                ].map(([label, value]) => (
                  <div key={label}>
                    <dt className="text-[11px] uppercase tracking-[0.18em] text-slate-400">{label}</dt>
                    <dd className="mt-1 text-sm font-medium text-slate-700 dark:text-slate-200">{value || 'Not available'}</dd>
                  </div>
                ))}
              </dl>
            </div>

            <div className="card p-6 bg-slate-50 dark:bg-slate-800/50">
              <p className="text-xs font-semibold section-heading">Decision rationale</p>
              <p className="mt-3 text-sm leading-7 text-slate-700 dark:text-slate-300">{decision.reason}</p>
            </div>
          </div>

          <aside className="space-y-5">
            <ConfidenceMeter score={decision.confidence_score} />
            {risk.reasons.length > 0 && (
              <div className="card p-6">
                <div className="flex items-center justify-between gap-3">
                  <div>
                    <p className="text-xs font-semibold section-heading">Risk insights</p>
                    <p className="mt-2 text-sm text-slate-600 dark:text-slate-400">Key risk drivers for this vendor.</p>
                  </div>
                  <span className={`inline-flex rounded-full px-3 py-1 text-[11px] font-semibold ${riskColors.bg} ${riskColors.text}`}>
                    {risk.risk_level}
                  </span>
                </div>
                <ul className="mt-4 space-y-2 text-sm text-slate-500 dark:text-slate-400">
                  {risk.reasons.map((reason, index) => (
                    <li key={index} className="flex gap-3">
                      <span className="mt-1 inline-flex h-2.5 w-2.5 rounded-full bg-indigo-500" />
                      <span>{reason}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {!approvalStatus ? (
              <div className="card p-6">
                <p className="text-xs font-semibold section-heading">Human approval</p>
                <textarea
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  rows={3}
                  placeholder="Add approval notes (optional)"
                  className="mt-4 w-full rounded-2xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-950 px-4 py-3 text-sm text-slate-900 dark:text-slate-100 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500/30"
                />
                <div className="mt-4 grid gap-3 sm:grid-cols-3">
                  <button
                    type="button"
                    onClick={() => handleHumanDecision('Approved')}
                    disabled={approving}
                    className="rounded-2xl bg-emerald-600 px-4 py-3 text-sm font-semibold text-white transition hover:bg-emerald-700 disabled:opacity-50"
                  >
                    Approve
                  </button>
                  <button
                    type="button"
                    onClick={() => handleHumanDecision('Rejected')}
                    disabled={approving}
                    className="rounded-2xl bg-red-600 px-4 py-3 text-sm font-semibold text-white transition hover:bg-red-700 disabled:opacity-50"
                  >
                    Reject
                  </button>
                  <button
                    type="button"
                    onClick={() => handleHumanDecision('Deferred')}
                    disabled={approving}
                    className="rounded-2xl bg-amber-500 px-4 py-3 text-sm font-semibold text-white transition hover:bg-amber-600 disabled:opacity-50"
                  >
                    Defer
                  </button>
                </div>
              </div>
            ) : (
              <div className={`card p-6 text-center ${approvalStatus === 'Approved' ? 'bg-emerald-50 dark:bg-emerald-900/10 border-emerald-200 dark:border-emerald-900/40' : approvalStatus === 'Rejected' ? 'bg-red-50 dark:bg-red-900/10 border-red-200 dark:border-red-900/40' : 'bg-amber-50 dark:bg-amber-900/10 border-amber-200 dark:border-amber-900/40'}`}>
                <p className="text-sm font-semibold">Decision recorded</p>
                <p className="mt-2 text-lg font-bold text-slate-900 dark:text-white">{approvalStatus}</p>
                <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">Saved to memory for audit and historical learning.</p>
              </div>
            )}
          </aside>
        </div>
      )}

      {activeTab === 'compliance' && (
        <div className="mt-5">
          <ComplianceChecklist checklist={compliance.checklist} score={compliance.compliance_score} />
        </div>
      )}

      {activeTab === 'evidence' && (
        <div className="mt-5">
          <EvidencePanel
            evidence={decision.evidence}
            policyExcerpts={policy_excerpts}
            reason={decision.reason}
            supportingPolicy={decision.supporting_policy}
          />
        </div>
      )}

      {activeTab === 'timeline' && (
        <div className="mt-5">
          <AgentTimeline timeline={agent_timeline} />
        </div>
      )}

      {activeTab === 'what-if' && (
        <div className="mt-5">
          <WhatIfAnalysis
            vendorName={vendor_info.company_name}
            vendorInfo={vendor_info}
            currentAnalysis={{
              recommendation: decision.recommendation,
              compliance_score: compliance.compliance_score,
              risk_level: risk.risk_level,
            }}
          />
        </div>
      )}
    </div>
  )
}

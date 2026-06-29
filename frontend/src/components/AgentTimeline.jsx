import { CheckCircle, Circle, Loader } from 'lucide-react'

const AGENT_ORDER = [
  { key: 'Planner', label: 'Planner Agent', desc: 'Coordinating workflow' },
  { key: 'Document Analysis', label: 'Document Analysis', desc: 'Extracting vendor data from PDFs' },
  { key: 'Policy Retrieval', label: 'Policy RAG Agent', desc: 'Retrieving relevant policies from ChromaDB' },
  { key: 'Compliance Check', label: 'Compliance Agent', desc: 'Checking against procurement policies' },
  { key: 'Risk Assessment', label: 'Risk Assessment Agent', desc: 'Calculating vendor risk score' },
  { key: 'Decision', label: 'Decision Agent', desc: 'Generating recommendation with Gemini AI' },
]

export default function AgentTimeline({ timeline = [], isProcessing = false }) {
  const completedAgents = new Set(timeline.map((t) => t.agent))

  return (
    <div className="card p-5">
      <h3 className="text-sm font-semibold text-slate-800 dark:text-slate-200 mb-4">
        Agent Execution Timeline
      </h3>
      <div className="space-y-0">
        {AGENT_ORDER.map((agent, i) => {
          const completed = completedAgents.has(agent.key)
          const timelineItem = timeline.find((t) => t.agent === agent.key)
          const isActive = isProcessing && !completed && completedAgents.size === i

          return (
            <div key={agent.key} className="flex gap-3">
              {/* Icon + connector */}
              <div className="flex flex-col items-center">
                <div className={`w-6 h-6 rounded-full flex items-center justify-center flex-shrink-0 transition-all duration-500 ${
                  completed
                    ? 'bg-indigo-100 dark:bg-indigo-900/40'
                    : isActive
                    ? 'bg-amber-100 dark:bg-amber-900/40'
                    : 'bg-slate-100 dark:bg-slate-800'
                }`}>
                  {completed ? (
                    <CheckCircle size={13} className="text-indigo-600 dark:text-indigo-400" />
                  ) : isActive ? (
                    <Loader size={13} className="text-amber-500 animate-spin" />
                  ) : (
                    <Circle size={13} className="text-slate-300 dark:text-slate-600" />
                  )}
                </div>
                {i < AGENT_ORDER.length - 1 && (
                  <div className={`w-px flex-1 my-1 transition-all duration-500 ${
                    completed ? 'bg-indigo-200 dark:bg-indigo-800' : 'bg-slate-200 dark:bg-slate-700'
                  }`} style={{ minHeight: '16px' }} />
                )}
              </div>

              {/* Content */}
              <div className="pb-4 pt-0.5 min-w-0">
                <div className="flex items-center gap-2">
                  <span className={`text-xs font-medium ${
                    completed
                      ? 'text-slate-800 dark:text-slate-200'
                      : 'text-slate-400 dark:text-slate-500'
                  }`}>
                    {agent.label}
                  </span>
                  {timelineItem?.duration_ms && (
                    <span className="text-[10px] text-slate-400 dark:text-slate-500">
                      {timelineItem.duration_ms}ms
                    </span>
                  )}
                </div>
                <p className="text-[11px] text-slate-400 dark:text-slate-500 mt-0.5">{agent.desc}</p>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

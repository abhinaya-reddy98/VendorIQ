import { NavLink } from 'react-router-dom'
import { Zap, Upload, LayoutDashboard, Clock, Moon, Sun } from 'lucide-react'
import { useState, useEffect } from 'react'

const navItems = [
  { to: '/', label: 'Upload', icon: Upload },
  { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/history', label: 'History', icon: Clock },
]

function getInitialTheme() {
  if (typeof window === 'undefined') return false
  const stored = window.localStorage.getItem('theme')
  if (stored) return stored === 'dark'
  return window.matchMedia?.('(prefers-color-scheme: dark)').matches ?? false
}

export default function Navbar() {
  const [dark, setDark] = useState(getInitialTheme)

  useEffect(() => {
    document.documentElement.classList.toggle('dark', dark)
    window.localStorage.setItem('theme', dark ? 'dark' : 'light')
  }, [dark])

  return (
    <nav className="fixed inset-x-0 top-0 z-50 border-b border-slate-200 dark:border-slate-800 bg-white/85 dark:bg-slate-950/85 backdrop-blur-xl shadow-sm">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-6">
        <NavLink to="/" className="flex items-center gap-3">
          <div className="flex h-11 w-11 items-center justify-center rounded-3xl bg-gradient-to-br from-indigo-600 to-violet-500 shadow-[0_18px_60px_rgba(79,70,229,0.18)] transition-transform duration-300 hover:-translate-y-0.5">
            <Zap size={16} className="text-white" />
          </div>
          <div>
            <p className="text-sm font-semibold text-slate-900 dark:text-white">VendorIQ</p>
            <p className="text-[11px] text-slate-500 dark:text-slate-400">Vendor intelligence platform</p>
          </div>
        </NavLink>

        <div className="flex items-center gap-2">
          {navItems.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              end={to === '/'}
              className={({ isActive }) =>
                `inline-flex items-center gap-2 rounded-2xl px-4 py-2 text-sm font-medium transition-all duration-200 ${
                  isActive
                    ? 'bg-indigo-50 dark:bg-indigo-900/30 text-indigo-700 dark:text-indigo-200 shadow-sm'
                    : 'text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 hover:text-slate-900 dark:hover:text-white'
                }`
              }
            >
              <Icon size={14} />
              {label}
            </NavLink>
          ))}
        </div>

        <button
          type="button"
          onClick={() => setDark(!dark)}
          aria-label="Toggle theme"
          className="flex h-11 w-11 items-center justify-center rounded-3xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-900 text-slate-600 dark:text-slate-200 transition hover:border-indigo-300 dark:hover:border-indigo-500"
        >
          {dark ? <Sun size={16} /> : <Moon size={16} />}
        </button>
      </div>
    </nav>
  )
}

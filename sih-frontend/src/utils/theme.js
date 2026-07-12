export const THEMES = {
  teal: {
    label: 'Teal médical',
    accent: '#14b8a6',
    accentLight: '#2dd4bf',
    sidebar: 'rgba(15, 23, 42, 0.95)',
    gradient: 'from-teal-500 to-cyan-500',
  },
  purple: {
    label: 'Violet institutionnel',
    accent: '#8b5cf6',
    accentLight: '#a78bfa',
    sidebar: 'rgba(30, 20, 50, 0.95)',
    gradient: 'from-violet-500 to-purple-500',
  },
  blue: {
    label: 'Bleu clinique',
    accent: '#3b82f6',
    accentLight: '#60a5fa',
    sidebar: 'rgba(15, 23, 42, 0.95)',
    gradient: 'from-blue-500 to-indigo-500',
  },
  emerald: {
    label: 'Vert apaisant',
    accent: '#10b981',
    accentLight: '#34d399',
    sidebar: 'rgba(10, 30, 25, 0.95)',
    gradient: 'from-emerald-500 to-teal-500',
  },
  rose: {
    label: 'Rose humanitaire',
    accent: '#f43f5e',
    accentLight: '#fb7185',
    sidebar: 'rgba(40, 15, 25, 0.95)',
    gradient: 'from-rose-500 to-pink-500',
  },
  amber: {
    label: 'Ambre chaleureux',
    accent: '#f59e0b',
    accentLight: '#fbbf24',
    sidebar: 'rgba(35, 25, 10, 0.95)',
    gradient: 'from-amber-500 to-orange-500',
  },
  indigo: {
    label: 'Indigo premium',
    accent: '#6366f1',
    accentLight: '#818cf8',
    sidebar: 'rgba(20, 18, 45, 0.95)',
    gradient: 'from-indigo-500 to-violet-500',
  },
  slate: {
    label: 'Ardoise sobre',
    accent: '#64748b',
    accentLight: '#94a3b8',
    sidebar: 'rgba(15, 20, 30, 0.97)',
    gradient: 'from-slate-500 to-slate-700',
  },
}

const STORAGE_KEY = 'sghl_ui_theme'

export function getStoredTheme() {
  return localStorage.getItem(STORAGE_KEY) || 'teal'
}

export function setStoredTheme(name) {
  const raw = localStorage.getItem('user')
  if (raw) {
    try {
      const u = JSON.parse(raw)
      if (u?.role !== 'ADMIN' && !u?.can_access_all && !u?.can_manage_ui) return false
    } catch { return false }
  } else {
    return false
  }
  localStorage.setItem(STORAGE_KEY, name)
  applyTheme(name)
  return true
}

export function applyTheme(name) {
  const theme = THEMES[name] || THEMES.teal
  const root = document.documentElement
  const style = root.dataset.sghlCustomAccent
  if (!style) {
    root.style.setProperty('--theme-accent', theme.accent)
    root.style.setProperty('--theme-accent-light', theme.accentLight)
  }
  root.style.setProperty('--theme-sidebar', theme.sidebar)
  root.dataset.sghlTheme = name
  localStorage.setItem(STORAGE_KEY, name)
}

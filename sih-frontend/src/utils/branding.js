import { applyTheme, THEMES } from './theme.js'

const CACHE_KEY = 'sghl_branding_cache'
export const BRANDING_EVENT = 'sghl-branding-updated'

export const DEFAULT_STYLE = {
  cardRadius: '2rem',
  cardStyle: 'glass',
  animations: true,
  compactMode: false,
  fontScale: 100,
  sidebarGlow: true,
  headerBlur: true,
  loginBackground: 'https://images.unsplash.com/photo-1559839734-2b71ea197ec2?w=1920&q=80',
  customAccent: '',
  customAccentLight: '',
}

export const DEFAULT_BRANDING = {
  nom_hopital: 'SGHL — Hôpital Général',
  nom_application: 'SGHL',
  slogan_application: 'Système de Gestion Hospitalière et de Laboratoire',
  icone_application: '🏥',
  theme_ui: 'teal',
  config_style: { ...DEFAULT_STYLE },
}

export const CARD_STYLES = {
  glass: { label: 'Verre dépoli', class: 'style-glass' },
  solid: { label: 'Solide profond', class: 'style-solid' },
  gradient: { label: 'Dégradé lumineux', class: 'style-gradient' },
}

export const RADIUS_OPTIONS = [
  { value: '0.75rem', label: 'Compact' },
  { value: '1.25rem', label: 'Standard' },
  { value: '2rem', label: 'Arrondi' },
  { value: '2.5rem', label: 'Très arrondi' },
]

export const ICON_OPTIONS = ['🏥', '⚕️', '🩺', '💊', '🔬', '🏛️', '❤️', '🌟', '🛡️', '🏨']

function mergeStyle(raw = {}) {
  return { ...DEFAULT_STYLE, ...(raw || {}) }
}

export function normalizeBranding(data = {}) {
  return {
    nom_hopital: data.nom_hopital || DEFAULT_BRANDING.nom_hopital,
    nom_application: data.nom_application || DEFAULT_BRANDING.nom_application,
    slogan_application: data.slogan_application || DEFAULT_BRANDING.slogan_application,
    icone_application: data.icone_application || DEFAULT_BRANDING.icone_application,
    theme_ui: data.theme_ui || DEFAULT_BRANDING.theme_ui,
    config_style: mergeStyle(data.config_style),
  }
}

export function getCachedBranding() {
  try {
    const raw = localStorage.getItem(CACHE_KEY)
    return raw ? normalizeBranding(JSON.parse(raw)) : { ...DEFAULT_BRANDING, config_style: mergeStyle() }
  } catch {
    return { ...DEFAULT_BRANDING, config_style: mergeStyle() }
  }
}

export function cacheBranding(data) {
  const normalized = normalizeBranding(data)
  localStorage.setItem(CACHE_KEY, JSON.stringify(normalized))
  return normalized
}

export function applyBranding(data) {
  const b = normalizeBranding(data)
  const style = b.config_style

  const root = document.documentElement
  root.style.setProperty('--app-card-radius', style.cardRadius)
  root.style.setProperty('--app-font-scale', `${style.fontScale}%`)
  root.style.setProperty('--app-login-bg', `url('${style.loginBackground}')`)

  if (style.customAccent) {
    root.dataset.sghlCustomAccent = '1'
    root.style.setProperty('--theme-accent', style.customAccent)
    root.style.setProperty('--theme-accent-light', style.customAccentLight || style.customAccent)
  } else {
    delete root.dataset.sghlCustomAccent
  }

  root.dataset.sghlCardStyle = style.cardStyle
  root.dataset.sghlCompact = style.compactMode ? '1' : '0'
  root.dataset.sghlAnimations = style.animations ? '1' : '0'
  root.dataset.sghlSidebarGlow = style.sidebarGlow ? '1' : '0'
  root.dataset.sghlHeaderBlur = style.headerBlur ? '1' : '0'

  applyTheme(b.theme_ui)

  const title = `${b.nom_application} — ${b.slogan_application.split('—')[0].trim()}`
  document.title = title.length > 80 ? b.nom_application : title

  const favicon = document.querySelector("link[rel='icon']")
  if (favicon) {
    const icon = b.icone_application.replace(/[<>&"']/g, '')
    favicon.href = `data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>${icon}</text></svg>`
  }

  if (typeof window !== 'undefined') {
    window.dispatchEvent(new CustomEvent(BRANDING_EVENT, { detail: b }))
  }

  return b
}

export async function loadBrandingFromApi(coreService) {
  try {
    const data = await coreService.settings()
    const cached = cacheBranding(data)
    applyBranding(cached)
    return cached
  } catch {
    const cached = getCachedBranding()
    applyBranding(cached)
    return cached
  }
}

export async function saveBranding(coreService, payload) {
  const data = await coreService.updateSettings(payload)
  const cached = cacheBranding(data)
  applyBranding(cached)
  return cached
}

export function canEditBranding(user) {
  return user?.role === 'ADMIN' || user?.can_access_all === true
}

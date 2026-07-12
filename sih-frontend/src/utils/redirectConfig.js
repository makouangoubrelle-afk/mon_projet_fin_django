/**
 * Configuration des redirections par rôle — modifiable par l'administrateur (localStorage).
 * { [role]: { homePath: '/chemin' } }
 */
const STORAGE_KEY = 'sghl_redirect_config'

export function getRedirectConfig() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    return raw ? JSON.parse(raw) : {}
  } catch {
    return {}
  }
}

export function saveRedirectConfig(config) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(config))
  if (typeof window !== 'undefined') {
    window.dispatchEvent(new Event('sghl-redirect-updated'))
  }
}

export function getRoleHomeOverride(role) {
  const path = getRedirectConfig()[role]?.homePath
  return path || null
}

export function setRoleHomeOverride(role, homePath) {
  const cfg = getRedirectConfig()
  if (!homePath) {
    if (cfg[role]) {
      delete cfg[role].homePath
      if (!Object.keys(cfg[role]).length) delete cfg[role]
    }
  } else {
    cfg[role] = { ...(cfg[role] || {}), homePath }
  }
  saveRedirectConfig(cfg)
}

/** Met la page d'accueil choisie en première position du parcours. */
export function applyHomeOverride(role, pages) {
  if (!pages?.length) return pages
  const home = getRoleHomeOverride(role)
  if (!home) return pages
  const idx = pages.findIndex((p) => p.path === home)
  if (idx <= 0) return pages
  const ordered = [...pages]
  const [picked] = ordered.splice(idx, 1)
  ordered.unshift(picked)
  return ordered
}

export function resetRedirectConfig() {
  localStorage.removeItem(STORAGE_KEY)
  if (typeof window !== 'undefined') {
    window.dispatchEvent(new Event('sghl-redirect-updated'))
  }
}

export function canEditRedirectConfig(user) {
  return user?.role === 'ADMIN' || user?.can_access_all === true
}

export function getAutoAdvance() {
  return getRedirectConfig().autoAdvance === true
}

export function setAutoAdvance(enabled) {
  const cfg = getRedirectConfig()
  cfg.autoAdvance = Boolean(enabled)
  saveRedirectConfig(cfg)
}

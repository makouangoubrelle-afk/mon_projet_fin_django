/**
 * Plan de navigation SGHL — ordre unique pour menus et redirections.
 * L'administrateur peut surcharger la page d'accueil par rôle (redirectConfig.js).
 */

import { applyHomeOverride, getRoleHomeOverride } from '../utils/redirectConfig.js'

export const NAV_SECTIONS = [
  {
    title: '1. Pilotage',
    pages: [
      { order: 1, path: '/admin', name: 'Admin', view: 'Admin', title: 'Administration', icon: '⚙️', roles: ['ADMIN'], adminOnly: true },
      { order: 2, path: '/', name: 'Dashboard', view: 'Dashboard', title: 'Tableau de bord', icon: '📊', roles: ['MEDECIN', 'INFIRMIER', 'SECRETAIRE', 'RECEPTIONNISTE', 'BIOLOGISTE', 'PHARMACIEN'] },
      { order: 2.1, path: '/users', name: 'Users', view: 'Users', title: 'Utilisateurs', icon: '👤', roles: ['ADMIN'], adminOnly: true },
      { order: 2.2, path: '/reports', name: 'Reports', view: 'Reports', title: 'Rapports', icon: '📈', roles: ['ADMIN', 'SECRETAIRE_GENERALE', 'SECRETAIRE', 'RECEPTIONNISTE'] },
      { order: 2.3, path: '/journal', name: 'Journal', view: 'Journal', title: 'Journal & connexions', icon: '📜', roles: ['ADMIN', 'SECRETAIRE_GENERALE'] },
      { order: 2.4, path: '/settings', name: 'HospitalSettings', view: 'HospitalSettings', title: "Paramètres hôpital", icon: '🏥', roles: ['ADMIN'], adminOnly: true },
      { order: 2.5, path: '/personnel', name: 'Personnel', view: 'Personnel', title: 'Personnel', icon: '👥', roles: ['ADMIN', 'SECRETAIRE_GENERALE'] },
    ],
  },
  {
    title: '2. Accueil patient',
    pages: [
      { order: 3, path: '/mon-espace', name: 'PatientPortal', view: 'PatientPortal', title: 'Mon espace patient', icon: '🧑', roles: ['PATIENT'] },
      { order: 4, path: '/patients', name: 'Patients', view: 'Patients', title: 'Patients', icon: '👥', roles: ['ADMIN', 'MEDECIN', 'INFIRMIER', 'SECRETAIRE', 'SECRETAIRE_GENERALE', 'RECEPTIONNISTE', 'PATIENT'], patientLabel: 'Mon statut', patientIcon: '👤' },
      { order: 5, path: '/reception', name: 'Reception', view: 'Reception', title: 'Réception', icon: '🏪', roles: ['ADMIN', 'RECEPTIONNISTE', 'SECRETAIRE', 'SECRETAIRE_GENERALE'] },
    ],
  },
  {
    title: '3. Parcours clinique',
    pages: [
      { order: 6, path: '/waiting-room', name: 'WaitingRoom', view: 'WaitingRoom', title: "Salle d'attente", icon: '🪑', roles: ['ADMIN', 'MEDECIN', 'INFIRMIER', 'SECRETAIRE', 'SECRETAIRE_GENERALE', 'RECEPTIONNISTE'] },
      { order: 7, path: '/urgence', name: 'Urgence', view: 'Urgence', title: 'Urgences', icon: '🚨', roles: ['ADMIN', 'MEDECIN', 'INFIRMIER', 'SECRETAIRE', 'SECRETAIRE_GENERALE', 'RECEPTIONNISTE'] },
      { order: 8, path: '/consultations', name: 'Consultations', view: 'Consultations', title: 'Consultations', icon: '🩺', roles: ['ADMIN', 'MEDECIN', 'INFIRMIER', 'SECRETAIRE', 'SECRETAIRE_GENERALE'] },
      { order: 9, path: '/doctors', name: 'Doctors', view: 'Doctors', title: 'Médecins', icon: '👨‍⚕️', roles: ['ADMIN', 'SECRETAIRE', 'SECRETAIRE_GENERALE', 'RECEPTIONNISTE'] },
      { order: 10, path: '/nurses', name: 'Nurses', view: 'Nurses', title: 'Infirmiers', icon: '💉', roles: ['ADMIN', 'MEDECIN', 'INFIRMIER', 'SECRETAIRE', 'SECRETAIRE_GENERALE'] },
      { order: 11, path: '/agenda', name: 'Agenda', view: 'Agenda', title: 'Agenda', icon: '📅', roles: ['ADMIN', 'MEDECIN', 'INFIRMIER', 'SECRETAIRE', 'SECRETAIRE_GENERALE'] },
      { order: 12, path: '/ordonnances', name: 'Ordonnances', view: 'Ordonnances', title: 'Ordonnances', icon: '📋', roles: ['ADMIN', 'MEDECIN', 'INFIRMIER', 'SECRETAIRE', 'SECRETAIRE_GENERALE', 'RECEPTIONNISTE', 'PATIENT'], patientLabel: 'Mes ordonnances' },
    ],
  },
  {
    title: '4. Services & hospitalisation',
    pages: [
      { order: 13, path: '/departments', name: 'Departments', view: 'Departments', title: 'Services & Redirections', icon: '🏢', roles: ['ADMIN', 'SECRETAIRE', 'SECRETAIRE_GENERALE', 'RECEPTIONNISTE', 'INFIRMIER'] },
      { order: 14, path: '/admissions', name: 'Admissions', view: 'admissions', title: 'Admissions', icon: '📝', roles: ['ADMIN', 'MEDECIN', 'INFIRMIER', 'SECRETAIRE', 'SECRETAIRE_GENERALE'] },
      { order: 15, path: '/rooms', name: 'Rooms', view: 'Rooms', title: 'Chambres & Lits', icon: '🛏️', roles: ['ADMIN', 'MEDECIN', 'INFIRMIER', 'SECRETAIRE', 'SECRETAIRE_GENERALE'] },
      { order: 16, path: '/localisation', name: 'Localisation', view: 'PatientLocation', title: 'Géolocalisation', icon: '📍', roles: ['ADMIN', 'MEDECIN', 'INFIRMIER', 'SECRETAIRE', 'SECRETAIRE_GENERALE', 'RECEPTIONNISTE', 'PATIENT'] },
    ],
  },
  {
    title: '5. Laboratoire & pharmacie',
    pages: [
      { order: 17, path: '/lab', name: 'Laboratory', view: 'Laboratory', title: 'Laboratoire', icon: '🔬', roles: ['ADMIN', 'MEDECIN', 'BIOLOGISTE', 'PATIENT', 'SECRETAIRE_GENERALE'], patientLabel: 'Mon laboratoire' },
      { order: 18, path: '/blood-bank', name: 'BloodBank', view: 'BloodBank', title: 'Banque de Sang', icon: '🩸', roles: ['ADMIN', 'MEDECIN', 'INFIRMIER', 'BIOLOGISTE', 'SECRETAIRE_GENERALE'] },
      { order: 19, path: '/pharmacy', name: 'Pharmacy', view: 'Pharmacy', title: 'Pharmacie', icon: '💊', roles: ['ADMIN', 'MEDECIN', 'INFIRMIER', 'SECRETAIRE_GENERALE', 'PHARMACIEN'] },
    ],
  },
  {
    title: '6. Caisse & finance',
    pages: [
      { order: 20, path: '/bills', name: 'Bills', view: 'Bills', title: 'Facturation', icon: '💰', roles: ['ADMIN', 'SECRETAIRE', 'SECRETAIRE_GENERALE', 'RECEPTIONNISTE'] },
      { order: 20.1, path: '/payments', name: 'Payments', view: 'Payments', title: 'Paiements', icon: '💳', roles: ['ADMIN', 'SECRETAIRE', 'SECRETAIRE_GENERALE', 'RECEPTIONNISTE'] },
      { order: 20.2, path: '/insurance', name: 'Insurance', view: 'Insurance', title: 'Assurances', icon: '🛡️', roles: ['ADMIN', 'SECRETAIRE', 'SECRETAIRE_GENERALE', 'RECEPTIONNISTE'] },
      { order: 21, path: '/privileged', name: 'PrivilegedClients', view: 'PrivilegedClients', title: 'Clients privilégiés', icon: '⭐', roles: ['ADMIN', 'SECRETAIRE', 'SECRETAIRE_GENERALE', 'RECEPTIONNISTE'] },
      { order: 22, path: '/bank', name: 'Bank', view: 'Bank', title: 'Banque', icon: '🏦', roles: ['ADMIN', 'SECRETAIRE', 'SECRETAIRE_GENERALE', 'RECEPTIONNISTE'] },
    ],
  },
  {
    title: '7. Informations',
    pages: [
      { order: 23, path: '/about', name: 'About', view: 'about', title: 'À propos', icon: 'ℹ️', roles: ['ADMIN', 'MEDECIN', 'INFIRMIER', 'SECRETAIRE', 'SECRETAIRE_GENERALE', 'RECEPTIONNISTE', 'BIOLOGISTE', 'PATIENT'] },
    ],
  },
]

/** Détail patient (hors menu principal, même contrôle d'accès que Patients) */
export const PATIENT_DETAIL_ROUTE = {
  order: 99,
  path: '/patients/:id',
  name: 'PatientDetail',
  view: 'PatientDetail',
  title: 'Dossier patient',
  roles: ['ADMIN', 'MEDECIN', 'INFIRMIER', 'SECRETAIRE', 'SECRETAIRE_GENERALE', 'RECEPTIONNISTE'],
}

const VIEW_LOADERS = {
  Dashboard: () => import('../views/Dashboard.vue'),
  Admin: () => import('../views/Admin.vue'),
  Users: () => import('../views/Users.vue'),
  Reports: () => import('../views/Reports.vue'),
  Journal: () => import('../views/Journal.vue'),
  HospitalSettings: () => import('../views/HospitalSettings.vue'),
  Personnel: () => import('../views/Personnel.vue'),
  Payments: () => import('../views/Payments.vue'),
  Insurance: () => import('../views/Insurance.vue'),
  PatientPortal: () => import('../views/PatientPortal.vue'),
  Patients: () => import('../views/Patients.vue'),
  PatientDetail: () => import('../views/PatientDetail.vue'),
  Reception: () => import('../views/Reception.vue'),
  WaitingRoom: () => import('../views/WaitingRoom.vue'),
  Urgence: () => import('../views/Urgence.vue'),
  Consultations: () => import('../views/Consultations.vue'),
  Doctors: () => import('../views/Doctors.vue'),
  Nurses: () => import('../views/Nurses.vue'),
  Agenda: () => import('../views/Agenda.vue'),
  Ordonnances: () => import('../views/Ordonnances.vue'),
  Departments: () => import('../views/Departments.vue'),
  admissions: () => import('../views/admissions.vue'),
  Rooms: () => import('../views/Rooms.vue'),
  PatientLocation: () => import('../views/PatientLocation.vue'),
  Laboratory: () => import('../views/Laboratory.vue'),
  BloodBank: () => import('../views/BloodBank.vue'),
  Pharmacy: () => import('../views/Pharmacy.vue'),
  Bills: () => import('../views/Bills.vue'),
  PrivilegedClients: () => import('../views/PrivilegedClients.vue'),
  Bank: () => import('../views/Bank.vue'),
  about: () => import('../views/about.vue'),
}

export const ALL_PAGES = NAV_SECTIONS.flatMap((s) => s.pages).sort((a, b) => a.order - b.order)

export const PAGE_TITLES = Object.fromEntries([
  ...ALL_PAGES.map((p) => [p.path, p.title]),
  [PATIENT_DETAIL_ROUTE.path, PATIENT_DETAIL_ROUTE.title],
])

export function hasFullAccess(user) {
  return user?.can_access_all === true || user?.role === 'ADMIN'
}

export function hasWideStaffAccess(user) {
  return hasFullAccess(user) || user?.role === 'SECRETAIRE_GENERALE'
}

function pageAllowsRole(page, role) {
  return page.roles?.includes(role)
}

function linkLabel(page, role) {
  if (role === 'PATIENT' && page.patientLabel) return page.patientLabel
  return page.title
}

function linkIcon(page, role) {
  if (role === 'PATIENT' && page.patientIcon) return page.patientIcon
  return page.icon
}

/** Pages accessibles pour un utilisateur, dans l'ordre officiel (+ surcharge admin) */
export function orderedPagesForUser(user) {
  if (!user?.role) return []
  const role = user.role
  let pages

  if (hasFullAccess(user)) {
    pages = ALL_PAGES.filter((p) => !p.adminOnly || role === 'ADMIN')
  } else if (hasWideStaffAccess(user)) {
    pages = ALL_PAGES.filter((p) => pageAllowsRole(p, role) && p.path !== '/admin')
  } else {
    pages = ALL_PAGES.filter((p) => pageAllowsRole(p, role))
  }

  return applyHomeOverride(role, pages)
}

/** Pages autorisées pour un rôle (sans surcharge redirection admin). */
export function basePagesForRole(role) {
  const user = { role, can_access_all: role === 'ADMIN' }
  if (hasFullAccess(user)) {
    return ALL_PAGES.filter((p) => !p.adminOnly || role === 'ADMIN')
  }
  if (hasWideStaffAccess(user)) {
    return ALL_PAGES.filter((p) => pageAllowsRole(p, role) && p.path !== '/admin')
  }
  return ALL_PAGES.filter((p) => pageAllowsRole(p, role))
}

/** 1re page du parcours = redirection par défaut après connexion */
export function defaultPathForUser(user) {
  const pages = orderedPagesForUser(user)
  return pages[0]?.path || '/login'
}

export function homeForRole(role, user = null) {
  if (user) return defaultPathForUser(user)
  const fake = { role, can_access_all: role === 'ADMIN' }
  return defaultPathForUser(fake)
}

export function canAccessPath(path, user) {
  if (!user) return false
  if (path === '/login') return true
  if (path.startsWith('/patients/') && path !== '/patients') {
    return PATIENT_DETAIL_ROUTE.roles.includes(user.role) || hasFullAccess(user) || hasWideStaffAccess(user)
  }
  const page = ALL_PAGES.find((p) => p.path === path)
  if (!page) return false
  if (page.adminOnly && user.role !== 'ADMIN') return false
  if (hasFullAccess(user)) return true
  if (hasWideStaffAccess(user)) return pageAllowsRole(page, user.role)
  return pageAllowsRole(page, user.role)
}

/** Prochaine page autorisée si la route actuelle ne l'est pas */
export function redirectPathForUser(user, attemptedPath) {
  if (canAccessPath(attemptedPath, user)) return null
  return defaultPathForUser(user)
}

export function getMenuForUser(user) {
  if (!user?.role) return []

  const role = user.role
  const pages = orderedPagesForUser(user)

  if (hasFullAccess(user)) {
    return [{
      title: 'Navigation complète (ordre officiel)',
      links: pages.map((p) => ({
        to: p.path,
        icon: linkIcon(p, role),
        label: `${p.order}. ${linkLabel(p, role)}`,
        order: p.order,
      })),
    }]
  }

  if (role === 'SECRETAIRE_GENERALE') {
    return [{
      title: 'Secrétariat général — parcours ordonné',
      links: pages.map((p) => ({
        to: p.path,
        icon: linkIcon(p, role),
        label: `${p.order}. ${p.title}`,
        order: p.order,
      })),
    }]
  }

  return NAV_SECTIONS
    .map((section) => ({
      title: section.title,
      links: section.pages
        .filter((p) => pageAllowsRole(p, role))
        .map((p) => ({
          to: p.path,
          icon: linkIcon(p, role),
          label: linkLabel(p, role),
          order: p.order,
        })),
    }))
    .filter((s) => s.links.length > 0)
}

/** Plan de redirection par rôle (affichage admin / secrétariat) */
export const ROLE_LABELS = {
  ADMIN: 'Administrateur',
  SECRETAIRE_GENERALE: 'Secrétaire générale',
  MEDECIN: 'Médecin',
  INFIRMIER: 'Infirmier',
  SECRETAIRE: 'Secrétaire',
  RECEPTIONNISTE: 'Réceptionniste',
  BIOLOGISTE: 'Biologiste / Laborantin',
  PHARMACIEN: 'Pharmacien',
  PATIENT: 'Patient',
}

export const ROLES_WITH_NAV = Object.keys(ROLE_LABELS)

export function redirectPlanForRole(role) {
  const fake = {
    role,
    can_access_all: role === 'ADMIN',
  }
  return orderedPagesForUser(fake).map((p, idx) => ({
    step: idx + 1,
    order: p.order,
    path: p.path,
    title: p.title,
    isHome: idx === 0,
    isCustomHome: idx === 0 && Boolean(getRoleHomeOverride(role)),
  }))
}

/** Normalise la route pour le parcours (détail patient → liste patients). */
export function normalizeFlowPath(path) {
  if (path.startsWith('/patients/') && path !== '/patients') return '/patients'
  return path
}

/** Page précédente / suivante dans le parcours ordonné du rôle. */
export function getPageFlowContext(path, user) {
  const pages = orderedPagesForUser(user)
  const normalized = normalizeFlowPath(path)
  const idx = pages.findIndex((p) => p.path === normalized)
  if (idx === -1) {
    return { current: null, prev: null, next: null, step: 0, total: pages.length, pages }
  }
  const role = user?.role
  return {
    current: pages[idx],
    prev: idx > 0 ? pages[idx - 1] : null,
    next: idx < pages.length - 1 ? pages[idx + 1] : null,
    step: idx + 1,
    total: pages.length,
    pages,
    prevLabel: idx > 0 ? linkLabel(pages[idx - 1], role) : null,
    nextLabel: idx < pages.length - 1 ? linkLabel(pages[idx + 1], role) : null,
    currentLabel: linkLabel(pages[idx], role),
  }
}

export function buildAppRoutes() {
  const routes = ALL_PAGES.map((p) => ({
    path: p.path,
    name: p.name,
    component: VIEW_LOADERS[p.view],
    meta: {
      roles: p.roles,
      order: p.order,
      title: p.title,
      ...(p.adminOnly ? { adminOnly: true } : {}),
    },
  }))

  routes.push({
    path: PATIENT_DETAIL_ROUTE.path,
    name: PATIENT_DETAIL_ROUTE.name,
    component: VIEW_LOADERS[PATIENT_DETAIL_ROUTE.view],
    meta: { roles: PATIENT_DETAIL_ROUTE.roles, title: PATIENT_DETAIL_ROUTE.title },
  })

  return routes
}

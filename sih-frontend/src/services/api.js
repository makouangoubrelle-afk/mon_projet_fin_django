import { defaultPathForUser, canAccessPath } from '../config/navigation.js'
import { extractEmail } from '../utils/email.js'

const API_BASE = '/api'
const PATIENT_SESSION_KEY = 'patientSession'

export const PATIENT_ROUTES = ['/mon-espace', '/patients', '/lab', '/ordonnances', '/localisation']

export function getPatientSession() {
  const raw = localStorage.getItem(PATIENT_SESSION_KEY)
  return raw ? JSON.parse(raw) : null
}

export function savePatientSession(data) {
  localStorage.removeItem('authToken')
  localStorage.removeItem('user')
  localStorage.setItem(PATIENT_SESSION_KEY, JSON.stringify({
    patient_id: data.patient_id,
    nom: data.nom,
    prenom: data.prenom,
    nom_recherche: data.nom_recherche || `${data.nom} ${data.prenom}`,
    nom_complet: data.nom_complet || `${data.nom} ${data.prenom}`,
  }))
}

export function clearPatientSession() {
  localStorage.removeItem(PATIENT_SESSION_KEY)
}

export function isPatientAccess() {
  const user = getUser()
  if (user?.role && user.role !== 'PATIENT') return false
  return Boolean(getPatientSession()?.patient_id) || user?.role === 'PATIENT'
}

export function isStaffUser() {
  const user = getUser()
  return Boolean(user?.role && user.role !== 'PATIENT')
}

export function isPatientRoute(path) {
  return PATIENT_ROUTES.includes(path)
}

async function apiCall(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`
  const headers = { 'Content-Type': 'application/json', ...(options.headers || {}) }
  const token = localStorage.getItem('authToken')
  if (token) headers['Authorization'] = `Bearer ${token}`
  try {
    const raw = localStorage.getItem('user')
    if (raw) {
      const u = JSON.parse(raw)
      if (u?.email) headers['X-SGHL-Email'] = u.email
    }
  } catch { /* ignore */ }
  const ps = getPatientSession()
  if (ps?.patient_id) {
    headers['X-SGHL-Patient-Id'] = String(ps.patient_id)
    const nomSession = ps.nom_recherche || ps.nom_complet || `${ps.nom || ''} ${ps.prenom || ''}`.trim()
    if (nomSession) headers['X-SGHL-Patient-Nom'] = nomSession
  }

  let response
  try {
    response = await fetch(url, { ...options, headers })
  } catch {
    throw new Error(
      'Impossible de contacter le serveur SGHL. Lancez : python manage.py runserver 8001'
    )
  }

  const ct = response.headers.get('content-type') || ''
  let data
  try {
    data = ct.includes('application/json') ? await response.json() : await response.text()
  } catch {
    data = null
  }

  if (!response.ok) {
    if (response.status === 502 || response.status === 503) {
      throw new Error(
        'Le serveur SGHL ne répond pas. Lancez : cd mon_projet_fin_django puis python manage.py runserver 8001'
      )
    }
    if (typeof data === 'string' && data.includes('<!DOCTYPE html>')) {
      if (data.includes('mon_projet_mongo')) {
        throw new Error(
          'Mauvais serveur Django sur le port 8000 (projet mon_projet_mongo). ' +
          'Lancez SGHL : python manage.py runserver 8001 depuis mon_projet_fin_django, puis relancez npm run dev.'
        )
      }
      if (data.includes('type_file') || data.includes('OperationalError')) {
        throw new Error(
          'Base de données à mettre à jour. Dans mon_projet_fin_django exécutez : python manage.py migrate puis python manage.py fix_salle_attente_type_file'
        )
      }
      throw new Error(
        'Réponse HTML au lieu de JSON — le backend SGHL n\'est pas démarré. ' +
        'Lancez : python manage.py runserver 8001'
      )
    }
    const detail = typeof data === 'object' ? (data.detail || JSON.stringify(data)) : data
    throw new Error(detail || `Erreur ${response.status}`)
  }
  return data
}

export const authService = {
  health: () => apiCall('/auth/health'),
  config: () => apiCall('/auth/config'),
  lookup: (email, role = '') => {
    const params = new URLSearchParams({ email: (email || '').trim() })
    if (role) params.set('role', role)
    return apiCall(`/auth/lookup?${params}`)
  },
  sendCode: (email, role = '') =>
    apiCall('/auth/send-code', {
      method: 'POST',
      body: JSON.stringify({
        email: email.trim().toLowerCase(),
        channel: 'email',
        role,
      }),
    }),
  verifyCode: (email, code, role = '') =>
    apiCall('/auth/verify-code', {
      method: 'POST',
      body: JSON.stringify({ email, code, role }),
    }),
  quickLogin: (email) =>
    apiCall('/auth/quick-login', { method: 'POST', body: JSON.stringify({ email }) }),
  resendCode: (email, role = '') =>
    apiCall('/auth/resend-code', {
      method: 'POST',
      body: JSON.stringify({
        email: email.trim().toLowerCase(),
        channel: 'email',
        role,
      }),
    }),
  demoAccounts: () => apiCall('/auth/comptes-demo'),
}

export function isAuthSuccess(res) {
  return Boolean(res && (res.success === true || (res.role && res.token)))
}

export function finishLogin(res, router, redirectPath) {
  if (!isAuthSuccess(res)) return false
  clearPatientSession()
  saveSession(res)
  const user = getUser()
  let target = redirectPath && canAccessPath(redirectPath, user)
    ? redirectPath
    : defaultPathForUser(user)
  if (user?.role === 'PATIENT') {
    target = '/mon-espace'
  }
  router.replace(target)
  return true
}

export const statsService = {
  dashboard: () => apiCall('/stats'),
  reports: () => apiCall('/core/reports'),
}

export const coreService = {
  settings: () => apiCall('/core/settings'),
  updateSettings: (data) => apiCall('/core/settings', { method: 'PATCH', body: JSON.stringify(data) }),
  loginHistory: (limit = 100) => apiCall(`/core/login-history?limit=${limit}`),
  activityLog: (limit = 100, module = '') => {
    const q = new URLSearchParams({ limit })
    if (module) q.set('module', module)
    return apiCall(`/core/activity-log?${q}`)
  },
  notifications: (unreadOnly = false) => apiCall(`/core/notifications?unread_only=${unreadOnly}`),
  markNotificationRead: (id) => apiCall(`/core/notifications/${id}/read`, { method: 'POST' }),
  markAllNotificationsRead: () => apiCall('/core/notifications/read-all', { method: 'POST' }),
  createNotification: (data) => apiCall('/core/notifications', { method: 'POST', body: JSON.stringify(data) }),
  users: (role = '') => apiCall(role ? `/core/users?role=${role}` : '/core/users'),
  adminOtpConfig: () => apiCall('/core/admin-otp'),
  setPrimaryAdmin: (userId) =>
    apiCall(`/core/users/${userId}/set-primary-admin`, { method: 'POST' }),
  createUser: (data) => apiCall('/core/users', { method: 'POST', body: JSON.stringify(data) }),
  updateUser: (id, data) => apiCall(`/core/users/${id}`, { method: 'PATCH', body: JSON.stringify(data) }),
  roles: () => apiCall('/core/roles'),
  backup: () => apiCall('/core/backup', { method: 'POST' }),
  backups: () => apiCall('/core/backups'),
}

export async function resolvePatientId() {
  const ps = getPatientSession()
  if (ps?.patient_id) return ps.patient_id

  const user = getUser()
  if (!user || user.role !== 'PATIENT') return null
  try {
    const profil = await patientService.me()
    if (profil?.id) {
      if (user.patient_id !== profil.id) {
        user.patient_id = profil.id
        localStorage.setItem('user', JSON.stringify(user))
      }
      return profil.id
    }
  } catch {
    /* dossier non lié à l'email */
  }
  return user.patient_id ?? null
}

export const patientService = {
  list: () => apiCall('/reception/patients'),
  get: (id) => apiCall(`/reception/patients/${id}`),
  parEmail: (query) =>
    apiCall(`/reception/patient-email?email=${encodeURIComponent((query || '').trim())}`),
  me: () => {
    const user = getUser()
    if (!user?.email) throw new Error('Non connecté')
    return apiCall(`/reception/mon-profil?email=${encodeURIComponent(user.email)}`)
  },
  monDossier: () => {
    const user = getUser()
    if (!user?.email) throw new Error('Non connecté')
    return apiCall(`/reception/mon-dossier?email=${encodeURIComponent(user.email)}`)
  },
  rechercherParNom: (nom) =>
    apiCall(`/reception/acces-patient/recherche?nom=${encodeURIComponent(nom)}`),
  dossierParNom: (nom, patientId) =>
    apiCall(`/reception/acces-patient/dossier?nom=${encodeURIComponent(nom)}&patient_id=${patientId}`),
  /** Charge le dossier du patient connecté par nom (session locale). */
  monDossierSession: async () => {
    const ps = getPatientSession()
    if (!ps?.patient_id) throw new Error('Non connecté — entrez votre nom sur la page de connexion.')
    return apiCall(
      `/reception/acces-patient/dossier?nom=${encodeURIComponent(ps.nom_recherche)}&patient_id=${ps.patient_id}`
    )
  },
  dossier: (id) => apiCall(`/reception/patients/${id}/dossier`),
  produits: (id) => apiCall(`/reception/patients/${id}/produits`),
  assurances: () => apiCall('/reception/assurances'),
  create: (data) => apiCall('/reception/patients', { method: 'POST', body: JSON.stringify(data) }),
  update: (id, data) => apiCall(`/reception/patients/${id}`, { method: 'PATCH', body: JSON.stringify(data) }),
  syncPortail: () => apiCall('/reception/patients/sync-portail', { method: 'POST' }),
}

export const chatService = {
  inbox: () => apiCall('/reception/chat/inbox'),
  messages: (patientId) => apiCall(`/reception/chat/messages?patient_id=${patientId}`),
  send: (data) => apiCall('/reception/chat/messages', { method: 'POST', body: JSON.stringify(data) }),
  demandeRdv: (data) => apiCall('/reception/chat/rdv-demande', { method: 'POST', body: JSON.stringify(data) }),
  unreadCount: (patientId) => {
    const q = patientId ? `?patient_id=${patientId}` : ''
    return apiCall(`/reception/chat/unread-count${q}`)
  },
  deleteConversation: (patientId) =>
    apiCall(`/reception/chat/conversation?patient_id=${patientId}`, { method: 'DELETE' }),
}

export const ordonnanceService = {
  list: (patientId) => apiCall(patientId ? `/consultations/ordonnances?patient_id=${patientId}` : '/consultations/ordonnances'),
  get: (id) => apiCall(`/consultations/ordonnances/${id}`),
  create: (data) => apiCall('/consultations/ordonnances', { method: 'POST', body: JSON.stringify(data) }),
}

export const consultationService = {
  list: () => apiCall('/consultations/'),
  create: (data) => apiCall('/consultations/', { method: 'POST', body: JSON.stringify(data) }),
  byPatient: (id) => apiCall(`/consultations/patient/${id}`),
}

export const clinicalService = {
  services: () => apiCall('/hospitalisations/services'),
  createService: (data) => apiCall('/hospitalisations/services', { method: 'POST', body: JSON.stringify(data) }),
  updateService: (id, data) => apiCall(`/hospitalisations/services/${id}`, { method: 'PATCH', body: JSON.stringify(data) }),
  toggleServicePause: (id) => apiCall(`/hospitalisations/services/${id}/pause`, { method: 'PATCH' }),
  chambres: () => apiCall('/hospitalisations/chambres'),
  lits: () => apiCall('/hospitalisations/lits'),
  createChambre: (data) => apiCall('/hospitalisations/chambres', { method: 'POST', body: JSON.stringify(data) }),
  updateChambreStatut: (id, statut) =>
    apiCall(`/hospitalisations/chambres/${id}/statut`, { method: 'PATCH', body: JSON.stringify({ statut }) }),
  createLit: (data) => apiCall('/hospitalisations/lits', { method: 'POST', body: JSON.stringify(data) }),
  admissions: () => apiCall('/hospitalisations/admissions'),
  hospitaliser: (data) => apiCall('/hospitalisations/admissions', { method: 'POST', body: JSON.stringify(data) }),
  sortieAdmission: (id) => apiCall(`/hospitalisations/admissions/${id}/sortie`, { method: 'POST' }),
  localisations: () => apiCall('/hospitalisations/localisations'),
  updateLocalisation: (data) => apiCall('/hospitalisations/localisations', { method: 'POST', body: JSON.stringify(data) }),
  localisationPatient: (id) => apiCall(`/hospitalisations/localisations/patient/${id}`),
  banqueSang: () => apiCall('/hospitalisations/banque-sang'),
  stockSanguin: () => apiCall('/hospitalisations/banque-sang/stock'),
  addPoche: (data) => apiCall('/hospitalisations/banque-sang', { method: 'POST', body: JSON.stringify(data) }),
}

export const pharmacyService = {
  medicaments: () => apiCall('/pharmacie/medicaments'),
  addMedicament: (data) => apiCall('/pharmacie/medicaments', { method: 'POST', body: JSON.stringify(data) }),
  updateMedicament: (id, data) => apiCall(`/pharmacie/medicaments/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  deleteMedicament: (id) => apiCall(`/pharmacie/medicaments/${id}`, { method: 'DELETE' }),
}

export const labService = {
  list: (patientId) => apiCall(patientId ? `/labo/analyses?patient_id=${patientId}` : '/labo/analyses'),
  create: (data) => apiCall('/labo/analyses', { method: 'POST', body: JSON.stringify(data) }),
  update: (id, data) => apiCall(`/labo/analyses/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  delete: (id) => apiCall(`/labo/analyses/${id}`, { method: 'DELETE' }),
  valider: (id) => apiCall(`/labo/analyses/${id}/valider`, { method: 'POST' }),
}

export const waitingService = {
  list: (typeFile = '') => {
    const q = typeFile ? `?type_file=${encodeURIComponent(typeFile)}` : ''
    return apiCall(`/hospitalisations/salle-attente${q}`)
  },
  add: (data) => apiCall('/hospitalisations/salle-attente', { method: 'POST', body: JSON.stringify(data) }),
  setStatut: (id, statut) => apiCall(`/hospitalisations/salle-attente/${id}/statut`, { method: 'PATCH', body: JSON.stringify({ statut }) }),
  remove: (id) => apiCall(`/hospitalisations/salle-attente/${id}`, { method: 'DELETE' }),
}

export const urgenceService = {
  list: () => apiCall('/hospitalisations/urgences'),
  create: (data) => apiCall('/hospitalisations/urgences', { method: 'POST', body: JSON.stringify(data) }),
  update: (id, data) => apiCall(`/hospitalisations/urgences/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  delete: (id) => apiCall(`/hospitalisations/urgences/${id}`, { method: 'DELETE' }),
}

export const doctorService = {
  list: (serviceId) => apiCall(serviceId ? `/personnel/medecins?service_id=${serviceId}` : '/personnel/medecins'),
  create: (data) => apiCall('/personnel/medecins', { method: 'POST', body: JSON.stringify(data) }),
  update: (id, data) => apiCall(`/personnel/medecins/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  toggle: (id) => apiCall(`/personnel/medecins/${id}/toggle`, { method: 'PATCH' }),
  delete: (id) => apiCall(`/personnel/medecins/${id}`, { method: 'DELETE' }),
}

export const nurseService = {
  list: (serviceId) => apiCall(serviceId ? `/personnel/infirmiers?service_id=${serviceId}` : '/personnel/infirmiers'),
  create: (data) => apiCall('/personnel/infirmiers', { method: 'POST', body: JSON.stringify(data) }),
  togglePause: (id) => apiCall(`/personnel/infirmiers/${id}/pause`, { method: 'PATCH' }),
  toggle: (id) => apiCall(`/personnel/infirmiers/${id}/toggle`, { method: 'PATCH' }),
  delete: (id) => apiCall(`/personnel/infirmiers/${id}`, { method: 'DELETE' }),
}

export const secretaireService = {
  list: () => apiCall('/personnel/secretaires'),
  togglePause: (id) => apiCall(`/personnel/secretaires/${id}/pause`, { method: 'PATCH' }),
}

export const billingService = {
  factures: () => apiCall('/caisse/factures'),
  creerFacture: (data) => apiCall('/caisse/factures', { method: 'POST', body: JSON.stringify(data) }),
  generer: (patientId) => apiCall(`/caisse/factures/patient/${patientId}`, { method: 'POST' }),
  payer: (id, data) => apiCall(`/caisse/factures/${id}/paiement`, { method: 'POST', body: JSON.stringify(data) }),
  paiements: () => apiCall('/caisse/paiements'),
}

export const bankService = {
  comptes: () => apiCall('/caisse/banque/comptes'),
  createCompte: (data) => apiCall('/caisse/banque/comptes', { method: 'POST', body: JSON.stringify(data) }),
  mouvements: () => apiCall('/caisse/banque/mouvements'),
  soldeTotal: () => apiCall('/caisse/banque/solde-total'),
}

export const privilegeService = {
  list: () => apiCall('/reception/clients-privilegies'),
  create: (data) => apiCall('/reception/clients-privilegies', { method: 'POST', body: JSON.stringify(data) }),
  toggle: (id) => apiCall(`/reception/clients-privilegies/${id}/toggle`, { method: 'PATCH' }),
}

export const agendaService = {
  rendezVous: (params = {}) => {
    const q = new URLSearchParams()
    if (params.medecin_id) q.set('medecin_id', params.medecin_id)
    if (params.service_id) q.set('service_id', params.service_id)
    if (params.patient_id) q.set('patient_id', params.patient_id)
    const qs = q.toString()
    return apiCall(`/reception/rendez-vous${qs ? `?${qs}` : ''}`)
  },
  createRdv: (data) => apiCall('/reception/rendez-vous', { method: 'POST', body: JSON.stringify(data) }),
  updateRdv: (id, data) => apiCall(`/reception/rendez-vous/${id}`, { method: 'PATCH', body: JSON.stringify(data) }),
  deleteRdv: (id) => apiCall(`/reception/rendez-vous/${id}`, { method: 'DELETE' }),
  patientsMedecin: (medecinId) => apiCall(`/reception/agenda/medecin/${medecinId}/patients`),
  notesPatient: (patientId, medecinId) => {
    const q = medecinId ? `?medecin_id=${medecinId}` : ''
    return apiCall(`/reception/patients/${patientId}/notes${q}`)
  },
  addNote: (patientId, data) => apiCall(`/reception/patients/${patientId}/notes`, { method: 'POST', body: JSON.stringify(data) }),
}

export const assuranceService = {
  list: () => apiCall('/reception/assurances'),
  create: (data) => apiCall('/reception/assurances', { method: 'POST', body: JSON.stringify(data) }),
}

export function saveSession(data) {
  clearPatientSession()
  localStorage.setItem('authToken', data.token || '')
  localStorage.setItem('user', JSON.stringify({
    username: data.username || data.email,
    email: data.email,
    role: data.role,
    role_label: data.role_label,
    user_id: data.user_id ?? null,
    patient_id: data.patient_id ?? null,
    service_id: data.service_id ?? null,
    can_access_all: data.can_access_all ?? false,
    can_manage_ui: data.can_manage_ui ?? false,
    can_manage_redirects: data.can_manage_redirects ?? false,
    medecin_service_ids: data.medecin_service_ids ?? [],
  }))
}

export function getUser() {
  const raw = localStorage.getItem('user')
  return raw ? JSON.parse(raw) : null
}

export function logout() {
  localStorage.removeItem('authToken')
  localStorage.removeItem('user')
  clearPatientSession()
}

export function loginPatientAndGo(patient, nomRecherche, router) {
  savePatientSession({
    patient_id: patient.id,
    nom: patient.nom,
    prenom: patient.prenom,
    nom_recherche: nomRecherche.trim(),
    nom_complet: `${patient.nom} ${patient.prenom}`,
  })
  router.replace('/mon-espace')
}

export function hasRole(roles) {
  const user = getUser()
  if (!user) return false
  return roles.includes(user.role)
}

/** Seul l'administrateur peut ajouter/modifier la structure (services, chambres…) */
export function canManageStructure() {
  const user = getUser()
  return user?.can_access_all === true || user?.role === 'ADMIN'
}

/** Administrateur : structure, design et redirections */
export function canManageUi() {
  return canManageStructure()
}

export function canManageRedirects() {
  return canManageStructure()
}

export function homeForRole(role) {
  return defaultPathForUser({ role, can_access_all: role === 'ADMIN' })
}

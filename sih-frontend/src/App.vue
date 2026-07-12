<template>
  <div v-if="isLoginPage">
    <router-view />
  </div>
  <div v-else class="flex min-h-screen bg-slate-950">
    <div
      v-if="sidebarOpen"
      class="fixed inset-0 bg-black/70 z-40 lg:hidden"
      aria-hidden="true"
      @click="sidebarOpen = false"
    />

    <!-- Sidebar -->
    <aside
      class="w-[min(100vw-3rem,18rem)] lg:w-72 fixed h-full z-50 flex flex-col app-sidebar border-r border-white/5 transition-transform duration-300 ease-out lg:translate-x-0"
      :class="sidebarOpen ? 'translate-x-0' : '-translate-x-full'"
    >
      <div class="p-6 border-b border-white/5">
        <div class="flex items-center gap-3">
          <div class="w-11 h-11 rounded-xl theme-accent-bg border theme-accent-border flex items-center justify-center text-xl">{{ appIcon }}</div>
          <div>
            <h1 class="text-lg font-bold text-white">{{ appName }}</h1>
            <p class="text-[10px] text-slate-500 uppercase tracking-widest">{{ appSlogan }}</p>
          </div>
        </div>
      </div>

      <nav class="flex-1 overflow-y-auto p-4 space-y-6">
        <div v-for="section in visibleMenu" :key="section.title">
          <p class="text-[10px] uppercase tracking-widest text-slate-600 px-3 mb-2">{{ section.title }}</p>
          <router-link v-for="link in section.links" :key="link.to" :to="link.to"
            class="flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm text-slate-400 hover:text-white hover:bg-white/5 transition mb-0.5 nav-link"
            active-class="nav-link-active"
            @click="closeSidebarMobile">
            <span>{{ link.icon }}</span>
            <span>{{ link.label }}</span>
          </router-link>
        </div>
      </nav>

      <div class="p-4 border-t border-white/5">
        <div class="flex items-center gap-3 px-3 py-2 rounded-xl bg-white/5">
          <div class="w-9 h-9 rounded-full theme-accent-bg flex items-center justify-center text-sm">{{ roleIcon }}</div>
          <div class="flex-1 min-w-0">
            <p class="text-sm text-white truncate">{{ displayName }}</p>
            <p class="text-[10px] theme-accent-text">{{ displayRole }}</p>
          </div>
          <button @click="doLogout" class="text-slate-500 hover:text-red-400 text-lg" title="Déconnexion">⏻</button>
        </div>
      </div>
    </aside>

    <!-- Main -->
    <div class="flex-1 w-full min-w-0 lg:ml-72">
      <header class="sticky top-0 z-30 px-4 sm:px-6 lg:px-8 py-3 sm:py-4 bg-slate-950/95 backdrop-blur border-b border-white/5 flex items-center justify-between gap-3">
        <div class="flex items-center gap-3 min-w-0">
          <button
            type="button"
            class="lg:hidden shrink-0 w-10 h-10 rounded-xl bg-white/5 border border-white/10 text-white text-lg"
            aria-label="Ouvrir le menu"
            @click="sidebarOpen = true"
          >
            ☰
          </button>
          <div class="min-w-0">
            <h2 class="text-white font-semibold truncate">{{ pageTitle }}</h2>
            <p class="text-xs text-slate-500 truncate">{{ today }}</p>
          </div>
        </div>
        <div class="flex items-center gap-2 sm:gap-3 shrink-0">
          <NotificationBell v-if="!isPatientMode" />
          <span class="status-pill text-xs hidden sm:inline-flex">
            <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
            Système opérationnel
          </span>
        </div>
      </header>
      <main
        class="p-4 sm:p-6 lg:p-8 main-backdrop min-h-[calc(100vh-4rem)]"
        :style="{ '--page-bg-image': `url('${pageBackground}')` }"
      >
        <PageFlowNav />
        <router-view :key="route.fullPath" />
      </main>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getUser, logout, getPatientSession, isPatientAccess } from './services/api.js'
import { getMenuForUser, PAGE_TITLES } from './config/navigation.js'
import { getPageBackground } from './config/pageBackgrounds.js'
import { getCachedBranding, BRANDING_EVENT } from './utils/branding.js'
import PageFlowNav from './components/PageFlowNav.vue'
import NotificationBell from './components/NotificationBell.vue'

const route = useRoute()
const router = useRouter()
const user = ref(getUser())
const patientSession = ref(getPatientSession())
const sidebarOpen = ref(false)

const PATIENT_MENU = [{
  title: 'Mon espace patient',
  links: [
    { to: '/mon-espace', icon: '🧑', label: 'Accueil' },
    { to: '/patients', icon: '📊', label: 'Mon statut' },
    { to: '/ordonnances', icon: '💊', label: 'Mes ordonnances' },
    { to: '/lab', icon: '🔬', label: 'Mon laboratoire' },
    { to: '/localisation', icon: '📍', label: 'Ma localisation' },
  ],
}]

router.afterEach(() => {
  user.value = getUser()
  patientSession.value = getPatientSession()
  sidebarOpen.value = false
})

function closeSidebarMobile() {
  if (typeof window !== 'undefined' && window.innerWidth < 1024) {
    sidebarOpen.value = false
  }
}

function refreshMenu() {
  user.value = getUser()
}

if (typeof window !== 'undefined') {
  window.addEventListener('sghl-redirect-updated', refreshMenu)
  window.addEventListener(BRANDING_EVENT, (e) => {
    branding.value = e.detail || getCachedBranding()
  })
}

const isLoginPage = computed(() => route.path === '/login')
const isPatientMode = computed(() => isPatientAccess())

const roleIcons = {
  ADMIN: '⚙️', SECRETAIRE_GENERALE: '📋', MEDECIN: '👨‍⚕️', INFIRMIER: '💉', SECRETAIRE: '📋',
  RECEPTIONNISTE: '🏪', BIOLOGISTE: '🔬', PHARMACIEN: '💊', PATIENT: '🧑',
}
const roleIcon = computed(() => {
  if (isPatientMode.value) return '🧑'
  return roleIcons[user.value?.role] || '👤'
})

const displayName = computed(() => {
  if (isPatientMode.value) return patientSession.value?.nom_complet || user.value?.username || user.value?.email || 'Patient'
  return user.value?.username
})

const displayRole = computed(() => {
  if (isPatientMode.value) return 'Espace patient'
  return user.value?.role_label
})

const branding = ref(getCachedBranding())

const appName = computed(() => branding.value.nom_application)
const appSlogan = computed(() => {
  const s = branding.value.slogan_application || ''
  return s.length > 42 ? `${s.slice(0, 40)}…` : s
})
const appIcon = computed(() => branding.value.icone_application || '🏥')

const today = new Date().toLocaleDateString('fr-FR', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' })

const visibleMenu = computed(() => {
  if (isPatientMode.value) return PATIENT_MENU
  return getMenuForUser(user.value)
})

const pageTitle = computed(() => {
  if (route.path.startsWith('/patients/') && route.path !== '/patients') {
    return PAGE_TITLES['/patients/:id'] || 'Dossier patient'
  }
  return PAGE_TITLES[route.path] || 'SGHL'
})

const pageBackground = computed(() => getPageBackground(route.path))

function doLogout() {
  logout()
  router.push('/login')
}
</script>

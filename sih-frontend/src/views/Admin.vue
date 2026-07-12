<template>
  <div class="space-y-6">
    <div class="page-card admin-hero p-8">
      <div class="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 class="text-3xl font-bold text-white flex items-center gap-3">
            <span>{{ branding.icone_application }}</span>
            Panneau d'administration
          </h1>
          <p class="text-slate-400 text-sm mt-2">
            Contrôle total : identité, design, redirections, utilisateurs et notifications
          </p>
        </div>
        <div class="flex flex-wrap gap-2">
          <router-link to="/users" class="btn-save text-sm rounded-xl px-4 py-2">👤 Utilisateurs & OTP</router-link>
          <router-link to="/settings" class="btn-save text-sm rounded-xl px-4 py-2 opacity-90">🏥 Paramètres hôpital</router-link>
          <router-link to="/departments" class="btn-save text-sm rounded-xl px-4 py-2 opacity-90">🏢 Services</router-link>
        </div>
      </div>
    </div>

    <div v-if="msg" class="p-3 rounded-xl bg-teal-500/10 border border-teal-500/30 text-teal-300 text-sm">{{ msg }}</div>
    <div v-if="error" class="p-3 rounded-xl bg-red-500/10 border border-red-500/30 text-red-300 text-sm">{{ error }}</div>

    <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
      <div v-for="stat in stats" :key="stat.label" class="stat-card-admin">
        <p class="text-2xl font-bold text-white">{{ stat.value }}</p>
        <p class="text-xs text-slate-400 mt-1">{{ stat.label }}</p>
      </div>
    </div>

    <div class="flex flex-wrap gap-2 pb-2 border-b border-white/10">
      <button
        v-for="tab in tabs"
        :key="tab.id"
        type="button"
        @click="activeTab = tab.id"
        class="px-5 py-3 rounded-t-xl text-sm font-semibold border-b-2 transition"
        :class="activeTab === tab.id ? 'admin-tab-active border-b-2' : 'text-slate-400 hover:text-white border-b-transparent'"
      >
        {{ tab.icon }} {{ tab.label }}
      </button>
    </div>

    <!-- IDENTITÉ -->
    <div v-show="activeTab === 'identity'" class="space-y-5 animate-fadeIn">
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <form class="page-card p-6 space-y-4" @submit.prevent="saveBranding">
          <h3 class="text-white font-bold text-lg">🏷️ Identité de l'application</h3>
          <label class="form-field"><span>Nom court (sidebar, titre)</span>
            <input v-model="branding.nom_application" class="modal-input" required maxlength="80" /></label>
          <label class="form-field"><span>Slogan / sous-titre</span>
            <input v-model="branding.slogan_application" class="modal-input" maxlength="200" /></label>
          <label class="form-field"><span>Nom de l'établissement</span>
            <input v-model="branding.nom_hopital" class="modal-input" maxlength="200" /></label>
          <label class="form-field"><span>Icône application</span>
            <div class="flex flex-wrap gap-2 mt-2">
              <button
                v-for="icon in iconOptions"
                :key="icon"
                type="button"
                class="w-10 h-10 rounded-xl border text-xl transition"
                :class="branding.icone_application === icon ? 'border-teal-400 bg-teal-500/20' : 'border-white/10 bg-white/5 hover:bg-white/10'"
                @click="branding.icone_application = icon"
              >{{ icon }}</button>
            </div>
          </label>
          <button type="submit" class="btn-save" :disabled="saving">{{ saving ? 'Enregistrement…' : '💾 Enregistrer l\'identité' }}</button>
        </form>

        <div class="preview-panel p-6">
          <p class="text-xs uppercase tracking-widest text-slate-500 mb-4">Aperçu en direct</p>
          <div class="flex items-center gap-3 mb-6">
            <div class="w-14 h-14 rounded-2xl theme-accent-bg border theme-accent-border flex items-center justify-center text-3xl">
              {{ branding.icone_application }}
            </div>
            <div>
              <p class="text-xl font-bold text-white">{{ branding.nom_application }}</p>
              <p class="text-sm theme-accent-text">{{ branding.slogan_application }}</p>
            </div>
          </div>
          <p class="text-slate-400 text-sm mb-2">Établissement</p>
          <p class="text-white font-medium">{{ branding.nom_hopital }}</p>
          <div class="mt-6 p-4 rounded-xl bg-white/5 border border-white/10">
            <p class="text-xs text-slate-500">Titre navigateur</p>
            <p class="text-sm text-slate-300 mt-1">{{ previewTitle }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- DESIGN -->
    <div v-show="activeTab === 'design'" class="space-y-5 animate-fadeIn">
      <div class="page-card p-6">
        <h3 class="text-white font-bold text-lg mb-4">🎨 Thème couleur</h3>
        <div class="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-8 gap-3">
          <button
            v-for="(theme, key) in themes"
            :key="key"
            type="button"
            class="theme-swatch p-3 border text-left"
            :class="branding.theme_ui === key ? 'theme-swatch-active border-white/40 bg-white/10' : 'border-white/10 bg-white/5'"
            @click="pickTheme(key)"
          >
            <div class="w-full h-8 rounded-lg mb-2" :style="{ background: theme.accent }"></div>
            <p class="text-white text-xs">{{ theme.label }}</p>
          </button>
        </div>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div class="page-card p-6 space-y-4">
          <h3 class="text-white font-bold text-lg">✨ Style des cartes</h3>
          <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <button
              v-for="(cfg, key) in cardStyles"
              :key="key"
              type="button"
              class="p-4 rounded-xl border text-sm transition"
              :class="styleForm.cardStyle === key ? 'border-teal-400 bg-teal-500/10 text-teal-200' : 'border-white/10 bg-white/5 text-slate-300'"
              @click="styleForm.cardStyle = key"
            >{{ cfg.label }}</button>
          </div>

          <label class="form-field"><span>Arrondi des cartes</span>
            <select v-model="styleForm.cardRadius" class="modal-input">
              <option v-for="r in radiusOptions" :key="r.value" :value="r.value">{{ r.label }}</option>
            </select>
          </label>

          <label class="form-field"><span>Image fond connexion (URL)</span>
            <input v-model="styleForm.loginBackground" class="modal-input" placeholder="https://..." /></label>

          <div class="grid grid-cols-2 gap-3">
            <label class="form-field"><span>Couleur accent custom</span>
              <input v-model="styleForm.customAccent" type="color" class="modal-input h-12 p-1" /></label>
            <label class="form-field"><span>Accent clair</span>
              <input v-model="styleForm.customAccentLight" type="color" class="modal-input h-12 p-1" /></label>
          </div>

          <label class="form-field"><span>Taille texte (%)</span>
            <input v-model.number="styleForm.fontScale" type="range" min="90" max="115" step="1" class="w-full accent-teal-500" />
            <span class="text-slate-400 text-xs">{{ styleForm.fontScale }}%</span>
          </label>

          <div class="space-y-3">
            <label class="flex items-center gap-3 cursor-pointer">
              <input v-model="styleForm.animations" type="checkbox" class="w-5 h-5 accent-teal-500" />
              <span class="text-white text-sm">Animations fluides</span>
            </label>
            <label class="flex items-center gap-3 cursor-pointer">
              <input v-model="styleForm.compactMode" type="checkbox" class="w-5 h-5 accent-teal-500" />
              <span class="text-white text-sm">Mode compact</span>
            </label>
            <label class="flex items-center gap-3 cursor-pointer">
              <input v-model="styleForm.sidebarGlow" type="checkbox" class="w-5 h-5 accent-teal-500" />
              <span class="text-white text-sm">Lueur sidebar</span>
            </label>
            <label class="flex items-center gap-3 cursor-pointer">
              <input v-model="styleForm.headerBlur" type="checkbox" class="w-5 h-5 accent-teal-500" />
              <span class="text-white text-sm">En-tête flou (glass)</span>
            </label>
          </div>

          <div class="flex flex-wrap gap-2 pt-2">
            <button type="button" class="btn-save" :disabled="saving" @click="saveBranding">💾 Appliquer le design</button>
            <button type="button" class="btn-cancel" @click="resetStyle">↩️ Style par défaut</button>
          </div>
        </div>

        <div class="preview-panel p-6 space-y-4">
          <p class="text-xs uppercase tracking-widest text-slate-500">Aperçu carte</p>
          <div class="page-card p-5">
            <p class="text-white font-semibold">Carte exemple</p>
            <p class="text-slate-400 text-sm mt-2">Le style choisi s'applique à toute l'application.</p>
            <button type="button" class="btn-save mt-4 text-sm">Bouton action</button>
          </div>
          <div class="page-card p-4 flex items-center gap-3">
            <span class="w-3 h-3 rounded-full bg-emerald-400 animate-pulse"></span>
            <span class="text-slate-300 text-sm">Système opérationnel — thème {{ themes[branding.theme_ui]?.label }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- REDIRECTIONS -->
    <div v-show="activeTab === 'redirects'" class="space-y-5 animate-fadeIn">
      <div class="page-card p-6">
        <h3 class="text-white font-bold text-lg mb-2">🔀 Page d'accueil par rôle</h3>
        <p class="text-slate-400 text-sm mb-4">Définissez où chaque rôle arrive après connexion.</p>
        <div class="space-y-3">
          <div v-for="role in rolesNav" :key="role.code" class="flex flex-wrap items-center gap-3 p-3 rounded-xl bg-white/5">
            <span class="text-white text-sm w-40">{{ role.label }}</span>
            <select v-model="redirectForm[role.code]" class="modal-input flex-1 min-w-[200px]">
              <option value="">Parcours par défaut</option>
              <option v-for="p in pagesForRole(role.code)" :key="p.path" :value="p.path">{{ p.title }}</option>
            </select>
          </div>
        </div>
        <label class="flex items-center gap-3 mt-4 cursor-pointer">
          <input v-model="autoAdvance" type="checkbox" class="w-5 h-5 accent-teal-500" />
          <span class="text-white text-sm">Avancer automatiquement après une action réussie</span>
        </label>
        <div class="flex gap-2 mt-4">
          <button type="button" class="btn-save" @click="saveRedirects">💾 Enregistrer redirections</button>
          <button type="button" class="btn-cancel" @click="resetRedirects">↩️ Réinitialiser</button>
        </div>
      </div>
    </div>

    <!-- UTILISATEURS -->
    <div v-show="activeTab === 'users'" class="space-y-4 animate-fadeIn">
      <div class="page-card overflow-hidden">
        <div class="p-4 flex justify-between items-center border-b border-white/10">
          <h3 class="text-white font-bold">👤 Comptes personnel ({{ users.length }})</h3>
          <router-link to="/users" class="btn-save text-sm">Gérer tout →</router-link>
        </div>
        <div v-if="loadingUsers" class="p-8 text-center text-slate-400">Chargement…</div>
        <div v-else class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead>
              <tr class="bg-white/5 border-b border-white/10">
                <th class="px-4 py-3 text-left text-slate-300">Utilisateur</th>
                <th class="px-4 py-3 text-left text-slate-300">Email</th>
                <th class="px-4 py-3 text-left text-slate-300">Rôle</th>
                <th class="px-4 py-3 text-left text-slate-300">Statut</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="u in users.slice(0, 15)" :key="u.id" class="border-b border-white/10 hover:bg-white/5">
                <td class="px-4 py-3 text-white">{{ u.username }}</td>
                <td class="px-4 py-3 text-slate-400">{{ u.email }}</td>
                <td class="px-4 py-3"><span class="badge badge-company">{{ u.role_label || u.role }}</span></td>
                <td class="px-4 py-3">
                  <span :class="u.is_active ? 'badge badge-success' : 'badge badge-warning'">
                    {{ u.is_active ? 'Actif' : 'Inactif' }}{{ u.en_pause ? ' · Pause' : '' }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- NOTIFICATIONS -->
    <div v-show="activeTab === 'notifications'" class="space-y-4 animate-fadeIn">
      <form class="page-card p-6 space-y-3" @submit.prevent="sendNotification">
        <h3 class="text-white font-bold text-lg">🔔 Publier une notification</h3>
        <input v-model="notifForm.title" class="modal-input" placeholder="Titre" required />
        <textarea v-model="notifForm.message" class="modal-input" rows="3" placeholder="Message" required />
        <select v-model="notifForm.level" class="modal-input">
          <option value="INFO">Information</option>
          <option value="SUCCESS">Succès</option>
          <option value="WARNING">Avertissement</option>
          <option value="DANGER">Urgent</option>
        </select>
        <button type="submit" class="btn-save" :disabled="savingNotif">{{ savingNotif ? 'Envoi…' : 'Publier' }}</button>
      </form>
      <div class="space-y-2">
        <div v-for="n in notifications" :key="n.id" class="page-card p-4 border-l-4"
          :class="n.level === 'DANGER' ? 'border-l-red-500' : n.level === 'WARNING' ? 'border-l-amber-500' : 'border-l-teal-500'">
          <p class="text-white font-semibold">{{ n.title }}</p>
          <p class="text-slate-400 text-sm mt-1">{{ n.message }}</p>
        </div>
        <p v-if="!notifications.length" class="text-slate-500 text-sm text-center py-6">Aucune notification récente</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { coreService } from '../services/api.js'
import { THEMES } from '../utils/theme.js'
import {
  applyBranding,
  CARD_STYLES,
  DEFAULT_STYLE,
  ICON_OPTIONS,
  RADIUS_OPTIONS,
  normalizeBranding,
} from '../utils/branding.js'
import {
  ROLES_WITH_NAV,
  ROLE_LABELS,
  basePagesForRole,
} from '../config/navigation.js'
import {
  getRedirectConfig,
  setRoleHomeOverride,
  resetRedirectConfig,
  getAutoAdvance,
  setAutoAdvance,
} from '../utils/redirectConfig.js'

const tabs = [
  { id: 'identity', label: 'Identité', icon: '🏷️' },
  { id: 'design', label: 'Design & Style', icon: '🎨' },
  { id: 'redirects', label: 'Redirections', icon: '🔀' },
  { id: 'users', label: 'Utilisateurs', icon: '👤' },
  { id: 'notifications', label: 'Notifications', icon: '🔔' },
]

const activeTab = ref('identity')
const themes = THEMES
const cardStyles = CARD_STYLES
const radiusOptions = RADIUS_OPTIONS
const iconOptions = ICON_OPTIONS
const rolesNav = ROLES_WITH_NAV.map((code) => ({ code, label: ROLE_LABELS[code] }))

const branding = ref(normalizeBranding())
const styleForm = ref({ ...DEFAULT_STYLE })
const redirectForm = ref({})
const autoAdvance = ref(getAutoAdvance())

const users = ref([])
const notifications = ref([])
const loadingUsers = ref(false)
const saving = ref(false)
const savingNotif = ref(false)
const msg = ref('')
const error = ref('')

const notifForm = ref({ title: '', message: '', level: 'INFO' })

const stats = computed(() => [
  { label: 'Utilisateurs actifs', value: users.value.filter((u) => u.is_active).length },
  { label: 'Thème actif', value: themes[branding.value.theme_ui]?.label?.split(' ')[0] || 'Teal' },
  { label: 'Notifications', value: notifications.value.length },
  { label: 'Application', value: branding.value.nom_application },
])

const previewTitle = computed(() => {
  const b = branding.value
  return `${b.nom_application} — ${b.slogan_application}`
})

function pagesForRole(role) {
  return basePagesForRole(role)
}

function loadRedirectForm() {
  const cfg = getRedirectConfig()
  const form = {}
  for (const r of rolesNav) {
    form[r.code] = cfg[r.code]?.homePath || ''
  }
  redirectForm.value = form
  autoAdvance.value = getAutoAdvance()
}

async function loadAll() {
  error.value = ''
  loadingUsers.value = true
  try {
    const settings = await coreService.settings()
    branding.value = normalizeBranding(settings)
    styleForm.value = { ...DEFAULT_STYLE, ...(settings.config_style || {}) }
    applyBranding(branding.value)

    const [userList, notifs] = await Promise.all([
      coreService.users(),
      coreService.notifications(false),
    ])
    users.value = userList
    notifications.value = notifs.slice(0, 10)
  } catch (e) {
    error.value = e.message
  } finally {
    loadingUsers.value = false
  }
  loadRedirectForm()
}

function pickTheme(key) {
  branding.value.theme_ui = key
  applyBranding({ ...branding.value, config_style: styleForm.value })
}

async function saveBranding() {
  saving.value = true
  msg.value = ''
  error.value = ''
  try {
    const payload = {
      nom_application: branding.value.nom_application,
      slogan_application: branding.value.slogan_application,
      nom_hopital: branding.value.nom_hopital,
      icone_application: branding.value.icone_application,
      theme_ui: branding.value.theme_ui,
      config_style: { ...styleForm.value },
    }
    const data = await coreService.updateSettings(payload)
    branding.value = normalizeBranding(data)
    applyBranding(branding.value)
    msg.value = '✓ Identité et design enregistrés — visible pour tous les utilisateurs.'
  } catch (e) {
    error.value = e.message
  } finally {
    saving.value = false
  }
}

function resetStyle() {
  styleForm.value = { ...DEFAULT_STYLE }
  branding.value.theme_ui = 'teal'
  applyBranding({ ...branding.value, config_style: styleForm.value })
}

function saveRedirects() {
  for (const r of rolesNav) {
    setRoleHomeOverride(r.code, redirectForm.value[r.code] || null)
  }
  setAutoAdvance(autoAdvance.value)
  msg.value = '✓ Redirections mises à jour.'
}

function resetRedirects() {
  resetRedirectConfig()
  loadRedirectForm()
  msg.value = 'Redirections réinitialisées.'
}

async function sendNotification() {
  savingNotif.value = true
  try {
    await coreService.createNotification(notifForm.value)
    notifForm.value = { title: '', message: '', level: 'INFO' }
    notifications.value = (await coreService.notifications(false)).slice(0, 10)
    msg.value = 'Notification publiée.'
  } catch (e) {
    error.value = e.message
  } finally {
    savingNotif.value = false
  }
}

watch(styleForm, () => {
  applyBranding({ ...branding.value, config_style: styleForm.value })
}, { deep: true })

onMounted(loadAll)
</script>

<style scoped>
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
.animate-fadeIn { animation: fadeIn 0.3s ease-out; }
.form-field span {
  display: block;
  font-size: 0.75rem;
  color: #94a3b8;
  margin-bottom: 0.35rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
</style>

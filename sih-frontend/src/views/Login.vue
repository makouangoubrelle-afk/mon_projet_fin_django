<template>
  <div class="min-h-screen flex items-center justify-center p-4 relative overflow-hidden">
    <div
      class="absolute inset-0 bg-cover bg-center"
      :style="{ backgroundImage: `linear-gradient(rgba(15,23,42,0.88), rgba(15,23,42,0.94)), var(--app-login-bg)` }"
    ></div>
    <div class="absolute inset-0 opacity-30" style="background-image: radial-gradient(circle at 20% 50%, #14b8a6 0%, transparent 50%), radial-gradient(circle at 80% 20%, #0ea5e9 0%, transparent 40%)"></div>

    <div class="relative w-full max-w-5xl grid md:grid-cols-2 gap-0 rounded-3xl overflow-hidden shadow-2xl border border-white/10">
      <div
        class="hidden md:flex flex-col justify-between p-10 bg-cover bg-center relative border-r border-white/10"
        style="background-image: linear-gradient(rgba(15,23,42,0.75), rgba(15,23,42,0.85)), url('https://images.unsplash.com/photo-1559839734-2b71ea197ec2?w=800&q=80')"
      >
        <div>
          <div class="flex items-center gap-3 mb-8">
            <div class="w-14 h-14 rounded-2xl theme-accent-bg border theme-accent-border flex items-center justify-center text-3xl backdrop-blur">{{ appIcon }}</div>
            <div>
              <h1 class="text-2xl font-bold text-white tracking-tight">{{ appName }}</h1>
              <p class="theme-accent-text text-sm opacity-90">{{ appSlogan }}</p>
            </div>
          </div>
          <h2 class="text-3xl font-bold text-white leading-tight mb-4">Connexion<br/>par Email OTP</h2>
          <p class="text-slate-300 text-sm leading-relaxed mb-6">
            Vérification par code à usage unique (One Time Password) envoyé par email — le même principe que la validation WhatsApp, mais via votre boîte mail.
          </p>
          <ol class="space-y-3">
            <li v-for="(s, i) in workflowSteps" :key="i" class="flex gap-3 text-sm">
              <span
                class="shrink-0 w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold border"
                :class="workflowStepClass(i + 1)"
              >{{ i + 1 }}</span>
              <div>
                <p class="text-white font-medium">{{ s.title }}</p>
                <p class="text-slate-400 text-xs leading-relaxed">{{ s.detail }}</p>
              </div>
            </li>
          </ol>
        </div>
        <div class="space-y-3 mt-8">
          <div v-for="item in features" :key="item" class="flex items-center gap-2 text-sm text-slate-300">
            <span class="text-teal-400">✓</span> {{ item }}
          </div>
        </div>
      </div>

      <div class="p-8 md:p-10 bg-slate-900/90 backdrop-blur">
        <div class="md:hidden flex items-center gap-3 mb-6">
          <div class="w-12 h-12 rounded-xl theme-accent-bg border theme-accent-border flex items-center justify-center text-2xl">{{ appIcon }}</div>
          <div>
            <h1 class="text-lg font-bold text-white">{{ appName }}</h1>
            <p class="text-slate-400 text-xs">{{ appSlogan }}</p>
          </div>
        </div>

        <h3 class="text-xl font-bold text-white mb-1">{{ step === 'email' ? 'Étape 1 — Identifiant' : 'Étape 2 — Vérification' }}</h3>
        <p v-if="step === 'email'" class="text-slate-400 text-sm mb-4">
          Saisissez votre adresse email. Le serveur générera un code à 6 chiffres et vous l'enverra par mail.
        </p>
        <p v-else class="text-slate-400 text-sm mb-4">
          Entrez le code reçu par email à
          <span class="text-white font-medium">{{ email }}</span>
          (valable {{ otpMinutes }} minutes).
        </p>

        <p v-if="step === 'email' && selectedRole === 'ADMIN'" class="text-xs text-teal-400/90 mb-4">
          ✓ Administrateur : le code sera envoyé à votre adresse email. Accès à toutes les sections après validation.
        </p>
        <p v-else-if="step === 'email' && authConfig.email_live" class="text-xs text-teal-400/90 mb-4">
          ✓ Le code sera envoyé dans votre boîte mail à chaque connexion.
        </p>

        <div v-if="serverDown" class="mb-4 p-4 rounded-xl bg-red-500/10 border border-red-500/30 text-red-300 text-sm">
          <p class="font-medium mb-1">Serveur indisponible</p>
          <p class="text-xs mb-2">Le backend Django doit tourner sur le port <strong>8001</strong> avant d'ouvrir l'interface.</p>
          <p class="text-xs">Terminal 1 : <code class="text-red-200">cd mon_projet_fin_django</code></p>
          <p class="text-xs">Puis : <code class="text-red-200">python manage.py runserver 8001</code></p>
          <p class="text-xs mt-2">Terminal 2 : <code class="text-red-200">cd sih-frontend</code> puis <code class="text-red-200">npm run dev</code></p>
          <p class="text-xs mt-2">Ouvrez ensuite <code class="text-red-200">http://localhost:5173</code> (pas le port 8001).</p>
          <button
            type="button"
            @click="checkServer"
            :disabled="serverChecking"
            class="mt-3 w-full py-2 rounded-xl border border-red-400/40 text-red-200 text-sm hover:bg-red-500/10 disabled:opacity-50"
          >
            {{ serverChecking ? 'Vérification...' : 'Réessayer la connexion' }}
          </button>
        </div>

        <div v-if="error" class="mb-4 p-3 rounded-xl bg-red-500/10 border border-red-500/30 text-red-300 text-sm whitespace-pre-line">{{ error }}</div>
        <div v-if="info" class="mb-4 p-3 rounded-xl bg-teal-500/10 border border-teal-500/30 text-teal-300 text-sm whitespace-pre-line">{{ info }}</div>

        <form v-if="step === 'email'" @submit.prevent="sendCode" class="space-y-4">
          <div>
            <label class="block text-xs text-slate-400 mb-1 uppercase tracking-wider">Je me connecte en tant que</label>
            <select
              v-model="selectedRole"
              class="w-full px-4 py-3 rounded-xl bg-slate-800 border border-slate-700 text-white focus:border-teal-500 focus:outline-none transition"
            >
              <option v-for="r in loginRoles" :key="r.code" :value="r.code">{{ r.label }}</option>
            </select>
          </div>

          <div>
            <label class="block text-xs text-slate-400 mb-1 uppercase tracking-wider">Adresse email</label>
            <input
              v-model="email"
              type="email"
              required
              autocomplete="email"
              placeholder="makouangoubrelle@gmail.com"
              class="w-full px-4 py-3 rounded-xl bg-slate-800 border border-slate-700 text-white placeholder-slate-500 focus:border-teal-500 focus:outline-none transition"
            />
            <p v-if="lookupLoading" class="text-slate-500 text-xs mt-1">Vérification…</p>
            <p v-else-if="lookupInfo.found && lookupInfo.otp_hint" class="text-teal-400/90 text-xs mt-1">
              ✓ {{ lookupInfo.otp_hint }}
            </p>
            <p v-else-if="lookupInfo.found" class="text-teal-400/90 text-xs mt-1">
              ✓ {{ lookupInfo.role_label || 'Profil' }} — code envoyé à {{ email }}
            </p>
            <p v-else-if="email.trim().includes('@')" class="text-slate-400 text-xs mt-1">
              Un code sera envoyé à cette adresse email.
            </p>
          </div>

          <button type="submit" :disabled="loading"
            class="w-full py-3 rounded-xl bg-gradient-to-r from-teal-500 to-cyan-500 text-white font-semibold hover:from-teal-400 hover:to-cyan-400 transition disabled:opacity-50 shadow-lg shadow-teal-500/20">
            {{ loading ? 'Envoi en cours...' : 'Envoyer le code par email' }}
          </button>
        </form>

        <form v-else @submit.prevent="verifyCode" class="space-y-4">
          <div class="p-4 rounded-xl bg-white/5 border border-white/10 text-center">
            <p class="text-slate-400 text-sm mb-1">Code de vérification envoyé à</p>
            <p class="text-white font-semibold break-all">{{ email }}</p>
            <p v-if="roleLabel" class="text-teal-400 text-xs mt-2">{{ roleLabel }}</p>
            <p v-if="deliveryLive" class="text-teal-300 text-xs mt-3 leading-relaxed">
              {{ deliveryChannel === 'sms'
                ? 'Consultez les SMS sur votre téléphone.'
                : 'Consultez votre boîte mail sur votre téléphone (vérifiez les spams).' }}
            </p>
            <p v-else-if="!debugCode" class="text-slate-500 text-xs mt-3">
              En attente du code dans votre boîte mail…
            </p>
          </div>

          <div v-if="debugCode && !deliveryLive" class="p-4 rounded-xl bg-amber-500/10 border border-amber-500/40 text-center">
            <p class="text-amber-200 text-xs uppercase tracking-wider mb-1">Votre code de connexion</p>
            <p class="text-3xl font-bold text-white tracking-[0.3em] select-all">{{ debugCode }}</p>
            <button type="button" class="text-amber-200/90 text-xs underline mt-2" @click="fillFromDebugCode">
              Remplir automatiquement
            </button>
          </div>

          <div>
            <label class="block text-xs text-slate-400 mb-3 uppercase tracking-wider text-center">Saisissez votre code à 6 chiffres</label>
            <div class="flex justify-center gap-2 sm:gap-3">
              <input
                v-for="(_, i) in otpDigits"
                :key="`otp-${i}`"
                :ref="el => setOtpRef(el, i)"
                v-model="otpDigits[i]"
                type="text"
                inputmode="numeric"
                pattern="[0-9]*"
                autocomplete="one-time-code"
                maxlength="1"
                class="otp-digit-input"
                :aria-label="`Chiffre ${i + 1}`"
                @input="onDigitInput(i, $event)"
                @keydown="onDigitKeydown(i, $event)"
                @paste="onOtpPaste"
              />
            </div>
            <p class="text-center text-xs text-slate-500 mt-3">Tapez chaque chiffre ou collez le code reçu</p>
          </div>

          <button type="submit" :disabled="loading || verifying || otpCode.length !== 6"
            class="w-full py-3 rounded-xl bg-gradient-to-r from-teal-500 to-cyan-500 text-white font-semibold disabled:opacity-50">
            {{ loading ? 'Vérification...' : 'Valider et accéder' }}
          </button>

          <div class="flex gap-2">
            <button type="button" @click="goBack" class="flex-1 py-2 text-slate-400 text-sm hover:text-white border border-slate-700 rounded-xl">
              ← Changer d'email
            </button>
            <button type="button" @click="sendCode" :disabled="loading || resendCooldown > 0"
              class="flex-1 py-2 text-teal-400 text-sm hover:text-teal-300 border border-teal-500/30 rounded-xl disabled:opacity-50">
              {{ resendCooldown > 0 ? `Renvoyer (${resendCooldown}s)` : 'Renvoyer le code' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { authService, finishLogin, isAuthSuccess, logout } from '../services/api.js'
import { extractEmail } from '../utils/email.js'
import { getCachedBranding, BRANDING_EVENT } from '../utils/branding.js'

const router = useRouter()
const route = useRoute()
const branding = ref(getCachedBranding())
const appName = computed(() => branding.value.nom_application)
const appSlogan = computed(() => branding.value.slogan_application)
const appIcon = computed(() => branding.value.icone_application || '🏥')

const step = ref('email')
const email = ref('')
const selectedRole = ref('MEDECIN')
const deliveryChannel = ref('email')
const loginRoles = ref([
  { code: 'ADMIN', label: 'Administrateur' },
  { code: 'SECRETAIRE_GENERALE', label: 'Secrétaire générale' },
  { code: 'MEDECIN', label: 'Médecin' },
  { code: 'INFIRMIER', label: 'Infirmier' },
  { code: 'SECRETAIRE', label: 'Secrétaire' },
  { code: 'RECEPTIONNISTE', label: 'Réceptionniste' },
  { code: 'PATIENT', label: 'Patient' },
])
const deliveryLive = ref(false)
const authConfig = ref({ hint: '', email_live: false, otp_validity_minutes: 5 })
const otpMinutes = computed(() => authConfig.value.otp_validity_minutes || 5)
const lookupInfo = ref({ found: false })
const lookupLoading = ref(false)
const otpCode = ref('')
const otpDigits = ref(['', '', '', '', '', ''])
const otpRefs = ref([])
const roleLabel = ref('')
const debugCode = ref('')
const loading = ref(false)
const error = ref('')
const info = ref('')
const serverDown = ref(false)
const serverChecking = ref(false)
const resendCooldown = ref(0)
const verifying = ref(false)
let cooldownTimer = null
let lookupTimer = null

const workflowSteps = [
  { title: 'Saisie de l\'identifiant', detail: 'L\'utilisateur entre son adresse email sur la page de connexion.' },
  { title: 'Génération du code', detail: 'Le serveur crée un code aléatoire à 6 chiffres, l\'enregistre en base avec une date d\'expiration.' },
  { title: 'Envoi de l\'email', detail: 'Le système envoie automatiquement le code à l\'adresse email saisie.' },
  { title: 'Vérification', detail: 'L\'utilisateur saisit le code reçu dans l\'application.' },
  { title: 'Validation', detail: 'Si le code est correct et non expiré, l\'accès est autorisé et une session est créée.' },
]

const features = [
  'Code à usage unique (OTP)',
  'Expiration automatique après quelques minutes',
  'Session sécurisée après validation',
  'Accès selon le rôle (admin, médecin, patient…)',
]

function workflowStepClass(stepNum) {
  const current = step.value === 'email' ? 1 : 4
  if (stepNum < current) return 'bg-teal-500/20 border-teal-500/50 text-teal-300'
  if (stepNum === current || (step.value === 'otp' && stepNum <= 4)) return 'bg-teal-500/30 border-teal-400 text-white'
  return 'bg-slate-800 border-slate-600 text-slate-400'
}

function setOtpRef(el, index) {
  if (el) otpRefs.value[index] = el
}

function syncCodeFromDigits() {
  otpCode.value = otpDigits.value.join('')
}

function resetOtpDigits() {
  otpCode.value = ''
  otpDigits.value = ['', '', '', '', '', '']
  otpRefs.value = []
}

function onDigitInput(index, event) {
  const digit = (event.target.value || '').replace(/\D/g, '').slice(-1)
  otpDigits.value[index] = digit
  event.target.value = digit
  syncCodeFromDigits()
  error.value = ''
  if (digit && index < 5) {
    otpRefs.value[index + 1]?.focus()
  }
}

function onDigitKeydown(index, event) {
  if (event.key === 'Backspace' && !otpDigits.value[index] && index > 0) {
    otpRefs.value[index - 1]?.focus()
  }
  if (event.key === 'Enter') {
    event.preventDefault()
    verifyCode()
  }
}

function onOtpPaste(event) {
  event.preventDefault()
  const pasted = (event.clipboardData?.getData('text') || '').replace(/\D/g, '').slice(0, 6)
  if (!pasted) return
  pasted.split('').forEach((digit, index) => {
    otpDigits.value[index] = digit
  })
  syncCodeFromDigits()
  otpRefs.value[Math.min(pasted.length, 5)]?.focus()
}

function fillFromDebugCode() {
  const code = (debugCode.value || '').replace(/\D/g, '').slice(0, 6)
  if (!code) return
  code.split('').forEach((digit, index) => {
    otpDigits.value[index] = digit
  })
  syncCodeFromDigits()
  focusOtpInput()
}

async function focusOtpInput() {
  await nextTick()
  otpRefs.value[0]?.focus()
}

watch(email, (val) => {
  error.value = ''
  if (lookupTimer) clearTimeout(lookupTimer)
  const q = (val || '').trim()
  if (q.length < 3) {
    lookupInfo.value = { found: false }
    return
  }
  lookupTimer = setTimeout(() => lookupAccount(), 450)
})

watch(selectedRole, () => {
  error.value = ''
  applyRoleDefaults()
  if (email.value.trim().length >= 3) lookupAccount()
})

function defaultEmailForRole(code) {
  return loginRoles.value.find(r => r.code === code)?.default_email || ''
}

function applyRoleDefaults() {
  const suggested = defaultEmailForRole(selectedRole.value)
  if (suggested) email.value = suggested
}

async function checkServer() {
  serverChecking.value = true
  try {
    await authService.health()
    serverDown.value = false
    info.value = 'Serveur connecté. Vous pouvez vous connecter.'
  } catch {
    serverDown.value = true
  } finally {
    serverChecking.value = false
  }
}

onMounted(async () => {
  if (typeof window !== 'undefined') {
    window.addEventListener(BRANDING_EVENT, (e) => {
      branding.value = e.detail || getCachedBranding()
    })
  }
  try {
    authConfig.value = await authService.config()
    if (authConfig.value.login_roles?.length) {
      loginRoles.value = authConfig.value.login_roles
    }
    applyRoleDefaults()
  } catch { /* ignore */ }
  await checkServer()
})

onUnmounted(() => {
  if (cooldownTimer) clearInterval(cooldownTimer)
  if (lookupTimer) clearTimeout(lookupTimer)
})

function goBack() {
  step.value = 'email'
  resetOtpDigits()
  debugCode.value = ''
  error.value = ''
  info.value = ''
}

function startCooldown(seconds = 60) {
  resendCooldown.value = seconds
  if (cooldownTimer) clearInterval(cooldownTimer)
  cooldownTimer = setInterval(() => {
    resendCooldown.value--
    if (resendCooldown.value <= 0) clearInterval(cooldownTimer)
  }, 1000)
}

function normaliserEmail() {
  const extrait = extractEmail(email.value)
  if (extrait) email.value = extrait
}

async function lookupAccount() {
  normaliserEmail()
  const q = email.value.trim()
  if (!q || q.length < 3) {
    lookupInfo.value = { found: false }
    return
  }
  lookupLoading.value = true
  try {
    const res = await authService.lookup(q, selectedRole.value)
    lookupInfo.value = res
    if (res.found && res.email) email.value = res.email
  } catch {
    lookupInfo.value = { found: false }
  } finally {
    lookupLoading.value = false
  }
}

async function sendCode() {
  normaliserEmail()
  if (!email.value.trim()) {
    error.value = 'Veuillez entrer votre adresse email.'
    return
  }
  if (!lookupInfo.value.found) await lookupAccount()
  loading.value = true
  error.value = ''
  info.value = ''
  try {
    logout()
    const res = await authService.sendCode(
      email.value.trim().toLowerCase(),
      selectedRole.value,
    )
    if (res.success) {
      if (res.email) email.value = res.email
      step.value = 'otp'
      roleLabel.value = res.role_label || loginRoles.value.find(r => r.code === selectedRole.value)?.label || ''
      deliveryLive.value = Boolean(res.delivery_live)
      deliveryChannel.value = res.channel || 'email'
      resetOtpDigits()
      debugCode.value = res.delivery_live ? '' : (res.debug_code || '')
      info.value = res.delivery_live
        ? (res.detail || 'Code envoyé ! Consultez votre boîte mail.')
        : (res.debug_code ? '' : (res.detail || 'Code généré.'))
      startCooldown(60)
      focusOtpInput()
    } else {
      error.value = res.detail || 'Impossible d\'envoyer le code. Vérifiez que Django tourne sur le port 8001.'
    }
  } catch (e) {
    error.value = e.message
    if (String(e.message).includes('serveur') || String(e.message).includes('Django')) {
      serverDown.value = true
    }
  } finally {
    loading.value = false
  }
}

async function verifyCode() {
  if (verifying.value) return
  const code = otpCode.value.trim().replace(/\D/g, '')
  if (code.length !== 6) {
    error.value = 'Entrez les 6 chiffres du code.'
    return
  }

  verifying.value = true
  loading.value = true
  error.value = ''
  normaliserEmail()
  try {
    const res = await authService.verifyCode(
      email.value.trim().toLowerCase(),
      code,
      selectedRole.value,
    )
    if (isAuthSuccess(res)) {
      const redirect = typeof route.query.redirect === 'string' ? route.query.redirect : null
      finishLogin(res, router, redirect)
    } else {
      error.value = res.detail || 'Code invalide.'
    }
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
    verifying.value = false
  }
}
</script>

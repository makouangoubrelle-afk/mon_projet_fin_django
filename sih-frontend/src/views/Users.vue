<template>
  <div class="space-y-6">
    <div class="page-card p-8 bg-gradient-to-r from-blue-500/20 via-cyan-500/20 to-teal-500/20 border border-blue-500/30 rounded-2xl">
      <div class="flex items-center justify-between flex-wrap gap-4">
        <div>
          <h1 class="text-3xl font-bold text-white">👤 Utilisateurs & OTP</h1>
          <p class="text-slate-400 text-sm mt-2">Gérez les comptes, changez l'administrateur, configurez l'envoi du code sur le téléphone ou par email.</p>
        </div>
        <button type="button" class="btn-save rounded-lg px-6 py-3 text-sm font-semibold" @click="openCreateForm">
          ➕ Nouvel utilisateur
        </button>
      </div>
    </div>

    <!-- Administrateur principal -->
    <div class="page-card p-6 rounded-2xl border border-amber-500/30 bg-amber-500/5">
      <h2 class="text-white font-bold mb-2">🔑 Administrateur principal</h2>
      <p class="text-slate-400 text-sm mb-4">
        L'admin se connecte avec son email — le code OTP part selon le canal configuré (SMS → téléphone enregistré ici).
      </p>
      <div class="flex flex-wrap items-center gap-3">
        <span class="text-teal-300 font-medium">{{ adminConfig.admin_email || 'Non défini' }}</span>
        <span v-if="adminConfig.admin_user_id" class="text-xs text-slate-500">(compte #{{ adminConfig.admin_user_id }})</span>
      </div>
      <p class="text-slate-500 text-xs mt-3">
        Pour changer d'admin : modifiez un utilisateur ci-dessous puis cliquez « Définir comme admin principal ».
      </p>
      <button
        v-if="primaryAdminUser"
        type="button"
        class="mt-4 text-sm px-4 py-2 rounded-lg bg-amber-500/20 text-amber-200 border border-amber-500/30 hover:bg-amber-500/30"
        @click="openEdit(primaryAdminUser)"
      >
        ✏️ Modifier téléphone / OTP de cet admin
      </button>
    </div>

    <div class="page-card p-4 rounded-xl border border-white/10">
      <p class="text-white text-sm font-semibold mb-3">Filtrer par rôle</p>
      <div class="flex flex-wrap gap-2">
        <button v-for="r in ['', ...roleCodes]" :key="r || 'all'" type="button"
          class="px-4 py-2 rounded-lg text-xs font-medium border transition"
          :class="filterRole === r ? 'bg-teal-500/30 border-teal-500/50 text-teal-200' : 'bg-white/5 border-white/10 text-slate-400 hover:text-white'"
          @click="filterRole = r; load()">
          {{ r ? roleLabel(r) : '✓ Tous' }}
        </button>
      </div>
    </div>

    <div v-if="error" class="page-card p-4 bg-red-500/10 border border-red-500/30 text-red-300 rounded-xl">⚠️ {{ error }}</div>

    <div class="page-card overflow-hidden rounded-2xl border border-white/10">
      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead>
            <tr class="bg-white/5 border-b border-white/10">
              <th class="px-4 py-4 text-left text-slate-300 font-semibold">Email</th>
              <th class="px-4 py-4 text-left text-slate-300 font-semibold">Téléphone</th>
              <th class="px-4 py-4 text-left text-slate-300 font-semibold">OTP</th>
              <th class="px-4 py-4 text-left text-slate-300 font-semibold">Rôle</th>
              <th class="px-4 py-4 text-left text-slate-300 font-semibold">Statut</th>
              <th class="px-4 py-4 text-left text-slate-300 font-semibold">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="u in users" :key="u.id" class="border-b border-white/10 hover:bg-white/5">
              <td class="px-4 py-4">
                <span class="text-white font-medium">{{ u.email }}</span>
                <span v-if="u.is_primary_admin" class="ml-2 text-xs text-amber-400">★ Admin principal</span>
              </td>
              <td class="px-4 py-4 text-slate-400 font-mono text-xs">{{ u.telephone || '—' }}</td>
              <td class="px-4 py-4">
                <span class="text-xs px-2 py-1 rounded-full bg-teal-500/20 text-teal-200">{{ u.otp_channel_label }}</span>
              </td>
              <td class="px-4 py-4">
                <span class="px-2 py-1 rounded-full text-xs bg-teal-500/30 text-teal-200">{{ u.role_label }}</span>
              </td>
              <td class="px-4 py-4">
                <span class="text-xs" :class="u.is_active ? 'text-green-300' : 'text-red-300'">
                  {{ u.is_active ? 'Actif' : 'Inactif' }}
                </span>
              </td>
              <td class="px-4 py-4 flex flex-wrap gap-2">
                <button type="button" class="text-teal-400 text-xs hover:text-teal-300" @click="openEdit(u)">✏️ Modifier</button>
                <button v-if="!u.is_primary_admin" type="button" class="text-amber-400 text-xs hover:text-amber-300"
                  @click="makePrimaryAdmin(u)">🔑 Admin principal</button>
                <button type="button" class="text-slate-400 text-xs" @click="toggleActive(u)">
                  {{ u.is_active ? 'Désactiver' : 'Activer' }}
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <p v-if="!loading && !users.length" class="p-8 text-center text-slate-400">Aucun utilisateur</p>
    </div>

    <!-- Création -->
    <div v-if="showForm" class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4" @click.self="closeCreateForm">
      <form class="page-card p-8 w-full max-w-md space-y-4 rounded-2xl border border-white/10 max-h-[90vh] overflow-y-auto" @submit.prevent="create">
        <h3 class="text-white font-bold text-xl">➕ Nouvel utilisateur</h3>
        <p class="text-slate-500 text-xs">Pour mettre à jour un compte existant, fermez cette fenêtre et cliquez ✏️ Modifier dans le tableau.</p>
        <div v-if="formError" class="p-3 rounded-lg bg-red-500/10 border border-red-500/30 text-red-300 text-sm space-y-2">
          <p>{{ formError }}</p>
          <button
            v-if="duplicateUser"
            type="button"
            class="text-amber-300 underline text-xs"
            @click="openEditFromDuplicate"
          >
            Ouvrir la modification de {{ duplicateUser.email }}
          </button>
        </div>
        <div v-if="successMessage" class="p-3 rounded-lg bg-green-500/10 border border-green-500/30 text-green-300 text-sm">{{ successMessage }}</div>
        <div>
          <label class="block text-white text-sm mb-1">Email *</label>
          <input v-model="form.email" type="email" required autocomplete="off" class="modal-input w-full px-4 py-2 rounded-lg bg-white/5 border border-white/10 text-white mb-0" />
        </div>
        <div>
          <label class="block text-white text-sm mb-1">Rôle *</label>
          <select v-model="form.role" required class="modal-input w-full px-4 py-2 rounded-lg bg-white/5 border border-white/10 text-white mb-0">
            <option v-for="r in staffRoles" :key="r.code" :value="r.code">{{ r.label }}</option>
          </select>
        </div>
        <div>
          <label class="block text-white text-sm mb-1">Téléphone (pour OTP SMS)</label>
          <input v-model="form.telephone" placeholder="+242 06 123 4567" class="modal-input w-full px-4 py-2 rounded-lg bg-white/5 border border-white/10 text-white mb-0" />
        </div>
        <div>
          <label class="block text-white text-sm mb-1">Réception du code OTP</label>
          <select v-model="form.otp_channel" class="modal-input w-full px-4 py-2 rounded-lg bg-white/5 border border-white/10 text-white mb-0">
            <option value="EMAIL">📧 Par email</option>
            <option value="SMS">📱 Par SMS (téléphone)</option>
          </select>
        </div>
        <div class="flex gap-3 justify-end pt-2">
          <button type="button" class="px-4 py-2 text-slate-400 hover:text-white" @click="closeCreateForm">Annuler</button>
          <button type="submit" class="btn-save px-4 py-2 rounded-lg disabled:opacity-50" :disabled="saving">{{ saving ? 'Création…' : 'Créer' }}</button>
        </div>
      </form>
    </div>

    <!-- Édition -->
    <div v-if="editUser" class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4" @click.self="editUser = null">
      <form class="page-card p-8 w-full max-w-md space-y-4 rounded-2xl border border-white/10 max-h-[90vh] overflow-y-auto" @submit.prevent="saveEdit">
        <h3 class="text-white font-bold text-xl">✏️ Modifier — OTP & connexion</h3>
        <p class="text-slate-400 text-xs">L'utilisateur entre son email à la connexion ; le code part automatiquement au canal choisi.</p>
        <div v-if="editFormError" class="p-3 rounded-lg bg-red-500/10 border border-red-500/30 text-red-300 text-sm">{{ editFormError }}</div>
        <div v-if="successMessage" class="p-3 rounded-lg bg-green-500/10 border border-green-500/30 text-green-300 text-sm">{{ successMessage }}</div>
        <div>
          <label class="block text-white text-sm mb-1">Email</label>
          <input v-model="editForm.email" type="email" required class="modal-input w-full px-4 py-2 rounded-lg bg-white/5 border border-white/10 text-white mb-0" />
        </div>
        <div>
          <label class="block text-white text-sm mb-1">Téléphone</label>
          <input v-model="editForm.telephone" type="tel" placeholder="+242 06 900 10 01" class="modal-input w-full px-4 py-2 rounded-lg bg-white/5 border border-white/10 text-white mb-0" />
        </div>
        <div>
          <label class="block text-white text-sm mb-1">Code OTP reçu sur</label>
          <select v-model="editForm.otp_channel" class="modal-input w-full px-4 py-2 rounded-lg bg-white/5 border border-white/10 text-white mb-0">
            <option value="EMAIL">📧 Email (boîte mail sur téléphone)</option>
            <option value="SMS">📱 SMS (numéro ci-dessus)</option>
          </select>
        </div>
        <div>
          <label class="block text-white text-sm mb-1">Rôle</label>
          <select v-model="editForm.role" class="modal-input w-full px-4 py-2 rounded-lg bg-white/5 border border-white/10 text-white mb-0">
            <option v-for="r in staffRoles" :key="r.code" :value="r.code">{{ r.label }}</option>
          </select>
        </div>
        <div class="flex gap-3 justify-end pt-2">
          <button type="button" class="px-4 py-2 text-slate-400 hover:text-white" @click="editUser = null">Annuler</button>
          <button type="submit" class="btn-save px-4 py-2 rounded-lg disabled:opacity-50" :disabled="saving">{{ saving ? 'Enregistrement…' : 'Enregistrer' }}</button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { coreService } from '../services/api.js'

const users = ref([])
const adminConfig = ref({ admin_email: '', admin_user_id: null })
const loading = ref(true)
const error = ref('')
const formError = ref('')
const editFormError = ref('')
const successMessage = ref('')
const duplicateUser = ref(null)
const filterRole = ref('')
const showForm = ref(false)
const editUser = ref(null)
const editForm = ref({ email: '', telephone: '', role: '', otp_channel: 'EMAIL' })
const saving = ref(false)
const staffRoles = ref([])
const roleCodes = ref([])
const form = ref({ email: '', role: 'MEDECIN', telephone: '', otp_channel: 'EMAIL' })

const primaryAdminUser = computed(() => {
  const email = (adminConfig.value.admin_email || '').trim().toLowerCase()
  if (email) {
    const byEmail = users.value.find((u) => u.email.toLowerCase() === email)
    if (byEmail) return byEmail
  }
  return users.value.find((u) => u.is_primary_admin) || null
})

function emptyForm() {
  return { email: '', role: 'MEDECIN', telephone: '', otp_channel: 'EMAIL' }
}

function openCreateForm() {
  form.value = emptyForm()
  formError.value = ''
  duplicateUser.value = null
  successMessage.value = ''
  showForm.value = true
}

function closeCreateForm() {
  showForm.value = false
  formError.value = ''
  duplicateUser.value = null
}

function findDuplicateEmail(email) {
  const normalized = (email || '').trim().toLowerCase()
  if (!normalized) return null
  return users.value.find((u) => u.email.toLowerCase() === normalized) || null
}

function openEditFromDuplicate() {
  if (!duplicateUser.value) return
  const u = duplicateUser.value
  closeCreateForm()
  openEdit(u)
}

function roleLabel(code) {
  return staffRoles.value.find((r) => r.code === code)?.label || code
}

async function loadAdminConfig() {
  try {
    adminConfig.value = await coreService.adminOtpConfig()
  } catch { /* ignore */ }
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    users.value = await coreService.users(filterRole.value)
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

async function create() {
  formError.value = ''
  duplicateUser.value = null
  successMessage.value = ''

  const email = form.value.email.trim().toLowerCase()
  if (!email) {
    formError.value = 'Indiquez une adresse email.'
    return
  }

  const existing = findDuplicateEmail(email)
  if (existing) {
    duplicateUser.value = existing
    formError.value = `Cet email est déjà utilisé par ${existing.email} (${existing.role_label}). Utilisez « Modifier » au lieu de créer un doublon.`
    return
  }

  saving.value = true
  try {
    await coreService.createUser({
      email,
      role: form.value.role,
      telephone: form.value.telephone.trim(),
      otp_channel: form.value.otp_channel,
    })
    successMessage.value = `Utilisateur ${email} créé avec succès.`
    form.value = emptyForm()
    await load()
    await loadAdminConfig()
    setTimeout(() => {
      closeCreateForm()
      successMessage.value = ''
    }, 1200)
  } catch (e) {
    formError.value = e.message || 'Impossible de créer l\'utilisateur.'
    const dup = findDuplicateEmail(email)
    if (dup) duplicateUser.value = dup
  } finally {
    saving.value = false
  }
}

async function toggleActive(u) {
  try {
    await coreService.updateUser(u.id, { is_active: !u.is_active })
    await load()
  } catch (e) {
    error.value = e.message
  }
}

function openEdit(u) {
  editUser.value = u
  editFormError.value = ''
  successMessage.value = ''
  editForm.value = {
    email: u.email,
    telephone: u.telephone || '',
    role: u.role,
    otp_channel: u.otp_channel || 'EMAIL',
  }
}

async function saveEdit() {
  if (!editUser.value) return
  editFormError.value = ''
  successMessage.value = ''

  const email = editForm.value.email.trim().toLowerCase()
  const conflict = users.value.find(
    (u) => u.id !== editUser.value.id && u.email.toLowerCase() === email
  )
  if (conflict) {
    editFormError.value = `Cet email est déjà utilisé par ${conflict.email}.`
    return
  }

  saving.value = true
  try {
    await coreService.updateUser(editUser.value.id, {
      email,
      telephone: editForm.value.telephone.trim(),
      role: editForm.value.role,
      otp_channel: editForm.value.otp_channel,
    })
    successMessage.value = 'Modifications enregistrées.'
    await load()
    await loadAdminConfig()
    setTimeout(() => {
      editUser.value = null
      successMessage.value = ''
    }, 1200)
  } catch (e) {
    editFormError.value = e.message || 'Impossible d\'enregistrer.'
  } finally {
    saving.value = false
  }
}

async function makePrimaryAdmin(u) {
  if (!confirm(`Définir ${u.email} comme administrateur principal ?`)) return
  try {
    await coreService.setPrimaryAdmin(u.id)
    await load()
    await loadAdminConfig()
  } catch (e) {
    error.value = e.message
  }
}

onMounted(async () => {
  const roles = await coreService.roles()
  staffRoles.value = roles.roles.filter((r) => r.code !== 'PATIENT')
  roleCodes.value = staffRoles.value.map((r) => r.code)
  await loadAdminConfig()
  await load()
})
</script>

<style scoped>
.modal-input:focus { outline: none; }
</style>

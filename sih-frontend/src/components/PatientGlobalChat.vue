<template>
  <div class="page-card overflow-hidden flex flex-col h-[min(440px,62vh)] sm:h-[520px] lg:h-[600px]">
    <div class="p-4 border-b border-white/10 flex items-center justify-between gap-3 bg-gradient-to-r from-teal-500/10 to-cyan-500/5">
      <div>
        <h3 class="text-white font-bold flex items-center gap-2">
          💬 Chat médical
          <span v-if="unreadCount" class="px-2 py-0.5 rounded-full bg-red-500/30 text-red-200 text-xs">{{ unreadCount }}</span>
        </h3>
        <p class="text-slate-400 text-xs mt-0.5">
          {{ isStaff ? `Conversation — ${patientLabel}` : 'Contactez l\'équipe médicale et demandez un rendez-vous' }}
        </p>
      </div>
      <div class="flex gap-2 flex-wrap justify-end">
        <button type="button" class="text-xs px-3 py-1.5 rounded-lg bg-white/5 text-slate-300 hover:bg-white/10" @click="loadMessages">
          ↻ Actualiser
        </button>
        <button
          v-if="messages.length"
          type="button"
          class="text-xs px-3 py-1.5 rounded-lg bg-red-500/15 text-red-300 hover:bg-red-500/25 border border-red-500/30"
          :disabled="deleting"
          title="Supprimer toute la conversation"
          @click="deleteConversation"
        >
          {{ deleting ? '…' : '🗑 Conversation' }}
        </button>
        <button
          type="button"
          class="text-xs px-3 py-1.5 rounded-lg transition"
          :class="mode === 'chat' ? 'bg-teal-500/20 text-teal-200' : 'bg-white/5 text-slate-400'"
          @click="mode = 'chat'"
        >Message</button>
        <button
          v-if="!isStaff"
          type="button"
          class="text-xs px-3 py-1.5 rounded-lg transition"
          :class="mode === 'rdv' ? 'bg-teal-500/20 text-teal-200' : 'bg-white/5 text-slate-400'"
          @click="mode = 'rdv'"
        >📅 RDV</button>
      </div>
    </div>

    <div v-if="!patientId" class="flex-1 flex items-center justify-center p-8 text-slate-500 text-sm text-center">
      Sélectionnez un patient dans la liste pour ouvrir la conversation.
    </div>

    <template v-else>
      <div ref="scrollEl" class="flex-1 overflow-y-auto p-4 space-y-3 chat-scroll">
        <div v-if="loading" class="text-center text-slate-500 text-sm py-8">Chargement des messages…</div>
        <div v-else-if="!messages.length" class="text-center py-10">
          <p class="text-4xl mb-3">💬</p>
          <p class="text-slate-400 text-sm">Aucun message. Écrivez à l'équipe médicale.</p>
        </div>
        <div
          v-for="m in messages"
          :key="m.id"
          class="flex group"
          :class="m.is_mine ? 'justify-end' : 'justify-start'"
        >
          <div
            class="max-w-[85%] rounded-2xl px-4 py-3 text-sm shadow-lg relative"
            :class="bubbleClass(m)"
          >
            <div class="flex items-center gap-2 mb-1 flex-wrap">
              <span class="font-semibold text-xs">{{ m.sender_name }}</span>
              <span class="text-[10px] opacity-70">{{ roleLabel(m.sender_role) }}</span>
              <span v-if="m.message_type === 'RDV_DEMANDE'" class="text-[10px] px-1.5 py-0.5 rounded bg-amber-500/30">RDV</span>
              <button
                v-if="canDeleteMessage(m)"
                type="button"
                class="ml-auto text-[10px] px-1.5 py-0.5 rounded opacity-70 hover:opacity-100 hover:bg-red-500/30 text-red-300"
                title="Supprimer ce message"
                :disabled="deletingMessageId === m.id"
                @click.stop="deleteMessage(m)"
              >
                {{ deletingMessageId === m.id ? '…' : '🗑' }}
              </button>
            </div>
            <p class="whitespace-pre-wrap leading-relaxed">{{ m.contenu }}</p>
            <p class="text-[10px] opacity-60 mt-2 text-right">{{ formatTime(m.created_at) }}</p>
          </div>
        </div>
      </div>

      <div class="p-4 border-t border-white/10 bg-slate-900/50">
        <div v-if="chatError" class="text-red-400 text-xs mb-2">{{ chatError }}</div>

        <form v-if="mode === 'chat'" @submit.prevent="sendMessage" class="flex gap-2">
          <input
            v-model="draft"
            type="text"
            placeholder="Votre message à l'équipe médicale…"
            class="modal-input flex-1 mb-0"
            maxlength="4000"
            :disabled="sending"
          />
          <button type="submit" class="btn-save shrink-0" :disabled="sending || !draft.trim()">
            {{ sending ? '…' : 'Envoyer' }}
          </button>
        </form>

        <form v-else @submit.prevent="sendRdv" class="space-y-2">
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-2">
            <input v-model="rdvForm.date_rdv" type="datetime-local" class="modal-input mb-0" required />
            <input v-model="rdvForm.motif" type="text" class="modal-input mb-0" placeholder="Motif du rendez-vous *" required />
          </div>
          <textarea v-model="rdvForm.message" class="modal-input mb-0" rows="2" placeholder="Message complémentaire (optionnel)"></textarea>
          <button type="submit" class="btn-save w-full sm:w-auto" :disabled="sending">
            {{ sending ? 'Envoi…' : '📅 Demander ce rendez-vous' }}
          </button>
        </form>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { chatService, getUser, getPatientSession } from '../services/api.js'

const props = defineProps({
  patientId: { type: Number, default: null },
  patientNom: { type: String, default: '' },
  embedded: { type: Boolean, default: true },
})

const emit = defineEmits(['message-sent', 'conversation-deleted'])

const STAFF_ROLES = ['ADMIN', 'MEDECIN', 'INFIRMIER', 'SECRETAIRE', 'SECRETAIRE_GENERALE', 'RECEPTIONNISTE']

const user = computed(() => getUser())
const isStaff = computed(() => {
  if (getPatientSession()?.patient_id && user.value?.role !== 'PATIENT') return false
  return STAFF_ROLES.includes(user.value?.role)
})

const messages = ref([])
const loading = ref(false)
const sending = ref(false)
const deleting = ref(false)
const deletingMessageId = ref(null)
const draft = ref('')
const chatError = ref('')
const mode = ref('chat')
const unreadCount = ref(0)
const scrollEl = ref(null)

const rdvForm = ref({
  date_rdv: '',
  motif: '',
  message: '',
})

const patientLabel = computed(() => props.patientNom || `Patient #${props.patientId}`)

let pollTimer = null

function roleLabel(role) {
  const map = {
    PATIENT: 'Patient',
    MEDECIN: 'Médecin',
    INFIRMIER: 'Infirmier',
    SECRETAIRE: 'Secrétaire',
    SECRETAIRE_GENERALE: 'Sec. générale',
    RECEPTIONNISTE: 'Réception',
    ADMIN: 'Admin',
  }
  return map[role] || role
}

function bubbleClass(m) {
  if (m.message_type === 'RDV_DEMANDE') {
    return m.is_mine
      ? 'bg-amber-500/20 border border-amber-500/30 text-amber-100'
      : 'bg-amber-500/10 border border-amber-500/20 text-amber-100'
  }
  if (m.is_mine) {
    return 'bg-teal-600/30 border border-teal-500/30 text-teal-50'
  }
  return 'bg-white/8 border border-white/10 text-slate-200'
}

function formatTime(iso) {
  if (!iso) return ''
  try {
    return new Date(iso).toLocaleString('fr-FR', { day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit' })
  } catch {
    return iso
  }
}

async function scrollBottom() {
  await nextTick()
  if (scrollEl.value) scrollEl.value.scrollTop = scrollEl.value.scrollHeight
}

async function loadUnread() {
  if (!props.patientId && !isStaff.value) return
  try {
    const res = await chatService.unreadCount(props.patientId || undefined)
    unreadCount.value = res.count || 0
  } catch { /* ignore */ }
}

async function loadMessages() {
  if (!props.patientId) return
  loading.value = true
  chatError.value = ''
  try {
    messages.value = await chatService.messages(props.patientId)
    await scrollBottom()
    await loadUnread()
  } catch (e) {
    chatError.value = e.message
  } finally {
    loading.value = false
  }
}

async function sendMessage() {
  const text = draft.value.trim()
  if (!text || !props.patientId) return
  sending.value = true
  chatError.value = ''
  try {
    const msg = await chatService.send({ patient_id: props.patientId, contenu: text })
    messages.value.push(msg)
    draft.value = ''
    await scrollBottom()
    emit('message-sent')
  } catch (e) {
    chatError.value = e.message
  } finally {
    sending.value = false
  }
}

function canDeleteMessage(m) {
  return Boolean(m?.is_mine) || isStaff.value
}

async function deleteMessage(m) {
  if (!m?.id || !canDeleteMessage(m)) return
  if (!window.confirm('Supprimer ce message ?')) return
  deletingMessageId.value = m.id
  chatError.value = ''
  try {
    await chatService.deleteMessage(m.id)
    messages.value = messages.value.filter((x) => x.id !== m.id)
    emit('message-sent')
  } catch (e) {
    chatError.value = e.message
  } finally {
    deletingMessageId.value = null
  }
}

async function deleteConversation() {
  if (!props.patientId || !messages.value.length) return
  const label = isStaff.value ? patientLabel.value : 'cette conversation'
  if (!window.confirm(`Supprimer toute la conversation avec ${label} ? Cette action est irréversible.`)) return
  deleting.value = true
  chatError.value = ''
  try {
    await chatService.deleteConversation(props.patientId)
    messages.value = []
    unreadCount.value = 0
    emit('conversation-deleted')
    emit('message-sent')
  } catch (e) {
    chatError.value = e.message
  } finally {
    deleting.value = false
  }
}

async function sendRdv() {
  if (!props.patientId) return
  sending.value = true
  chatError.value = ''
  try {
    const res = await chatService.demandeRdv({
      patient_id: props.patientId,
      date_rdv: new Date(rdvForm.value.date_rdv).toISOString(),
      motif: rdvForm.value.motif.trim(),
      message: rdvForm.value.message.trim(),
    })
    messages.value.push(res.message)
    rdvForm.value = { date_rdv: '', motif: '', message: '' }
    mode.value = 'chat'
    await scrollBottom()
  } catch (e) {
    chatError.value = e.message
  } finally {
    sending.value = false
  }
}

function defaultRdvDateTime() {
  const d = new Date()
  d.setDate(d.getDate() + 1)
  d.setHours(9, 0, 0, 0)
  const pad = (n) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`
}

watch(() => props.patientId, (id) => {
  if (id) {
    loadMessages()
    if (!rdvForm.value.date_rdv) rdvForm.value.date_rdv = defaultRdvDateTime()
  } else {
    messages.value = []
  }
}, { immediate: true })

onMounted(() => {
  if (!rdvForm.value.date_rdv) rdvForm.value.date_rdv = defaultRdvDateTime()
  pollTimer = setInterval(() => {
    if (props.patientId) loadMessages()
  }, 20000)
})

onUnmounted(() => {
  if (pollTimer) clearInterval(pollTimer)
})
</script>

<style scoped>
.chat-scroll {
  scrollbar-width: thin;
  scrollbar-color: rgba(255,255,255,0.15) transparent;
}
</style>

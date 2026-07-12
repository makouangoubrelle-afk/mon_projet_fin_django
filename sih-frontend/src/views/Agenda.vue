<template>
  <div class="space-y-6">
    <div class="page-heading">
      <div>
        <h2 class="text-xl font-bold text-white">📅 Agenda</h2>
        <p class="text-slate-400 text-sm">{{ subtitle }}</p>
      </div>
      <button @click="openRdvModal()" class="action-button px-5 py-2.5 rounded-xl text-sm font-medium">+ Rendez-vous</button>
    </div>

    <div class="grid grid-cols-1 xl:grid-cols-3 gap-6">
      <!-- Calendrier -->
      <div class="xl:col-span-2 page-card p-5">
        <div class="flex items-center justify-between mb-4">
          <button @click="prevMonth" class="text-slate-400 hover:text-white px-2">‹</button>
          <h3 class="text-white font-semibold capitalize">{{ monthLabel }}</h3>
          <button @click="nextMonth" class="text-slate-400 hover:text-white px-2">›</button>
        </div>
        <div class="grid grid-cols-7 gap-1 text-center text-xs text-slate-500 mb-2">
          <span v-for="d in weekDays" :key="d">{{ d }}</span>
        </div>
        <div class="grid grid-cols-7 gap-1">
          <div v-for="(cell, i) in calendarCells" :key="i"
            class="min-h-[72px] p-1 rounded-lg border text-left transition cursor-pointer"
            :class="cell.inMonth ? (isSameDay(cell.date, selectedDay) ? 'border-teal-500/50 bg-teal-500/10' : 'border-white/5 hover:bg-white/5') : 'border-transparent opacity-30'"
            @click="cell.inMonth && selectDay(cell.date)">
            <span class="text-xs font-medium" :class="cell.inMonth ? 'text-white' : 'text-slate-600'">{{ cell.day }}</span>
            <div class="mt-1 space-y-0.5">
              <div v-for="ev in eventsOnDay(cell.date).slice(0, 2)" :key="ev.id"
                class="text-[9px] truncate px-1 py-0.5 rounded bg-teal-500/25 text-teal-200"
                @click.stop="openRdvDetail(ev)">
                {{ formatTime(ev.date_rdv) }} {{ ev.patient_nom }}
              </div>
              <p v-if="eventsOnDay(cell.date).length > 2" class="text-[9px] text-slate-500">+{{ eventsOnDay(cell.date).length - 2 }}</p>
            </div>
          </div>
        </div>

        <div v-if="selectedDay" class="mt-5 border-t border-white/10 pt-4">
          <h4 class="text-sm text-white font-medium mb-3">{{ formatDayFull(selectedDay) }}</h4>
          <div v-if="!dayEvents.length" class="text-slate-500 text-sm">Aucun rendez-vous ce jour.</div>
          <div v-else class="space-y-2">
            <div v-for="ev in dayEvents" :key="ev.id"
              class="p-3 rounded-xl bg-white/5 flex justify-between items-start gap-3 hover:bg-white/8 cursor-pointer"
              @click="openRdvDetail(ev)">
              <div>
                <p class="text-white font-medium">{{ ev.patient_nom }}</p>
                <p class="text-xs text-teal-400">{{ formatTime(ev.date_rdv) }} · {{ ev.medecin_nom || '—' }}</p>
                <p class="text-xs text-slate-400 mt-1">{{ ev.motif }}</p>
              </div>
              <span class="text-[10px] px-2 py-0.5 rounded-full shrink-0"
                :class="statutClass(ev.statut)">{{ ev.statut_label }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Panneau secrétaire / patients -->
      <div class="space-y-4">
        <div v-if="isSecretaire || isAdmin" class="page-card p-5">
          <h3 class="text-white font-semibold mb-3">👨‍⚕️ Agenda du médecin</h3>
          <select v-model="selectedMedecinId" class="modal-input text-sm mb-3" @change="onMedecinChange">
            <option value="">Choisir un médecin</option>
            <option v-for="d in medecins" :key="d.id" :value="d.user_id">{{ d.prenom }} {{ d.nom }} — {{ d.specialite }}</option>
          </select>
          <p v-if="selectedMedecin" class="text-xs text-slate-400">{{ rdvList.length }} rendez-vous · {{ patientsMedecin.length }} patients</p>
        </div>

        <div class="page-card p-5 max-h-[480px] overflow-y-auto">
          <h3 class="text-white font-semibold mb-3">👥 Patients</h3>
          <div v-if="!patientsMedecin.length" class="text-slate-500 text-sm">Sélectionnez un médecin ou aucun patient.</div>
          <button v-for="p in patientsMedecin" :key="p.id" @click="selectPatient(p)"
            class="w-full text-left p-3 rounded-xl mb-2 transition border"
            :class="selectedPatient?.id === p.id ? 'border-teal-500/40 bg-teal-500/10' : 'border-white/5 hover:bg-white/5'">
            <p class="text-white text-sm font-medium">{{ p.nom }} {{ p.prenom }}</p>
            <p class="text-xs text-slate-500">{{ p.telephone }}</p>
          </button>
        </div>

        <div v-if="selectedPatient" class="page-card p-5">
          <h3 class="text-white font-semibold mb-2">📝 Notes — {{ selectedPatient.nom }}</h3>
          <form @submit.prevent="saveNote" class="space-y-2 mb-4">
            <textarea v-model="noteForm.contenu" placeholder="Note pour le médecin..." class="modal-input text-sm" rows="3" required></textarea>
            <label class="flex items-center gap-2 text-xs text-slate-400">
              <input v-model="noteForm.est_important" type="checkbox" class="rounded" /> Important
            </label>
            <button type="submit" class="btn-save text-sm w-full">Enregistrer la note</button>
          </form>
          <div class="space-y-2 max-h-40 overflow-y-auto">
            <div v-for="n in notes" :key="n.id" class="p-2 rounded-lg text-sm"
              :class="n.est_important ? 'bg-amber-500/10 border border-amber-500/20' : 'bg-white/5'">
              <p class="text-slate-300">{{ n.contenu }}</p>
              <p class="text-[10px] text-slate-500 mt-1">{{ n.auteur_nom }} · {{ formatDateTime(n.date_creation) }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal RDV -->
    <div v-if="showRdv" class="modal" @click.self="showRdv = false">
      <div class="modal-content max-w-md">
        <h3 class="text-white font-semibold mb-4">{{ editingRdv ? 'Modifier RDV' : 'Nouveau rendez-vous' }}</h3>
        <form @submit.prevent="saveRdv" class="space-y-3">
          <select v-model="rdvForm.patient_id" class="modal-input" required>
            <option value="">Patient *</option>
            <option v-for="p in allPatients" :key="p.id" :value="p.id">{{ p.nom }} {{ p.prenom }}</option>
          </select>
          <select v-if="isSecretaire || isAdmin" v-model="rdvForm.medecin_id" class="modal-input">
            <option value="">Médecin</option>
            <option v-for="d in medecins" :key="d.id" :value="d.user_id">{{ d.prenom }} {{ d.nom }}</option>
          </select>
          <input v-model="rdvForm.date_rdv" type="datetime-local" class="modal-input" required />
          <input v-model="rdvForm.motif" placeholder="Motif *" class="modal-input" required />
          <select v-model="rdvForm.statut" class="modal-input">
            <option value="PLANIFIE">Planifié</option>
            <option value="CONFIRME">Confirmé</option>
            <option value="ANNULE">Annulé</option>
            <option value="TERMINE">Terminé</option>
          </select>
          <textarea v-model="rdvForm.notes" placeholder="Notes internes" class="modal-input" rows="2"></textarea>
          <p v-if="rdvError" class="text-red-400 text-sm">{{ rdvError }}</p>
          <div class="modal-buttons">
            <button v-if="editingRdv" type="button" @click="deleteRdv" class="btn-cancel text-red-400">Supprimer</button>
            <button type="button" @click="showRdv = false" class="btn-cancel">Annuler</button>
            <button type="submit" class="btn-save">Enregistrer</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { agendaService, patientService, doctorService, getUser } from '../services/api.js'

const user = getUser()
const isMedecin = computed(() => user?.role === 'MEDECIN')
const isInfirmier = computed(() => user?.role === 'INFIRMIER')
const isSecretaire = computed(() => user?.role === 'SECRETAIRE')
const isAdmin = computed(() => user?.role === 'ADMIN')

const currentMonth = ref(new Date())
const selectedDay = ref(new Date())
const rdvList = ref([])
const medecins = ref([])
const allPatients = ref([])
const patientsMedecin = ref([])
const selectedMedecinId = ref('')
const selectedPatient = ref(null)
const notes = ref([])
const showRdv = ref(false)
const editingRdv = ref(null)
const rdvError = ref('')
const noteForm = ref({ contenu: '', est_important: false })
const rdvForm = ref({ patient_id: '', medecin_id: '', date_rdv: '', motif: '', statut: 'PLANIFIE', notes: '' })

const weekDays = ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim']

const subtitle = computed(() => {
  if (isSecretaire.value) return 'Calendrier du médecin, patients et notes'
  if (isMedecin.value) return 'Votre agenda et rendez-vous'
  if (isInfirmier.value) return 'Agenda du service'
  return 'Planning hospitalier'
})

const selectedMedecin = computed(() => medecins.value.find(d => String(d.user_id) === String(selectedMedecinId.value)))

const monthLabel = computed(() =>
  currentMonth.value.toLocaleDateString('fr-FR', { month: 'long', year: 'numeric' })
)

const calendarCells = computed(() => {
  const y = currentMonth.value.getFullYear()
  const m = currentMonth.value.getMonth()
  const first = new Date(y, m, 1)
  let start = first.getDay() - 1
  if (start < 0) start = 6
  const cells = []
  const startDate = new Date(y, m, 1 - start)
  for (let i = 0; i < 42; i++) {
    const d = new Date(startDate)
    d.setDate(startDate.getDate() + i)
    cells.push({ date: d, day: d.getDate(), inMonth: d.getMonth() === m })
  }
  return cells
})

const dayEvents = computed(() => eventsOnDay(selectedDay.value))

function eventsOnDay(date) {
  if (!date) return []
  return rdvList.value.filter(ev => isSameDay(new Date(ev.date_rdv), date))
}

function isSameDay(a, b) {
  return a.getFullYear() === b.getFullYear() && a.getMonth() === b.getMonth() && a.getDate() === b.getDate()
}

function selectDay(d) { selectedDay.value = new Date(d) }
function prevMonth() { currentMonth.value = new Date(currentMonth.value.getFullYear(), currentMonth.value.getMonth() - 1, 1) }
function nextMonth() { currentMonth.value = new Date(currentMonth.value.getFullYear(), currentMonth.value.getMonth() + 1, 1) }

function formatTime(iso) {
  return new Date(iso).toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })
}
function formatDayFull(d) {
  return d.toLocaleDateString('fr-FR', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' })
}
function formatDateTime(iso) {
  return new Date(iso).toLocaleString('fr-FR', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' })
}

function statutClass(s) {
  return { CONFIRME: 'bg-emerald-500/20 text-emerald-300', PLANIFIE: 'bg-blue-500/20 text-blue-300', ANNULE: 'bg-red-500/20 text-red-300', TERMINE: 'bg-slate-500/20 text-slate-400' }[s] || 'bg-teal-500/20 text-teal-300'
}

async function loadRdv() {
  const params = {}
  if (isMedecin.value && user?.user_id) params.medecin_id = user.user_id
  else if (selectedMedecinId.value) params.medecin_id = selectedMedecinId.value
  else if (isInfirmier.value && user?.service_id) params.service_id = user.service_id
  rdvList.value = await agendaService.rendezVous(params)
}

async function loadPatientsMedecin() {
  if (selectedMedecinId.value) {
    patientsMedecin.value = await agendaService.patientsMedecin(selectedMedecinId.value)
  } else if (isMedecin.value) {
    patientsMedecin.value = user?.user_id ? await agendaService.patientsMedecin(user.user_id) : []
  } else {
    patientsMedecin.value = []
  }
}

async function onMedecinChange() {
  await loadRdv()
  await loadPatientsMedecin()
  selectedPatient.value = null
  notes.value = []
}

async function selectPatient(p) {
  selectedPatient.value = p
  notes.value = await agendaService.notesPatient(p.id, selectedMedecinId.value || undefined)
}

async function saveNote() {
  if (!selectedPatient.value) return
  await agendaService.addNote(selectedPatient.value.id, {
    contenu: noteForm.value.contenu,
    est_important: noteForm.value.est_important,
    medecin_id: selectedMedecinId.value ? Number(selectedMedecinId.value) : undefined,
  })
  noteForm.value = { contenu: '', est_important: false }
  notes.value = await agendaService.notesPatient(selectedPatient.value.id, selectedMedecinId.value || undefined)
}

function openRdvModal(date) {
  editingRdv.value = null
  const d = date || selectedDay.value
  const local = new Date(d.getTime() - d.getTimezoneOffset() * 60000).toISOString().slice(0, 16)
  rdvForm.value = {
    patient_id: selectedPatient.value?.id || '',
    medecin_id: selectedMedecinId.value || (isMedecin.value ? user?.user_id : '') || '',
    date_rdv: local,
    motif: '',
    statut: 'PLANIFIE',
    notes: '',
  }
  rdvError.value = ''
  showRdv.value = true
}

function openRdvDetail(ev) {
  editingRdv.value = ev
  const d = new Date(ev.date_rdv)
  rdvForm.value = {
    patient_id: ev.patient_id,
    medecin_id: ev.medecin_id || '',
    date_rdv: new Date(d.getTime() - d.getTimezoneOffset() * 60000).toISOString().slice(0, 16),
    motif: ev.motif,
    statut: ev.statut,
    notes: ev.notes || '',
  }
  rdvError.value = ''
  showRdv.value = true
}

async function saveRdv() {
  rdvError.value = ''
  try {
    const payload = {
      patient_id: Number(rdvForm.value.patient_id),
      date_rdv: new Date(rdvForm.value.date_rdv).toISOString(),
      motif: rdvForm.value.motif,
      statut: rdvForm.value.statut,
      notes: rdvForm.value.notes,
    }
    if (rdvForm.value.medecin_id) payload.medecin_id = Number(rdvForm.value.medecin_id)
    if (user?.service_id) payload.service_id = user.service_id
    if (editingRdv.value) await agendaService.updateRdv(editingRdv.value.id, payload)
    else await agendaService.createRdv(payload)
    showRdv.value = false
    await loadRdv()
    await loadPatientsMedecin()
  } catch (e) {
    rdvError.value = e.message
  }
}

async function deleteRdv() {
  if (!editingRdv.value || !confirm('Supprimer ce rendez-vous ?')) return
  await agendaService.deleteRdv(editingRdv.value.id)
  showRdv.value = false
  await loadRdv()
}

onMounted(async () => {
  const svcId = isSecretaire.value || isInfirmier.value ? user?.service_id : null
  medecins.value = (await doctorService.list(svcId)).filter(d => d.est_actif && d.user_id)
  allPatients.value = await patientService.list()

  if (isMedecin.value) {
    const me = medecins.value.find(d => d.email === user?.email)
    if (me?.user_id) selectedMedecinId.value = me.user_id
    else if (user?.user_id) selectedMedecinId.value = user.user_id
  } else if (medecins.value.length === 1) {
    selectedMedecinId.value = medecins.value[0].user_id
  }

  await loadRdv()
  await loadPatientsMedecin()
})

watch(currentMonth, loadRdv)
</script>

<style scoped>
input[type="datetime-local"] { color-scheme: dark; }
</style>

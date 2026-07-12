<template>
  <div class="space-y-6">
    <div class="page-heading">
      <div>
        <h2 class="text-xl font-bold text-white">{{ isPatient ? '📋 Mes ordonnances' : '📋 Ordonnances' }}</h2>
        <p class="text-slate-400 text-sm">{{ filtered.length }} ordonnances — export PDF & Excel</p>
      </div>
      <div class="flex gap-2">
        <button @click="exportAllPdf" class="px-4 py-2.5 rounded-xl text-sm font-medium bg-red-600/20 text-red-300 border border-red-500/30 hover:bg-red-600/30">📄 PDF (liste)</button>
        <button @click="exportAllExcel" class="px-4 py-2.5 rounded-xl text-sm font-medium bg-emerald-600/20 text-emerald-300 border border-emerald-500/30">📊 Excel (liste)</button>
        <button v-if="!isPatient" @click="showAdd = true" class="action-button px-5 py-2.5 rounded-xl text-sm font-medium">+ Nouvelle ordonnance</button>
      </div>
    </div>

    <div v-if="patientError" class="page-card p-4 border border-amber-500/30 bg-amber-500/10">
      <p class="text-amber-200 text-sm">{{ patientError }}</p>
      <router-link to="/mon-espace" class="inline-block mt-2 text-sm text-teal-400">Accéder par nom →</router-link>
    </div>

    <div v-if="!isPatient" class="page-card p-4">
      <input v-model="filtre.nom" placeholder="Filtrer par nom patient" class="modal-input text-sm max-w-md" />
    </div>

    <div class="table-card">
      <table class="w-full text-sm">
        <thead>
          <tr class="text-slate-500 text-xs uppercase">
            <th v-if="!isPatient" class="p-4 text-left">Patient</th>
            <th class="p-4 text-left">Médecin</th>
            <th class="p-4 text-left">Date</th>
            <th class="p-4 text-left">Médicaments</th>
            <th class="p-4 text-left">QR</th>
            <th class="p-4 text-left">Export</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="o in filtered" :key="o.id" class="border-t border-white/5 hover:bg-white/3">
            <td v-if="!isPatient" class="p-4 text-white font-medium">{{ o.patient_nom }}</td>
            <td class="p-4 text-slate-400">{{ o.medecin_nom || '—' }}</td>
            <td class="p-4 text-slate-500 text-xs">{{ formatDate(o.date_ordonnance) }}</td>
            <td class="p-4 text-slate-300 max-w-xs truncate">{{ o.medicaments }}</td>
            <td class="p-4">
              <button @click="showQr(o)" class="text-xs text-teal-400 hover:text-teal-300">QR</button>
            </td>
            <td class="p-4">
              <div class="flex gap-2">
                <button @click="exportPdf(o)" class="text-xs text-red-400 hover:text-red-300">PDF</button>
                <button @click="exportExcel(o)" class="text-xs text-emerald-400 hover:text-emerald-300">Excel</button>
              </div>
            </td>
          </tr>
          <tr v-if="!filtered.length"><td colspan="6" class="p-8 text-center text-slate-500">Aucune ordonnance</td></tr>
        </tbody>
      </table>
    </div>

    <div v-if="showAdd" class="modal" @click.self="showAdd = false">
      <div class="modal-content max-w-lg">
        <h3 class="text-white font-semibold mb-4">Nouvelle ordonnance</h3>
        <form @submit.prevent="create" class="space-y-3">
          <select v-model="form.patient_id" class="modal-input" required>
            <option value="">Patient *</option>
            <option v-for="p in patients" :key="p.id" :value="p.id">{{ p.nom }} {{ p.prenom }}</option>
          </select>
          <select v-model="form.medecin_id" class="modal-input">
            <option value="">Médecin prescripteur</option>
            <option v-for="d in medecins" :key="d.id" :value="d.id">{{ d.prenom }} {{ d.nom }} — {{ d.specialite }}</option>
          </select>
          <textarea v-model="form.medicaments" placeholder="Médicaments et posologie *" class="modal-input" rows="4" required></textarea>
          <textarea v-model="form.instructions" placeholder="Instructions" class="modal-input" rows="2"></textarea>
          <div v-if="formError" class="text-red-400 text-sm">{{ formError }}</div>
          <div class="modal-buttons">
            <button type="button" @click="showAdd = false" class="btn-cancel">Annuler</button>
            <button type="submit" class="btn-save">Enregistrer</button>
          </div>
        </form>
      </div>
    </div>

    <div v-if="qrOrdonnance" class="modal" @click.self="qrOrdonnance = null">
      <div class="modal-content max-w-sm text-center">
        <h3 class="text-white font-semibold mb-2">{{ qrOrdonnance.patient_nom }}</h3>
        <p class="text-xs text-slate-500 mb-4">QR Code patient — Ordonnance #{{ qrOrdonnance.id }}</p>
        <img v-if="qrImage" :src="qrImage" alt="QR" class="mx-auto w-48 h-48 bg-white p-3 rounded-xl" />
        <p class="text-[10px] text-slate-600 font-mono mt-3 break-all">{{ qrOrdonnance.patient_qr_code }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import QRCode from 'qrcode'
import { ordonnanceService, patientService, doctorService, getUser, resolvePatientId } from '../services/api.js'
import { exportOrdonnanceExcel, exportOrdonnancePdf, exportOrdonnancesListExcel, exportOrdonnancesListPdf } from '../utils/exportExcel.js'

const user = getUser()
const isPatient = computed(() => user?.role === 'PATIENT')
const ordonnances = ref([])
const patients = ref([])
const medecins = ref([])
const showAdd = ref(false)
const formError = ref('')
const filtre = ref({ nom: '' })
const qrOrdonnance = ref(null)
const qrImage = ref('')
const form = ref({ patient_id: '', medecin_id: '', medicaments: '', instructions: '' })
const patientError = ref('')
const myPatientId = ref(null)

const filtered = computed(() => {
  let list = ordonnances.value
  if (filtre.value.nom) {
    const q = filtre.value.nom.toLowerCase()
    list = list.filter(o => o.patient_nom?.toLowerCase().includes(q))
  }
  return list
})

function formatDate(d) {
  return new Date(d).toLocaleString('fr-FR', { day: 'numeric', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' })
}

async function showQr(o) {
  qrOrdonnance.value = o
  qrImage.value = await QRCode.toDataURL(`SGHL-PATIENT:${o.patient_qr_code}`, { width: 256 })
}

function exportPdf(o) { exportOrdonnancePdf(o) }
function exportExcel(o) { exportOrdonnanceExcel(o) }
function exportAllExcel() { exportOrdonnancesListExcel(filtered.value) }
function exportAllPdf() { exportOrdonnancesListPdf(filtered.value) }

async function load() {
  patientError.value = ''
  let patientId = null
  if (isPatient.value) {
    patientId = await resolvePatientId()
    myPatientId.value = patientId
    if (!patientId) {
      patientError.value = 'Dossier patient introuvable pour votre compte. Utilisez Mon espace patient avec votre nom.'
      ordonnances.value = []
      return
    }
  }
  ordonnances.value = await ordonnanceService.list(patientId)
  if (!isPatient.value) {
    const [pats, docs] = await Promise.all([patientService.list(), doctorService.list()])
    patients.value = pats
    medecins.value = docs.filter(d => d.est_actif)
  }
}

async function create() {
  formError.value = ''
  try {
    const payload = {
      patient_id: Number(form.value.patient_id),
      medicaments: form.value.medicaments,
      instructions: form.value.instructions || undefined,
    }
    if (form.value.medecin_id) {
      const doc = medecins.value.find(d => String(d.id) === String(form.value.medecin_id))
      if (doc?.user_id) payload.medecin_id = Number(doc.user_id)
    }
    await ordonnanceService.create(payload)
    showAdd.value = false
    form.value = { patient_id: '', medecin_id: '', medicaments: '', instructions: '' }
    await load()
  } catch (e) {
    formError.value = e.message || 'Erreur lors de la création'
  }
}

onMounted(load)
</script>

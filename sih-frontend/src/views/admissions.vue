<template>
  <div class="space-y-6">
    <div class="page-heading">
      <div>
        <h2 class="text-xl font-bold text-white">📝 Hospitalisations</h2>
        <p class="text-slate-400 text-sm">{{ admissionsActives.length }} patient(s) hospitalisé(s)</p>
      </div>
      <button @click="openModal" class="action-button px-5 py-2.5 rounded-xl text-sm font-medium">+ Nouvelle admission</button>
    </div>

    <div v-if="error" class="page-card p-4 border border-red-500/30 bg-red-500/10 text-red-300 text-sm">{{ error }}</div>

    <div class="table-card">
      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead>
            <tr class="text-slate-500 text-xs uppercase">
              <th class="text-left p-4">Patient</th>
              <th class="text-left p-4">Lit</th>
              <th class="text-left p-4">Motif</th>
              <th class="text-left p-4">Entrée</th>
              <th class="text-left p-4">Sortie</th>
              <th class="text-left p-4">Frais</th>
              <th class="text-left p-4">Statut</th>
              <th class="text-left p-4">Action</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="loading"><td colspan="8" class="p-8 text-center text-slate-500">Chargement…</td></tr>
            <tr v-else-if="!admissions.length"><td colspan="8" class="p-8 text-center text-slate-500">Aucune hospitalisation</td></tr>
            <tr v-for="a in admissions" :key="a.id" class="border-t border-white/5 hover:bg-white/3">
              <td class="p-4 text-white font-medium">{{ a.patient_nom }}</td>
              <td class="p-4 text-slate-400">Lit #{{ a.lit_id || '—' }}</td>
              <td class="p-4 text-slate-400">{{ a.motif_hospitalisation }}</td>
              <td class="p-4 text-slate-400">{{ formatDate(a.date_entree) }}</td>
              <td class="p-4 text-slate-400">{{ a.date_sortie ? formatDate(a.date_sortie) : '—' }}</td>
              <td class="p-4 text-teal-400">{{ Number(a.frais_hebergement_total || 0).toLocaleString() }} FC</td>
              <td class="p-4">
                <span class="text-xs px-2 py-0.5 rounded-full"
                  :class="a.est_cloture ? 'bg-slate-500/20 text-slate-400' : 'bg-emerald-500/20 text-emerald-300'">
                  {{ a.est_cloture ? 'Sorti' : 'Actif' }}
                </span>
              </td>
              <td class="p-4">
                <button v-if="!a.est_cloture" @click="sortie(a)" class="text-xs text-amber-400 hover:text-amber-300">Sortie</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div v-if="showModal" class="modal" @click.self="showModal = false">
      <div class="modal-content max-w-lg">
        <h3 class="text-white font-semibold mb-4">Nouvelle hospitalisation</h3>
        <form @submit.prevent="hospitaliser" class="space-y-4">
          <label class="form-field">
            <span>Email du patient *</span>
            <div class="flex gap-2">
              <input v-model="form.email" type="email" required placeholder="patient@sghl.com" class="modal-input flex-1" />
              <button type="button" @click="chercherPatient" class="btn-save text-sm whitespace-nowrap" :disabled="searchingPatient">
                {{ searchingPatient ? '…' : 'Chercher' }}
              </button>
            </div>
            <p v-if="patientSelectionne" class="text-teal-400 text-xs mt-1">✓ {{ patientSelectionne.nom }} {{ patientSelectionne.prenom }}</p>
            <p v-if="patientSearchError" class="text-red-400 text-xs mt-1">{{ patientSearchError }}</p>
          </label>
          <label class="form-field">
            <span>Lit disponible *</span>
            <select v-model="form.lit_id" class="modal-input" required>
              <option value="">Choisir un lit…</option>
              <option v-for="l in litsLibres" :key="l.id" :value="l.id">
                Chambre {{ chambreNum(l.chambre_id) }} — Lit {{ l.code_lit }}
              </option>
            </select>
          </label>
          <label class="form-field">
            <span>Motif d'hospitalisation *</span>
            <input v-model="form.motif" required placeholder="Ex: Observation post-opératoire" class="modal-input" />
          </label>
          <div class="modal-buttons">
            <button type="button" @click="showModal = false" class="btn-cancel">Annuler</button>
            <button type="submit" class="btn-save" :disabled="saving || !patientSelectionne">Hospitaliser</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { clinicalService, patientService } from '../services/api.js'

const admissions = ref([])
const chambres = ref([])
const lits = ref([])
const loading = ref(true)
const saving = ref(false)
const error = ref('')
const showModal = ref(false)
const searchingPatient = ref(false)
const patientSearchError = ref('')
const patientSelectionne = ref(null)

const form = ref({ email: '', lit_id: '', motif: '' })

const admissionsActives = computed(() => admissions.value.filter(a => !a.est_cloture))

const litsLibres = computed(() => lits.value.filter(l => !l.est_occupe))

function chambreNum(chambreId) {
  return chambres.value.find(c => c.id === chambreId)?.numero || chambreId
}

function formatDate(iso) {
  if (!iso) return '—'
  return new Date(iso).toLocaleDateString('fr-FR', { day: '2-digit', month: 'short', year: 'numeric' })
}

function openModal() {
  form.value = { email: '', lit_id: '', motif: '' }
  patientSelectionne.value = null
  patientSearchError.value = ''
  showModal.value = true
}

async function chercherPatient() {
  searchingPatient.value = true
  patientSearchError.value = ''
  patientSelectionne.value = null
  try {
    patientSelectionne.value = await patientService.parEmail(form.value.email.trim())
  } catch (e) {
    patientSearchError.value = e.message || 'Patient introuvable.'
  } finally {
    searchingPatient.value = false
  }
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    const [adm, ch, lt] = await Promise.all([
      clinicalService.admissions(),
      clinicalService.chambres(),
      clinicalService.lits(),
    ])
    admissions.value = adm
    chambres.value = ch
    lits.value = lt
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

async function hospitaliser() {
  if (!patientSelectionne.value) return
  saving.value = true
  error.value = ''
  try {
    await clinicalService.hospitaliser({
      patient_id: patientSelectionne.value.id,
      lit_id: Number(form.value.lit_id),
      motif_hospitalisation: form.value.motif.trim(),
    })
    showModal.value = false
    await load()
  } catch (e) {
    error.value = e.message
  } finally {
    saving.value = false
  }
}

async function sortie(a) {
  if (!confirm(`Confirmer la sortie de ${a.patient_nom} ?`)) return
  try {
    await clinicalService.sortieAdmission(a.id)
    await load()
  } catch (e) {
    error.value = e.message
  }
}

onMounted(load)
</script>

<style scoped>
.form-field { display: flex; flex-direction: column; gap: 0.35rem; }
.form-field span { font-size: 0.75rem; color: #94a3b8; font-weight: 500; }
</style>

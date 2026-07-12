<template>
  <div class="space-y-6">
    <div class="page-heading">
      <div>
        <h2 class="text-xl font-bold text-white">📍 Géolocalisation des patients</h2>
        <p class="text-slate-400 text-sm mt-1">Pointe-Noire, Congo-Brazzaville — suivi en temps réel</p>
      </div>
      <div class="flex items-center gap-3">
        <span class="text-xs text-slate-500 flex items-center gap-2">
          <span class="w-2 h-2 rounded-full bg-green-400 animate-pulse"></span>
          Live · {{ lastRefresh }}
        </span>
        <button v-if="canUpdate" @click="showModal = true" class="action-button px-5 py-2.5 rounded-xl text-sm font-medium">
          + Mettre à jour position
        </button>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div class="lg:col-span-2 page-card p-3">
        <div class="flex items-center justify-between mb-2 px-1">
          <h3 class="text-white font-semibold text-sm">Hôpital SGHL — Pointe-Noire</h3>
          <span class="text-xs text-slate-500">{{ activeLocalisations.length }} patient(s)</span>
        </div>
        <HospitalMap
          ref="mapRef"
          :markers="activeLocalisations"
          :selected-id="selected?.id"
          height="560px"
          :animate="true"
          @marker-click="selectPatient"
        />
      </div>

      <div class="space-y-4">
        <div class="page-card p-4">
          <input v-model="search" placeholder="🔍 Rechercher un patient..." class="modal-input w-full text-sm" />
        </div>

        <div v-if="selected" class="page-card p-5 border-teal-500/30">
          <p class="text-xs text-teal-400 uppercase tracking-wider mb-2">Patient sélectionné</p>
          <p class="text-lg font-bold text-white">{{ selected.patient_nom }}</p>
          <p class="text-xs text-slate-500 font-mono">{{ selected.patient_sgl_id }}</p>
          <div class="mt-4 space-y-2 text-sm">
            <p class="text-slate-300"><span class="text-slate-500">Statut :</span> {{ selected.statut_label }}</p>
            <p class="text-slate-300"><span class="text-slate-500">Lieu :</span> {{ selected.batiment }}, {{ selected.etage }}</p>
            <p class="text-slate-300"><span class="text-slate-500">Salle :</span> {{ selected.salle }}</p>
            <p v-if="selected.service_nom" class="text-slate-300"><span class="text-slate-500">Service :</span> {{ selected.service_nom }}</p>
          </div>
          <a v-if="selected.latitude" :href="googleMapsUrl(selected)" target="_blank" rel="noopener"
            class="mt-4 inline-flex items-center gap-2 text-xs text-teal-400 hover:text-teal-300">
            Itinéraire Google Maps ↗
          </a>
        </div>

        <div class="page-card p-4">
          <h3 class="text-white font-semibold mb-3 text-sm">Patients localisés</h3>
          <div class="space-y-2 max-h-[420px] overflow-y-auto">
            <div v-for="loc in filteredLocalisations" :key="loc.id"
              class="p-3 rounded-xl cursor-pointer transition text-sm"
              :class="selected?.id === loc.id ? 'bg-teal-500/15 border border-teal-500/30' : 'bg-white/5 border border-white/5 hover:border-teal-500/20'"
              @click="selectPatient(loc)">
              <div class="flex justify-between items-start gap-2">
                <div class="min-w-0">
                  <p class="text-white font-medium truncate">{{ loc.patient_nom }}</p>
                  <p class="text-[10px] text-teal-400 font-mono">{{ loc.patient_sgl_id }}</p>
                </div>
                <span class="text-[10px] px-2 py-0.5 rounded-full shrink-0"
                  :class="statutClass(loc.statut)">{{ loc.statut_label }}</span>
              </div>
              <p class="text-[11px] text-slate-500 mt-1 truncate">{{ loc.batiment }} · {{ loc.salle }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="showModal" class="modal" @click.self="showModal = false">
      <div class="modal-content max-w-md">
        <h3 class="text-white font-semibold mb-4">Mettre à jour la position</h3>
        <form @submit.prevent="submitLocation" class="space-y-3">
          <select v-model="form.patient_id" required class="modal-input" @change="onPatientChange">
            <option value="">Sélectionner un patient</option>
            <option v-for="p in patients" :key="p.id" :value="p.id">{{ p.nom }} {{ p.prenom }}</option>
          </select>
          <select v-model="form.service_id" class="modal-input">
            <option value="">Service (optionnel)</option>
            <option v-for="s in servicesList" :key="s.id" :value="s.id">{{ s.nom }} — {{ s.batiment }}</option>
          </select>
          <select v-model="form.batiment" class="modal-input" required @change="onBatimentChange">
            <option v-for="b in batiments" :key="b.name" :value="b.name">{{ b.name }}</option>
          </select>
          <input v-model="form.etage" placeholder="Étage" class="modal-input" required />
          <input v-model="form.salle" placeholder="Salle" class="modal-input" required />
          <select v-model="form.statut" class="modal-input">
            <option value="ENREGISTRE">Enregistré à l'accueil</option>
            <option value="EN_ATTENTE">En salle d'attente</option>
            <option value="EN_CONSULTATION">En consultation</option>
            <option value="EXAMEN">En examen</option>
            <option value="HOSPITALISE">Hospitalisé</option>
            <option value="SORTI">Sorti</option>
          </select>
          <div class="modal-buttons">
            <button type="button" @click="showModal = false" class="btn-cancel">Annuler</button>
            <button type="submit" class="btn-save">Enregistrer — la carte se déplace</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { clinicalService, patientService, getUser } from '../services/api.js'
import HospitalMap from '../components/HospitalMap.vue'
import { HOSPITAL_CENTER, BUILDINGS, VILLE } from '../constants/geo.js'

const mapRef = ref(null)
const localisations = ref([])
const patients = ref([])
const servicesList = ref([])
const selected = ref(null)
const showModal = ref(false)
const search = ref('')
const lastRefresh = ref('')
let pollTimer = null

const form = ref({ patient_id: '', service_id: '', batiment: 'Bâtiment A', etage: 'RDC', salle: '', statut: 'EN_ATTENTE' })

const user = getUser()
const canUpdate = computed(() => ['ADMIN','MEDECIN','INFIRMIER','SECRETAIRE','RECEPTIONNISTE'].includes(user?.role))

const batiments = BUILDINGS

const activeLocalisations = computed(() => localisations.value.filter(l => l.statut !== 'SORTI'))

const filteredLocalisations = computed(() => {
  const q = search.value.toLowerCase().trim()
  if (!q) return activeLocalisations.value
  return activeLocalisations.value.filter(l =>
    l.patient_nom?.toLowerCase().includes(q) ||
    l.patient_sgl_id?.toLowerCase().includes(q) ||
    l.salle?.toLowerCase().includes(q)
  )
})

function statutClass(statut) {
  const m = {
    EN_CONSULTATION: 'bg-blue-500/20 text-blue-300',
    HOSPITALISE: 'bg-purple-500/20 text-purple-300',
    EXAMEN: 'bg-amber-500/20 text-amber-300',
    EN_ATTENTE: 'bg-green-500/20 text-green-300',
  }
  return m[statut] || 'bg-teal-500/20 text-teal-300'
}

function selectPatient(loc) {
  selected.value = loc
}

function googleMapsUrl(loc) {
  return `https://www.google.com/maps/dir/?api=1&destination=${loc.latitude},${loc.longitude}`
}

function onBatimentChange() {
  const svc = servicesList.value.find(s => s.batiment === form.value.batiment)
  if (svc) {
    form.value.etage = svc.etage
    form.value.service_id = svc.id
  }
}

function onPatientChange() {
  const p = patients.value.find(x => x.id === Number(form.value.patient_id))
  if (p) form.value.salle = `Accueil — ${p.nom} ${p.prenom}`
}

async function load() {
  try {
    const [locs, pats, svcs] = await Promise.all([
      clinicalService.localisations(),
      patientService.list(),
      clinicalService.services(),
    ])
    localisations.value = locs
    patients.value = pats
    servicesList.value = svcs
    lastRefresh.value = new Date().toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
    if (selected.value) {
      selected.value = locs.find(l => l.id === selected.value.id) || locs[0] || null
    } else if (locs.length) {
      selected.value = locs[0]
    }
  } catch (e) {
    console.error(e)
  }
}

async function submitLocation() {
  const bat = batiments.find(b => b.name === form.value.batiment)
  const payload = {
    ...form.value,
    patient_id: Number(form.value.patient_id),
    service_id: form.value.service_id ? Number(form.value.service_id) : null,
    latitude: bat?.lat,
    longitude: bat?.lng,
  }
  await clinicalService.updateLocalisation(payload)
  showModal.value = false
  await load()
  const loc = localisations.value.find(l => l.patient_id === payload.patient_id)
  if (loc) selectPatient(loc)
}

onMounted(() => {
  load()
  pollTimer = setInterval(load, 5000)
})

onUnmounted(() => {
  if (pollTimer) clearInterval(pollTimer)
})
</script>

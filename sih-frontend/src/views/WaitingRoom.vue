<template>
  <div class="space-y-6">
    <div class="page-heading">
      <div>
        <h2 class="text-xl font-bold text-white">🪑 Salles d'attente</h2>
        <p class="text-slate-400 text-sm">File standard et salon VIP réservé aux clients privilégiés</p>
      </div>
      <button @click="openAdd(activeTab)" class="action-button px-5 py-2.5 rounded-xl text-sm font-medium">
        + Ajouter {{ activeTab === 'PRIVILEGE' ? '(VIP)' : '' }}
      </button>
    </div>

    <!-- Onglets -->
    <div class="flex flex-wrap gap-2">
      <button
        v-for="tab in tabs"
        :key="tab.id"
        type="button"
        @click="activeTab = tab.id"
        class="px-4 py-2 rounded-xl text-sm font-medium border transition"
        :class="activeTab === tab.id
          ? tab.id === 'PRIVILEGE'
            ? 'bg-amber-500/20 border-amber-500/40 text-amber-200'
            : 'bg-teal-500/20 border-teal-500/40 text-teal-200'
          : 'border-white/10 text-slate-400 hover:text-white'"
      >
        {{ tab.icon }} {{ tab.label }}
        <span class="ml-1 text-xs opacity-70">({{ counts[tab.id] }})</span>
      </button>
    </div>

    <div class="page-card p-4">
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
        <input v-model="filtre.nom" placeholder="Nom et prénom" class="modal-input text-sm" />
        <input v-model="filtre.identite" placeholder="N° identité" class="modal-input text-sm" />
        <button type="button" @click="load" class="btn-save text-sm">Actualiser</button>
      </div>
    </div>

    <!-- Salon VIP -->
    <div
      v-if="activeTab === 'PRIVILEGE'"
      class="page-card p-4 border border-amber-500/30 bg-gradient-to-r from-amber-500/5 to-transparent"
    >
      <p class="text-amber-300 text-sm font-medium">⭐ Salon VIP — accueil prioritaire, confort et prise en charge rapide</p>
    </div>

    <div class="table-card">
      <table class="w-full text-sm">
        <thead>
          <tr class="text-slate-500 text-xs uppercase">
            <th class="p-4 text-left">N° identité</th>
            <th class="p-4 text-left">Nom et prénom</th>
            <th v-if="activeTab === 'PRIVILEGE'" class="p-4 text-left">Carte VIP</th>
            <th class="p-4 text-left">Sexe</th>
            <th class="p-4 text-left">GSM</th>
            <th class="p-4 text-left">Âge</th>
            <th class="p-4 text-left">Motif</th>
            <th class="p-4 text-left">Statut</th>
            <th class="p-4 text-left">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="e in filtered"
            :key="e.id"
            class="border-t border-white/5 hover:bg-white/3"
            :class="activeTab === 'PRIVILEGE' ? 'bg-amber-500/5' : ''"
          >
            <td class="p-4 font-mono text-teal-400 text-xs">{{ e.numero_identite }}</td>
            <td class="p-4 text-white font-medium">
              {{ e.patient_nom }}
              <span v-if="e.priorite === 'URGENT'" class="ml-1 text-[10px] text-red-400">URGENT</span>
            </td>
            <td v-if="activeTab === 'PRIVILEGE'" class="p-4">
              <span class="text-xs text-amber-400">{{ e.carte_type || '—' }}</span>
              <p class="text-[10px] text-slate-500 font-mono">{{ e.carte_numero }}</p>
              <p v-if="e.taux_reduction" class="text-[10px] text-amber-300">-{{ e.taux_reduction }}%</p>
            </td>
            <td class="p-4 text-slate-400">{{ e.genre_label }}</td>
            <td class="p-4 text-slate-400">{{ e.telephone }}</td>
            <td class="p-4 text-slate-400">{{ e.age }}</td>
            <td class="p-4 text-slate-400 text-xs max-w-[140px] truncate">{{ e.motif || '—' }}</td>
            <td class="p-4">
              <span class="text-xs px-2 py-0.5 rounded-full bg-blue-500/20 text-blue-300">{{ e.statut_label }}</span>
            </td>
            <td class="p-4">
              <ActionMenu :items="menuItems(e)" @action="(k) => onAction(k, e)" />
            </td>
          </tr>
          <tr v-if="!filtered.length">
            <td :colspan="activeTab === 'PRIVILEGE' ? 9 : 8" class="p-8 text-center text-slate-500">
              {{ activeTab === 'PRIVILEGE' ? 'Aucun client privilégié en attente' : 'Aucun patient en attente' }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="showAdd" class="modal" @click.self="showAdd = false">
      <div class="modal-content max-w-md">
        <h3 class="text-white font-semibold mb-4">
          {{ addTypeFile === 'PRIVILEGE' ? '⭐ Ajouter au salon VIP' : 'Ajouter à la salle d\'attente' }}
        </h3>
        <form @submit.prevent="add" class="space-y-3">
          <select v-model="form.patient_id" class="modal-input" required>
            <option value="">Patient *</option>
            <option v-for="p in patientOptions" :key="p.id" :value="p.id">
              {{ p.nom }} {{ p.prenom }}{{ p._vip ? ' ⭐' : '' }}
            </option>
          </select>
          <input v-model="form.motif" placeholder="Motif de visite" class="modal-input" />
          <select v-model="form.priorite" class="modal-input">
            <option value="NORMAL">Priorité normale</option>
            <option value="URGENT">Urgent</option>
          </select>
          <p v-if="addTypeFile === 'PRIVILEGE'" class="text-xs text-amber-400">
            Les clients avec carte active sont dirigés automatiquement vers le salon VIP.
          </p>
          <div class="modal-buttons">
            <button type="button" @click="showAdd = false" class="btn-cancel">Annuler</button>
            <button type="submit" class="btn-save">Ajouter</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { waitingService, patientService, privilegeService } from '../services/api.js'
import ActionMenu from '../components/ActionMenu.vue'

const router = useRouter()
const standardEntries = ref([])
const vipEntries = ref([])
const patients = ref([])
const vipPatientIds = ref(new Set())
const showAdd = ref(false)
const addTypeFile = ref('STANDARD')
const activeTab = ref('STANDARD')
const filtre = ref({ nom: '', identite: '' })
const form = ref({ patient_id: '', motif: '', priorite: 'NORMAL' })

const tabs = [
  { id: 'STANDARD', label: 'Salle standard', icon: '🪑' },
  { id: 'PRIVILEGE', label: 'Salon VIP privilèges', icon: '⭐' },
]

const counts = computed(() => ({
  STANDARD: standardEntries.value.length,
  PRIVILEGE: vipEntries.value.length,
}))

const currentEntries = computed(() =>
  activeTab.value === 'PRIVILEGE' ? vipEntries.value : standardEntries.value
)

const filtered = computed(() => {
  let list = currentEntries.value
  if (filtre.value.nom) {
    const q = filtre.value.nom.toLowerCase()
    list = list.filter((e) => e.patient_nom.toLowerCase().includes(q))
  }
  if (filtre.value.identite) {
    list = list.filter((e) => e.numero_identite.includes(filtre.value.identite))
  }
  return list
})

const patientOptions = computed(() => {
  const waitingIds = new Set([
    ...standardEntries.value.map((e) => e.patient_id),
    ...vipEntries.value.map((e) => e.patient_id),
  ])
  const list = patients.value
    .filter((p) => !waitingIds.has(p.id))
    .map((p) => ({
      ...p,
      _vip: vipPatientIds.value.has(p.id),
    }))
  if (addTypeFile.value === 'PRIVILEGE') {
    return list.filter((p) => p._vip)
  }
  return list
})

function menuItems() {
  return [
    { key: 'consultation', icon: '🩺', label: 'Mettre en consultation' },
    { key: 'dossier', icon: '📁', label: 'Voir dossier' },
    { key: 'terminer', icon: '✓', label: 'Terminer' },
    { key: 'supprimer', icon: '🗑️', label: 'Supprimer', danger: true },
  ]
}

async function openAdd(typeFile) {
  addTypeFile.value = typeFile
  form.value = {
    patient_id: '',
    motif: typeFile === 'PRIVILEGE' ? 'Consultation prioritaire VIP' : '',
    priorite: typeFile === 'PRIVILEGE' ? 'URGENT' : 'NORMAL',
  }
  try {
    await load(true)
    const waitingIds = new Set([
      ...standardEntries.value.map((e) => e.patient_id),
      ...vipEntries.value.map((e) => e.patient_id),
    ])
    const options = patients.value
      .filter((p) => !waitingIds.has(p.id))
      .filter((p) => typeFile !== 'PRIVILEGE' || vipPatientIds.value.has(p.id))
    console.log('[SalleAttente] openAdd — patients disponibles:', options.length, 'type:', typeFile)
    if (!options.length) {
      alert(
        typeFile === 'PRIVILEGE'
          ? 'Aucun client privilégié disponible. Créez une carte VIP ou retirez les patients déjà en attente.'
          : 'Aucun patient disponible à ajouter (tous sont déjà en attente ou la liste est vide).'
      )
      return
    }
  } catch (e) {
    console.error('[SalleAttente] openAdd:', e)
    alert(`Impossible de préparer l'ajout : ${e.message}`)
    return
  }
  showAdd.value = true
}

async function onAction(key, e) {
  if (key === 'dossier') router.push(`/patients/${e.patient_id}`)
  else if (key === 'consultation') await waitingService.setStatut(e.id, 'EN_CONSULTATION')
  else if (key === 'terminer') await waitingService.setStatut(e.id, 'TERMINE')
  else if (key === 'supprimer') await waitingService.remove(e.id)
  await load()
}

async function load(silent = false) {
  const errors = []

  try {
    standardEntries.value = await waitingService.list('STANDARD')
  } catch (e) {
    console.error('[SalleAttente] load standard:', e)
    errors.push(`Salle standard : ${e.message}`)
    standardEntries.value = []
  }

  try {
    vipEntries.value = await waitingService.list('PRIVILEGE')
  } catch (e) {
    console.error('[SalleAttente] load VIP:', e)
    errors.push(`Salon VIP : ${e.message}`)
    vipEntries.value = []
  }

  try {
    patients.value = await patientService.list()
    console.log('[SalleAttente] patients chargés:', patients.value.length)
  } catch (e) {
    console.error('[SalleAttente] load patients:', e)
    errors.push(`Patients : ${e.message}`)
    patients.value = []
  }

  try {
    const priv = await privilegeService.list()
    vipPatientIds.value = new Set(
      priv.filter((c) => c.est_actif).map((c) => c.patient_id)
    )
  } catch (e) {
    console.error('[SalleAttente] load privilèges:', e)
    errors.push(`Cartes VIP : ${e.message}`)
    vipPatientIds.value = new Set()
  }

  if (errors.length && !silent) {
    alert(`Erreur lors du chargement :\n${errors.join('\n')}`)
  }
  return errors
}

async function add() {
  const f = form.value
  console.log('[SalleAttente] add — formulaire:', { ...f, type_file: addTypeFile.value })

  const patientId = Number(f.patient_id)
  if (!f.patient_id || Number.isNaN(patientId) || patientId <= 0) {
    alert('Veuillez sélectionner un patient dans la liste.')
    return
  }

  const payload = {
    patient_id: patientId,
    motif: (f.motif || '').trim(),
    priorite: f.priorite || 'NORMAL',
    type_file: addTypeFile.value,
  }
  console.log('[SalleAttente] POST /salle-attente', payload)

  try {
    const res = await waitingService.add(payload)
    console.log('[SalleAttente] réponse:', res)
    const fileCible = res?.type_file || addTypeFile.value
    alert(
      fileCible === 'PRIVILEGE'
        ? `Patient ajouté au salon VIP avec succès (${res?.patient_nom || ''}).`
        : `Patient ajouté à la salle d'attente avec succès (${res?.patient_nom || ''}).`
    )
    showAdd.value = false
    await load()
    activeTab.value = fileCible
  } catch (e) {
    console.error('[SalleAttente] add:', e)
    alert(`Échec de l'ajout : ${e.message}`)
  }
}

watch(activeTab, () => {
  filtre.value = { nom: '', identite: '' }
})

onMounted(load)
</script>

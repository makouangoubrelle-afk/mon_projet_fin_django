<template>
  <div class="space-y-6">
    <div class="page-heading">
      <div>
        <h2 class="text-xl font-bold text-white">🚨 Urgences</h2>
        <p class="text-slate-400 text-sm">Gestion des cas urgents</p>
      </div>
      <button @click="openAdd" class="action-button px-5 py-2.5 rounded-xl text-sm font-medium">+ Nouveau cas</button>
    </div>

    <div class="table-card">
      <table class="w-full text-sm">
        <thead>
          <tr class="text-slate-500 text-xs uppercase">
            <th class="p-4 text-left">Patient</th>
            <th class="p-4 text-left">Diagnostic</th>
            <th class="p-4 text-left">Situation</th>
            <th class="p-4 text-left">Date</th>
            <th class="p-4 text-left">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="u in cas" :key="u.id" class="border-t border-white/5 hover:bg-white/3">
            <td class="p-4 text-white font-medium">{{ u.patient_nom }}</td>
            <td class="p-4 text-slate-300">{{ u.diagnostic }}</td>
            <td class="p-4">
              <span class="text-xs px-2 py-0.5 rounded-full font-medium"
                :class="u.situation === 'IMPORTANT' || u.situation === 'CRITIQUE' ? 'bg-orange-500/20 text-orange-300' : 'bg-green-500/20 text-green-300'">
                {{ u.situation_label }}
              </span>
            </td>
            <td class="p-4 text-slate-500 text-xs">{{ formatDate(u.date_admission) }}</td>
            <td class="p-4">
              <ActionMenu :items="urgenceMenu" @action="(k) => onAction(k, u)" />
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="showModal" class="modal" @click.self="showModal = false">
      <div class="modal-content max-w-lg">
        <h3 class="text-white font-semibold mb-4">{{ editing ? 'Modifier le cas' : 'Nouveau cas urgence' }}</h3>
        <form @submit.prevent="save" class="space-y-3">
          <select v-if="!editing" v-model="form.patient_id" class="modal-input" required>
            <option value="">Patient *</option>
            <option v-for="p in patients" :key="p.id" :value="p.id">{{ p.nom }} {{ p.prenom }}</option>
          </select>
          <input v-model="form.diagnostic" placeholder="Diagnostic *" class="modal-input" required />
          <select v-model="form.situation" class="modal-input">
            <option value="NORMAL">Normal</option>
            <option value="IMPORTANT">Important</option>
            <option value="CRITIQUE">Critique</option>
          </select>
          <textarea v-if="editing" v-model="form.traitement" placeholder="Traitements" class="modal-input" rows="2"></textarea>
          <textarea v-if="editing" v-model="form.examen_biologique" placeholder="E. Biologique" class="modal-input" rows="2"></textarea>
          <textarea v-if="editing" v-model="form.examen_radiologique" placeholder="E. Radiologique" class="modal-input" rows="2"></textarea>
          <textarea v-model="form.notes" placeholder="Notes" class="modal-input" rows="2"></textarea>
          <div class="modal-buttons">
            <button type="button" @click="showModal = false" class="btn-cancel">Annuler</button>
            <button type="submit" class="btn-save">Enregistrer</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { urgenceService, patientService } from '../services/api.js'
import ActionMenu from '../components/ActionMenu.vue'

const cas = ref([])
const patients = ref([])
const showModal = ref(false)
const editing = ref(null)
const form = ref({ patient_id: '', diagnostic: '', situation: 'NORMAL', notes: '', traitement: '', examen_biologique: '', examen_radiologique: '' })

const urgenceMenu = [
  { key: 'traitements', icon: '🖨️', label: 'Traitements' },
  { key: 'bio', icon: '🖨️', label: 'E. Biologique' },
  { key: 'radio', icon: '🖨️', label: 'E. Radiologique' },
  { key: 'edit', icon: '✏️', label: 'Modifier' },
  { key: 'delete', icon: '🗑️', label: 'Supprimer', danger: true },
]

function formatDate(d) { return new Date(d).toLocaleString('fr-FR') }

async function openAdd() {
  editing.value = null
  form.value = { patient_id: '', diagnostic: '', situation: 'NORMAL', notes: '', traitement: '', examen_biologique: '', examen_radiologique: '' }
  try {
    patients.value = await patientService.list()
    console.log('[Urgence] openAdd — patients chargés:', patients.value.length)
    if (!patients.value.length) {
      alert('Aucun patient disponible. Enregistrez d\'abord un patient dans la page Patients.')
      return
    }
  } catch (e) {
    console.error('[Urgence] openAdd — chargement patients:', e)
    alert(`Impossible de charger les patients : ${e.message}`)
    return
  }
  showModal.value = true
}

async function onAction(key, u) {
  if (key === 'edit') {
    editing.value = u
    form.value = { ...u, patient_id: u.patient_id }
    showModal.value = true
  } else if (key === 'delete') {
    if (confirm('Supprimer ce cas ?')) { await urgenceService.delete(u.id); await load() }
  } else if (key === 'traitements') {
    alert(u.traitement || 'Aucun traitement enregistré.\n\nUtilisez Modifier pour ajouter.')
  } else if (key === 'bio') {
    alert(u.examen_biologique || 'Aucun examen biologique.\n\nUtilisez Modifier pour ajouter.')
  } else if (key === 'radio') {
    alert(u.examen_radiologique || 'Aucun examen radiologique.\n\nUtilisez Modifier pour ajouter.')
  }
}

async function load() {
  try {
    cas.value = await urgenceService.list()
  } catch (e) {
    console.error('[Urgence] load cas:', e)
    alert(`Erreur lors du chargement des urgences : ${e.message}`)
  }
  try {
    patients.value = await patientService.list()
    console.log('[Urgence] patients chargés:', patients.value.length)
  } catch (e) {
    console.error('[Urgence] load patients:', e)
    alert(`Erreur lors du chargement des patients : ${e.message}`)
  }
}

async function save() {
  const f = form.value
  console.log('[Urgence] save — formulaire:', { ...f, editing: !!editing.value })

  if (!editing.value) {
    const patientId = Number(f.patient_id)
    if (!f.patient_id || Number.isNaN(patientId) || patientId <= 0) {
      alert('Veuillez sélectionner un patient dans la liste.')
      return
    }
  }
  if (!f.diagnostic?.trim()) {
    alert('Le diagnostic est obligatoire.')
    return
  }

  try {
    if (editing.value) {
      const payload = {
        diagnostic: f.diagnostic.trim(),
        situation: f.situation,
        notes: f.notes || '',
        traitement: f.traitement || '',
        examen_biologique: f.examen_biologique || '',
        examen_radiologique: f.examen_radiologique || '',
      }
      console.log('[Urgence] PUT /urgences/' + editing.value.id, payload)
      const res = await urgenceService.update(editing.value.id, payload)
      console.log('[Urgence] réponse:', res)
      alert('Cas urgence modifié avec succès.')
    } else {
      const payload = {
        patient_id: Number(f.patient_id),
        diagnostic: f.diagnostic.trim(),
        situation: f.situation,
        notes: f.notes || '',
      }
      console.log('[Urgence] POST /urgences', payload)
      const res = await urgenceService.create(payload)
      console.log('[Urgence] réponse:', res)
      alert('Cas urgence enregistré avec succès.')
    }
    showModal.value = false
    await load()
  } catch (e) {
    console.error('[Urgence] save:', e)
    alert(`Échec de l'enregistrement : ${e.message}`)
  }
}

onMounted(load)
</script>

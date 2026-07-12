<template>
  <div class="space-y-6">
    <div class="page-heading">
      <div>
        <h2 class="text-xl font-bold text-white">👨‍⚕️ Médecins</h2>
        <p class="text-slate-400 text-sm">{{ docteurs.length }} médecins enregistrés</p>
      </div>
      <button @click="openModal()" class="action-button px-5 py-2.5 rounded-xl text-sm font-medium">+ Nouveau médecin</button>
    </div>

    <div class="flex flex-wrap gap-3">
      <input v-model="search" placeholder="🔍 Rechercher..." class="modal-input max-w-xs text-sm" />
      <select v-model="filterSpecialite" class="modal-input max-w-xs text-sm">
        <option value="">Toutes les spécialités</option>
        <option v-for="s in specialites" :key="s" :value="s">{{ s }}</option>
      </select>
    </div>

    <div class="table-card">
      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead>
            <tr class="text-slate-500 text-xs uppercase">
              <th class="p-4 text-left">ID</th>
              <th class="p-4 text-left">Nom complet</th>
              <th class="p-4 text-left">Spécialité</th>
              <th class="p-4 text-left">Email</th>
              <th class="p-4 text-left">Téléphone</th>
              <th class="p-4 text-left">Service</th>
              <th class="p-4 text-left">Statut</th>
              <th class="p-4 text-left">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="d in filteredDocteurs" :key="d.id" class="border-t border-white/5 hover:bg-white/3">
              <td class="p-4 text-teal-400 font-mono text-xs">#{{ d.id }}</td>
              <td class="p-4 text-white font-medium">Dr. {{ d.nom }} {{ d.prenom }}</td>
              <td class="p-4"><span class="px-2 py-0.5 rounded-full bg-blue-500/15 text-blue-300 text-xs">{{ d.specialite }}</span></td>
              <td class="p-4 text-slate-400">{{ d.email }}</td>
              <td class="p-4 text-slate-400">{{ d.telephone }}</td>
              <td class="p-4 text-slate-400">{{ d.service_nom || '—' }}</td>
              <td class="p-4">
                <span class="text-xs px-2 py-0.5 rounded-full"
                  :class="d.est_actif ? 'bg-green-500/20 text-green-300' : 'bg-slate-500/20 text-slate-400'">
                  {{ d.est_actif ? 'Actif' : 'Inactif' }}
                </span>
              </td>
              <td class="p-4">
                <div class="flex gap-2">
                  <button @click="openModal(d)" class="text-xs text-teal-400 hover:text-teal-300">Modifier</button>
                  <button @click="toggle(d.id)" class="text-xs text-amber-400 hover:text-amber-300">{{ d.est_actif ? 'Désactiver' : 'Activer' }}</button>
                  <button @click="remove(d.id)" class="text-xs text-red-400 hover:text-red-300">Supprimer</button>
                </div>
              </td>
            </tr>
            <tr v-if="filteredDocteurs.length === 0">
              <td colspan="8" class="p-8 text-center text-slate-500">Aucun médecin trouvé.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div v-if="showModal" class="modal" @click.self="showModal = false">
      <div class="modal-content max-w-lg max-h-[90vh] overflow-y-auto">
        <h3 class="text-white font-semibold mb-4">{{ editing ? 'Modifier le médecin' : 'Ajouter un médecin' }}</h3>
        <form @submit.prevent="save" class="space-y-3">
          <div class="grid grid-cols-2 gap-3">
            <input v-model="form.nom" placeholder="Nom *" class="modal-input" required />
            <input v-model="form.prenom" placeholder="Prénom *" class="modal-input" required />
          </div>
          <select v-model="form.specialite" class="modal-input" required>
            <option value="">Spécialité *</option>
            <option v-for="s in specialites" :key="s" :value="s">{{ s }}</option>
          </select>
          <input v-model="form.email" type="email" placeholder="Email *" class="modal-input" required />
          <input v-model="form.telephone" placeholder="Téléphone *" class="modal-input" required />
          <input v-model="form.numero_ordre" placeholder="N° ordre des médecins" class="modal-input" />
          <select v-model="form.service_id" class="modal-input">
            <option value="">Service (optionnel)</option>
            <option v-for="s in services" :key="s.id" :value="s.id">{{ s.nom }}</option>
          </select>
          <textarea v-model="form.adresse" placeholder="Adresse" class="modal-input" rows="2"></textarea>
          <input v-model="form.photo" placeholder="Photo (URL optionnelle)" class="modal-input" />
          <p v-if="error" class="text-red-400 text-sm">{{ error }}</p>
          <div class="modal-buttons">
            <button type="button" @click="showModal = false" class="btn-cancel">Annuler</button>
            <button type="submit" class="btn-save" :disabled="saving">{{ saving ? 'Enregistrement...' : 'Enregistrer' }}</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { doctorService, clinicalService } from '../services/api.js'

const docteurs = ref([])
const services = ref([])
const search = ref('')
const filterSpecialite = ref('')
const showModal = ref(false)
const editing = ref(null)
const saving = ref(false)
const error = ref('')

const specialites = [
  'Cardiologie', 'Neurologie', 'Pédiatrie', 'Gynécologie', 'Dermatologie',
  'Orthopédie', 'Psychiatrie', 'Ophtalmologie', 'Urgences', 'Médecine générale',
]

const emptyForm = () => ({
  nom: '', prenom: '', specialite: '', email: '', telephone: '',
  adresse: '', numero_ordre: '', photo: '', service_id: '',
})

const form = ref(emptyForm())

const filteredDocteurs = computed(() => {
  let list = docteurs.value
  const q = search.value.toLowerCase().trim()
  if (q) {
    list = list.filter(d =>
      `${d.nom} ${d.prenom}`.toLowerCase().includes(q) ||
      d.email.toLowerCase().includes(q) ||
      d.specialite.toLowerCase().includes(q)
    )
  }
  if (filterSpecialite.value) {
    list = list.filter(d => d.specialite === filterSpecialite.value)
  }
  return list
})

function openModal(d = null) {
  editing.value = d
  error.value = ''
  if (d) {
    form.value = {
      nom: d.nom, prenom: d.prenom, specialite: d.specialite, email: d.email,
      telephone: d.telephone, adresse: d.adresse || '', numero_ordre: d.numero_ordre || '',
      photo: d.photo || '', service_id: d.service_id || '',
    }
  } else {
    form.value = emptyForm()
  }
  showModal.value = true
}

async function load() {
  const [docs, svcs] = await Promise.all([doctorService.list(), clinicalService.services()])
  docteurs.value = docs
  services.value = svcs
}

async function save() {
  saving.value = true
  error.value = ''
  try {
    const payload = { ...form.value }
    if (payload.service_id) payload.service_id = Number(payload.service_id)
    else delete payload.service_id
    if (editing.value) {
      await doctorService.update(editing.value.id, payload)
    } else {
      await doctorService.create(payload)
    }
    showModal.value = false
    await load()
  } catch (e) {
    error.value = e.message
  } finally {
    saving.value = false
  }
}

async function toggle(id) {
  await doctorService.toggle(id)
  await load()
}

async function remove(id) {
  if (!confirm('Supprimer ce médecin ?')) return
  await doctorService.delete(id)
  await load()
}

onMounted(load)
</script>

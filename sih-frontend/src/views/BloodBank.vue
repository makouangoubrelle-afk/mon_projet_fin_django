<template>
  <div class="space-y-6">
    <div class="page-heading">
      <div>
        <h2 class="text-xl font-bold text-white">🩸 Banque de Sang</h2>
        <p class="text-slate-400 text-sm mt-1">Gestion des stocks sanguins par groupe</p>
      </div>
      <button @click="showAdd = true" class="action-button px-5 py-2.5 rounded-xl text-sm font-medium">+ Ajouter une poche</button>
    </div>

    <div class="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-8 gap-3">
      <div v-for="s in stock" :key="s.groupe_sanguin" class="page-card p-4 text-center cursor-pointer hover:border-red-500/30"
        :class="s.statut === 'CRITIQUE' ? 'ring-2 ring-red-500/50' : ''" @click="filterGroupe = s.groupe_sanguin">
        <p class="text-2xl font-bold text-white">{{ s.groupe_sanguin }}</p>
        <p class="text-lg font-semibold text-teal-400 mt-1">{{ s.total_ml }} ml</p>
        <p class="text-xs text-slate-500">{{ s.poches_disponibles }} poches</p>
        <span class="inline-block mt-2 text-[10px] px-2 py-0.5 rounded-full"
          :class="{ 'bg-red-500/20 text-red-300': s.statut === 'CRITIQUE', 'bg-amber-500/20 text-amber-300': s.statut === 'BAS', 'bg-emerald-500/20 text-emerald-300': s.statut === 'NORMAL' }">
          {{ s.statut }}
        </span>
      </div>
    </div>

    <div v-if="criticalGroups.length" class="p-4 rounded-2xl bg-red-500/10 border border-red-500/30">
      <p class="text-red-300 font-medium">⚠️ Stock critique : {{ criticalGroups.join(', ') }}</p>
    </div>

    <div class="table-card">
      <div class="p-4 border-b border-white/5 flex justify-between items-center">
        <h3 class="text-white font-semibold">Inventaire des poches</h3>
        <button v-if="filterGroupe" @click="filterGroupe = ''" class="text-xs text-teal-400">Tout afficher</button>
      </div>
      <table class="w-full text-sm">
        <thead>
          <tr class="text-slate-500 text-xs uppercase">
            <th class="p-4 text-left">N° Poche</th>
            <th class="p-4 text-left">Groupe</th>
            <th class="p-4 text-left">Volume</th>
            <th class="p-4 text-left">Collecte</th>
            <th class="p-4 text-left">Expiration</th>
            <th class="p-4 text-left">Statut</th>
            <th class="p-4 text-left">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="p in pochesFiltered" :key="p.id" class="border-t border-white/5 hover:bg-white/3 cursor-pointer" @click="selected = p">
            <td class="p-4 text-white font-mono text-xs">{{ p.numero_poche }}</td>
            <td class="p-4"><span class="font-bold text-red-400">{{ p.groupe_sanguin }}</span></td>
            <td class="p-4 text-slate-300">{{ p.volume_ml }} ml</td>
            <td class="p-4 text-slate-400">{{ formatDate(p.date_collecte) }}</td>
            <td class="p-4 text-slate-400">{{ formatDate(p.date_expiration) }}</td>
            <td class="p-4">
              <span class="text-xs px-2 py-0.5 rounded-full" :class="p.statut === 'DISPONIBLE' ? 'bg-emerald-500/20 text-emerald-300' : 'bg-slate-500/20 text-slate-400'">{{ p.statut }}</span>
            </td>
            <td class="p-4" @click.stop>
              <ActionMenu :items="[{ key: 'detail', icon: '👁️', label: 'Détails' }]" @action="selected = p" />
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="selected" class="page-card p-5 border-red-500/20">
      <p class="text-white font-semibold">Poche {{ selected.numero_poche }}</p>
      <p class="text-sm text-slate-400 mt-2">Groupe {{ selected.groupe_sanguin }} · {{ selected.volume_ml }} ml · Expire {{ formatDate(selected.date_expiration) }}</p>
    </div>

    <div v-if="showAdd" class="modal" @click.self="showAdd = false">
      <div class="modal-content max-w-md">
        <h3 class="text-white font-semibold mb-4">Ajouter une poche de sang</h3>
        <form @submit.prevent="addPoche" class="space-y-3">
          <select v-model="form.groupe_sanguin" class="modal-input" required>
            <option v-for="g in groupes" :key="g" :value="g">{{ g }}</option>
          </select>
          <input v-model="form.numero_poche" placeholder="N° poche *" class="modal-input" required />
          <input v-model.number="form.volume_ml" type="number" placeholder="Volume (ml)" class="modal-input" />
          <input v-model="form.date_collecte" type="date" class="modal-input" required />
          <input v-model="form.date_expiration" type="date" class="modal-input" required />
          <div class="modal-buttons">
            <button type="button" @click="showAdd = false" class="btn-cancel">Annuler</button>
            <button type="submit" class="btn-save">Enregistrer</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { clinicalService } from '../services/api.js'
import ActionMenu from '../components/ActionMenu.vue'

const stock = ref([])
const poches = ref([])
const showAdd = ref(false)
const selected = ref(null)
const filterGroupe = ref('')
const groupes = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
const form = ref({ groupe_sanguin: 'O+', numero_poche: '', volume_ml: 450, date_collecte: '', date_expiration: '' })

const criticalGroups = computed(() => stock.value.filter(s => s.statut === 'CRITIQUE').map(s => s.groupe_sanguin))
const pochesFiltered = computed(() => filterGroupe.value ? poches.value.filter(p => p.groupe_sanguin === filterGroupe.value) : poches.value)

function formatDate(d) { return new Date(d).toLocaleDateString('fr-FR') }

async function load() {
  const [s, p] = await Promise.all([clinicalService.stockSanguin(), clinicalService.banqueSang()])
  stock.value = s
  poches.value = p
}

async function addPoche() {
  await clinicalService.addPoche(form.value)
  showAdd.value = false
  await load()
}

onMounted(load)
</script>

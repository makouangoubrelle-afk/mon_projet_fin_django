<template>
  <div class="space-y-6">
    <div class="page-heading">
      <div>
        <h2 class="text-xl font-bold text-white">🛏️ Chambres & Lits</h2>
        <p class="text-slate-400 text-sm">{{ chambres.length }} chambres — gestion des statuts</p>
      </div>
      <button @click="showAddModal = true" class="action-button px-5 py-2.5 rounded-xl text-sm font-medium">+ Ajouter une chambre</button>
    </div>

    <!-- Légende statuts -->
    <div class="flex flex-wrap gap-3">
      <span v-for="s in statutOptions" :key="s.value"
        class="flex items-center gap-2 text-xs px-3 py-1.5 rounded-full border"
        :class="statutBadgeClass(s.value)">
        <span class="w-2 h-2 rounded-full" :class="statutDotClass(s.value)"></span>
        {{ s.label }}
        <span class="text-slate-500">({{ countByStatut(s.value) }})</span>
      </span>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <div v-for="c in chambres" :key="c.id"
        class="page-card p-5 transition-all"
        :class="statutCardBorder(c.statut)">
        <div class="flex justify-between items-start mb-3 gap-2">
          <h3 class="text-white font-semibold">Chambre {{ c.numero }}</h3>
          <span class="text-xs px-2.5 py-1 rounded-full font-medium shrink-0"
            :class="statutBadgeClass(c.statut)">
            {{ c.statut_label }}
          </span>
        </div>

        <div class="flex gap-2 mb-3">
          <span class="text-xs px-2 py-0.5 rounded-full bg-purple-500/20 text-purple-300">{{ c.type_chambre }}</span>
          <span class="text-xs text-slate-500">📍 {{ c.batiment }}, Étage {{ c.etage }}</span>
        </div>

        <p class="text-sm text-slate-400">
          Lits : <span class="text-white font-medium">{{ c.lits_occupes }}/{{ c.lits_total }}</span> occupés
        </p>
        <p class="text-sm text-teal-400 mt-1">{{ Number(c.prix_journalier).toLocaleString() }} FC/jour</p>

        <div class="mt-3 h-2 rounded-full bg-white/10">
          <div class="h-2 rounded-full transition-all duration-500"
            :class="c.lits_occupes > 0 ? 'bg-red-500' : 'bg-green-500'"
            :style="{ width: c.lits_total ? (c.lits_occupes / c.lits_total * 100) + '%' : '0%' }"></div>
        </div>

        <!-- Changer le statut -->
        <div class="mt-4 pt-4 border-t border-white/10">
          <label class="text-xs text-slate-500 uppercase tracking-wider block mb-2">Changer le statut</label>
          <div class="grid grid-cols-2 gap-2">
            <button v-for="s in statutOptions" :key="s.value"
              @click="changeStatut(c, s.value)"
              :disabled="updating === c.id"
              class="text-xs px-2 py-2 rounded-lg border transition disabled:opacity-50"
              :class="c.statut === s.value
                ? statutBadgeClass(s.value) + ' ring-1 ring-white/20'
                : 'bg-white/5 border-white/10 text-slate-400 hover:bg-white/10 hover:text-white'">
              {{ s.label }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal ajouter chambre -->
    <div v-if="showAddModal" class="modal" @click.self="showAddModal = false">
      <div class="modal-content max-w-md">
        <h3 class="text-white font-semibold mb-4">Ajouter une chambre</h3>
        <form @submit.prevent="addChambre" class="space-y-3">
          <input v-model="newChambre.numero" placeholder="N° chambre *" class="modal-input" required />
          <select v-model="newChambre.type_chambre" class="modal-input">
            <option value="STANDARD">Standard</option>
            <option value="VIP">VIP</option>
            <option value="REANIMATION">Réanimation</option>
          </select>
          <input v-model.number="newChambre.prix_journalier" type="number" placeholder="Prix journalier (FC) *" class="modal-input" required />
          <input v-model="newChambre.batiment" placeholder="Bâtiment" class="modal-input" />
          <input v-model="newChambre.etage" placeholder="Étage" class="modal-input" />
          <input v-model.number="newChambre.nb_lits" type="number" min="1" max="6" placeholder="Nombre de lits" class="modal-input" />
          <div class="modal-buttons">
            <button type="button" @click="showAddModal = false" class="btn-cancel">Annuler</button>
            <button type="submit" class="btn-save">Enregistrer</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { clinicalService } from '../services/api.js'

const chambres = ref([])
const updating = ref(null)
const showAddModal = ref(false)
const newChambre = ref({ numero: '', type_chambre: 'STANDARD', prix_journalier: 50000, batiment: 'Bâtiment A', etage: '1', nb_lits: 2 })

const statutOptions = [
  { value: 'LIBRE', label: 'Libre' },
  { value: 'OCCUPEE', label: 'Occupée' },
  { value: 'NETTOYAGE', label: 'En nettoyage' },
  { value: 'MAINTENANCE', label: 'Maintenance' },
]

function statutBadgeClass(statut) {
  const m = {
    LIBRE: 'bg-green-500/15 border-green-500/30 text-green-300',
    OCCUPEE: 'bg-red-500/15 border-red-500/30 text-red-300',
    NETTOYAGE: 'bg-amber-500/15 border-amber-500/30 text-amber-300',
    MAINTENANCE: 'bg-slate-500/15 border-slate-500/30 text-slate-300',
  }
  return m[statut] || m.LIBRE
}

function statutDotClass(statut) {
  const m = {
    LIBRE: 'bg-green-400',
    OCCUPEE: 'bg-red-400',
    NETTOYAGE: 'bg-amber-400',
    MAINTENANCE: 'bg-slate-400',
  }
  return m[statut] || 'bg-green-400'
}

function statutCardBorder(statut) {
  const m = {
    LIBRE: 'border-green-500/20',
    OCCUPEE: 'border-red-500/30',
    NETTOYAGE: 'border-amber-500/30',
    MAINTENANCE: 'border-slate-500/30',
  }
  return m[statut] || ''
}

function countByStatut(statut) {
  return chambres.value.filter(c => c.statut === statut).length
}

async function load() {
  chambres.value = await clinicalService.chambres()
}

async function changeStatut(chambre, statut) {
  if (chambre.statut === statut) return
  updating.value = chambre.id
  try {
    const updated = await clinicalService.updateChambreStatut(chambre.id, statut)
    const idx = chambres.value.findIndex(c => c.id === chambre.id)
    if (idx !== -1) chambres.value[idx] = updated
  } catch (e) {
    alert(e.message)
  } finally {
    updating.value = null
  }
}

async function addChambre() {
  const ch = await clinicalService.createChambre({
    numero: newChambre.value.numero,
    type_chambre: newChambre.value.type_chambre,
    prix_journalier: newChambre.value.prix_journalier,
    batiment: newChambre.value.batiment,
    etage: newChambre.value.etage,
  })
  const codes = ['A', 'B', 'C', 'D', 'E', 'F']
  for (let i = 0; i < newChambre.value.nb_lits; i++) {
    await clinicalService.createLit({ chambre_id: ch.id, code_lit: codes[i] })
  }
  showAddModal.value = false
  newChambre.value = { numero: '', type_chambre: 'STANDARD', prix_journalier: 50000, batiment: 'Bâtiment A', etage: '1', nb_lits: 2 }
  await load()
}

onMounted(load)
</script>

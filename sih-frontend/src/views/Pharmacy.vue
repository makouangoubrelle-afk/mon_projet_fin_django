<template>
  <div class="space-y-6">
    <div class="page-heading">
      <div>
        <h2 class="text-xl font-bold text-white">💊 Pharmacie</h2>
        <p class="text-slate-400 text-sm">{{ meds.length }} médicaments — stock et prix</p>
      </div>
      <button @click="showAdd = true" class="action-button px-5 py-2.5 rounded-xl text-sm font-medium">+ Ajouter médicament</button>
    </div>

    <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
      <div class="page-card p-4 text-center">
        <p class="text-2xl font-bold text-white">{{ meds.length }}</p>
        <p class="text-xs text-slate-500">Références</p>
      </div>
      <div class="page-card p-4 text-center">
        <p class="text-2xl font-bold text-teal-400">{{ totalStock }}</p>
        <p class="text-xs text-slate-500">Unités en stock</p>
      </div>
      <div class="page-card p-4 text-center">
        <p class="text-2xl font-bold text-amber-400">{{ lowStock }}</p>
        <p class="text-xs text-slate-500">Stock bas (&lt;20)</p>
      </div>
      <div class="page-card p-4 text-center">
        <p class="text-2xl font-bold text-white">{{ formatMoney(valeurStock) }}</p>
        <p class="text-xs text-slate-500">Valeur stock</p>
      </div>
    </div>

    <div class="table-card">
      <table class="w-full text-sm">
        <thead>
          <tr class="text-slate-500 text-xs uppercase">
            <th class="p-4 text-left">Médicament</th>
            <th class="p-4 text-left">Stock</th>
            <th class="p-4 text-left">Prix unitaire</th>
            <th class="p-4 text-left">Valeur</th>
            <th class="p-4 text-left">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="m in meds" :key="m.id" class="border-t border-white/5 hover:bg-white/3">
            <td class="p-4 text-white font-medium">{{ m.nom }}</td>
            <td class="p-4">
              <span :class="m.quantite_en_stock < 20 ? 'text-amber-400 font-bold' : 'text-emerald-400'">{{ m.quantite_en_stock }}</span>
            </td>
            <td class="p-4 text-slate-300">{{ formatMoney(m.prix_unitaire) }}</td>
            <td class="p-4 text-slate-400">{{ formatMoney(m.quantite_en_stock * m.prix_unitaire) }}</td>
            <td class="p-4">
              <ActionMenu :items="medMenu" @action="(k) => onMedAction(k, m)" />
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="showAdd || editing" class="modal" @click.self="closeModal">
      <div class="modal-content max-w-md">
        <h3 class="text-white font-semibold mb-4">{{ editing ? 'Modifier' : 'Nouveau médicament' }}</h3>
        <form @submit.prevent="saveMed" class="space-y-3">
          <input v-model="form.nom" placeholder="Nom du médicament *" class="modal-input" required />
          <input v-model.number="form.quantite_en_stock" type="number" min="0" placeholder="Quantité en stock" class="modal-input" required />
          <input v-model.number="form.prix_unitaire" type="number" min="0" step="100" placeholder="Prix unitaire (FC) *" class="modal-input" required />
          <div class="modal-buttons">
            <button type="button" @click="closeModal" class="btn-cancel">Annuler</button>
            <button type="submit" class="btn-save">Enregistrer</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { pharmacyService } from '../services/api.js'
import ActionMenu from '../components/ActionMenu.vue'

const meds = ref([])
const showAdd = ref(false)
const editing = ref(null)
const form = ref({ nom: '', quantite_en_stock: 0, prix_unitaire: 0 })
const medMenu = [
  { key: 'edit', icon: '✏️', label: 'Modifier stock/prix' },
  { key: 'delete', icon: '🗑️', label: 'Supprimer', danger: true },
]

const totalStock = computed(() => meds.value.reduce((s, m) => s + m.quantite_en_stock, 0))
const lowStock = computed(() => meds.value.filter(m => m.quantite_en_stock < 20).length)
const valeurStock = computed(() => meds.value.reduce((s, m) => s + m.quantite_en_stock * Number(m.prix_unitaire), 0))

function formatMoney(n) { return Number(n || 0).toLocaleString('fr-FR') + ' FC' }

function closeModal() { showAdd.value = false; editing.value = null }

function onMedAction(key, m) {
  if (key === 'edit') {
    editing.value = m
    form.value = { nom: m.nom, quantite_en_stock: m.quantite_en_stock, prix_unitaire: Number(m.prix_unitaire) }
    showAdd.value = true
  } else if (key === 'delete' && confirm('Supprimer ce médicament ?')) {
    pharmacyService.deleteMedicament(m.id).then(load)
  }
}

async function load() { meds.value = await pharmacyService.medicaments() }

async function saveMed() {
  if (editing.value) {
    await pharmacyService.updateMedicament(editing.value.id, form.value)
  } else {
    await pharmacyService.addMedicament(form.value)
  }
  closeModal()
  form.value = { nom: '', quantite_en_stock: 0, prix_unitaire: 0 }
  await load()
}

onMounted(load)
</script>

<template>
  <div class="space-y-6">
    <div class="page-heading">
      <div>
        <h2 class="text-xl font-bold text-white">🛡️ Assurances</h2>
        <p class="text-slate-400 text-sm">Gestion des assurances et taux de couverture</p>
      </div>
      <button type="button" class="btn-save" @click="showForm = true">+ Nouvelle assurance</button>
    </div>

    <div v-if="error" class="text-red-400 text-sm">{{ error }}</div>

    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <div v-for="a in assurances" :key="a.id" class="page-card p-5">
        <h3 class="text-white font-semibold">{{ a.nom }}</h3>
        <p class="text-teal-400 text-2xl font-bold mt-2">{{ a.taux_couverture }}%</p>
        <p class="text-slate-500 text-xs mt-1">Code : {{ a.code_assurance }}</p>
        <p v-if="a.adresse" class="text-slate-400 text-sm mt-2">{{ a.adresse }}</p>
      </div>
    </div>

    <div v-if="showForm" class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4" @click.self="showForm = false">
      <form class="page-card p-6 w-full max-w-md space-y-4" @submit.prevent="create">
        <h3 class="text-white font-semibold">Nouvelle assurance</h3>
        <label class="form-field"><span>Nom *</span><input v-model="form.nom" class="modal-input" required /></label>
        <label class="form-field"><span>Code *</span><input v-model="form.code_assurance" class="modal-input" required /></label>
        <label class="form-field"><span>Taux couverture (%) *</span><input v-model.number="form.taux_couverture" type="number" min="0" max="100" class="modal-input" required /></label>
        <label class="form-field"><span>Adresse</span><textarea v-model="form.adresse" class="modal-input" rows="2" /></label>
        <div class="flex gap-2 justify-end">
          <button type="button" class="btn-cancel" @click="showForm = false">Annuler</button>
          <button type="submit" class="btn-save">Créer</button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { assuranceService } from '../services/api.js'

const assurances = ref([])
const showForm = ref(false)
const error = ref('')
const form = ref({ nom: '', code_assurance: '', taux_couverture: 80, adresse: '' })

async function load() {
  try {
    assurances.value = await assuranceService.list()
  } catch (e) {
    error.value = e.message
  }
}

async function create() {
  try {
    await assuranceService.create(form.value)
    showForm.value = false
    form.value = { nom: '', code_assurance: '', taux_couverture: 80, adresse: '' }
    await load()
  } catch (e) {
    error.value = e.message
  }
}

onMounted(load)
</script>

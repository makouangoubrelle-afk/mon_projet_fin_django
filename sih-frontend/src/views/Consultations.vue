<template>
  <div class="space-y-6">
    <div class="page-heading">
      <div>
        <h2 class="text-xl font-bold text-white">🩺 Consultations</h2>
        <p class="text-slate-400 text-sm">{{ consultations.length }} consultations</p>
      </div>
      <button @click="showModal = true" class="action-button px-5 py-2.5 rounded-xl text-sm font-medium">+ Nouvelle</button>
    </div>
    <div class="space-y-3">
      <div v-for="c in consultations" :key="c.id" class="page-card p-5">
        <div class="flex justify-between">
          <div>
            <p class="text-white font-medium">Patient #{{ c.patient_id }}</p>
            <p class="text-sm text-slate-400 mt-1">{{ c.motif_consultation }}</p>
            <p v-if="c.diagnostic" class="text-sm text-teal-300 mt-1">Diagnostic : {{ c.diagnostic }}</p>
          </div>
          <div class="text-right">
            <p class="text-xs text-slate-500">{{ formatDate(c.date_consultation) }}</p>
            <p class="text-sm text-teal-400 mt-1">{{ Number(c.frais_consultation).toLocaleString() }} FC</p>
          </div>
        </div>
      </div>
    </div>
    <div v-if="showModal" class="modal" @click.self="showModal = false">
      <div class="modal-content">
        <h3 class="text-white font-semibold mb-4">Nouvelle consultation</h3>
        <form @submit.prevent="create" class="space-y-3">
          <select v-model="form.patient_id" class="modal-input" required>
            <option value="">Patient</option>
            <option v-for="p in patients" :key="p.id" :value="p.id">{{ p.nom }} {{ p.prenom }}</option>
          </select>
          <input v-model="form.motif_consultation" placeholder="Motif" class="modal-input" required />
          <input v-model="form.diagnostic" placeholder="Diagnostic" class="modal-input" />
          <div class="grid grid-cols-2 gap-3">
            <input v-model="form.tension_arterielle" placeholder="Tension (12/8)" class="modal-input" />
            <input v-model="form.temperature" type="number" step="0.1" placeholder="Temp °C" class="modal-input" />
          </div>
          <div class="modal-buttons">
            <button type="button" @click="showModal = false" class="btn-cancel">Annuler</button>
            <button type="submit" class="btn-save">Créer</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { consultationService, patientService } from '../services/api.js'

const consultations = ref([])
const patients = ref([])
const showModal = ref(false)
const form = ref({ patient_id: '', motif_consultation: '', diagnostic: '', tension_arterielle: '', temperature: null })

function formatDate(d) { return new Date(d).toLocaleDateString('fr-FR', { hour: '2-digit', minute: '2-digit' }) }

async function load() {
  consultations.value = await consultationService.list()
  patients.value = await patientService.list()
}

async function create() {
  const payload = { ...form.value, patient_id: Number(form.value.patient_id) }
  if (payload.temperature) payload.temperature = Number(payload.temperature)
  await consultationService.create(payload)
  showModal.value = false
  await load()
}

onMounted(load)
</script>

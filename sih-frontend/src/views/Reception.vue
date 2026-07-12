<template>
  <div class="space-y-6">
    <div class="page-heading">
      <div>
        <h2 class="text-xl font-bold text-white">🏪 Réception</h2>
        <p class="text-slate-400 text-sm">Enregistrement des nouveaux patients à l'accueil</p>
      </div>
      <router-link to="/patients" class="action-button px-5 py-2.5 rounded-xl text-sm font-medium inline-block">
        + Enregistrer un patient
      </router-link>
    </div>
    <div class="page-card p-6">
      <h3 class="text-white font-semibold mb-4">File d'enregistrement récente</h3>
      <div class="space-y-3">
        <div v-for="p in patients" :key="p.id" class="flex items-center justify-between p-4 rounded-xl bg-white/5 border border-white/5">
          <div>
            <p class="text-white font-medium">{{ p.nom }} {{ p.prenom }}</p>
            <p class="text-xs text-teal-400">{{ p.sgl_id }}</p>
          </div>
          <p class="text-xs text-slate-500">{{ formatDate(p.date_enregistrement) }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { patientService } from '../services/api.js'
const patients = ref([])
function formatDate(d) { return new Date(d).toLocaleDateString('fr-FR', { hour: '2-digit', minute: '2-digit' }) }
onMounted(async () => {
  try {
    patients.value = await patientService.list()
  } catch (e) {
    console.error('Erreur chargement patients:', e)
    patients.value = []
  }
})
</script>

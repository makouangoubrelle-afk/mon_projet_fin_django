<template>
  <div class="space-y-6">
    <div class="page-heading">
      <div>
        <h2 class="text-xl font-bold text-white">👥 Personnel</h2>
        <p class="text-slate-400 text-sm">Vue unifiée : médecins, infirmiers et effectifs</p>
      </div>
    </div>

    <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
      <div class="page-card p-5 text-center">
        <p class="text-3xl">👨‍⚕️</p>
        <p class="text-2xl font-bold text-white">{{ doctors.length }}</p>
        <p class="text-slate-500 text-xs">Médecins</p>
      </div>
      <div class="page-card p-5 text-center">
        <p class="text-3xl">💉</p>
        <p class="text-2xl font-bold text-white">{{ nurses.length }}</p>
        <p class="text-slate-500 text-xs">Infirmiers</p>
      </div>
      <div class="page-card p-5 text-center">
        <p class="text-3xl">📋</p>
        <p class="text-2xl font-bold text-white">{{ secretaires.length }}</p>
        <p class="text-slate-500 text-xs">Secrétaires</p>
      </div>
    </div>

    <div class="flex gap-2">
      <router-link to="/doctors" class="btn-save text-sm">Gérer les médecins</router-link>
      <router-link to="/nurses" class="btn-cancel text-sm">Gérer les infirmiers</router-link>
      <router-link to="/users" class="btn-cancel text-sm">Comptes utilisateurs</router-link>
    </div>

    <div class="page-card p-6">
      <h3 class="text-white font-semibold mb-4">Effectif par service</h3>
      <div class="space-y-2 text-sm">
        <div v-for="s in byService" :key="s.nom" class="flex justify-between p-2 rounded-lg bg-white/5">
          <span class="text-white">{{ s.nom }}</span>
          <span class="text-slate-400">{{ s.medecins }} médecin(s) · {{ s.infirmiers }} infirmier(s)</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { doctorService, nurseService, secretaireService } from '../services/api.js'

const doctors = ref([])
const nurses = ref([])
const secretaires = ref([])

const byService = computed(() => {
  const map = {}
  for (const d of doctors.value) {
    const n = d.service_nom || 'Non affecté'
    if (!map[n]) map[n] = { nom: n, medecins: 0, infirmiers: 0 }
    map[n].medecins++
  }
  for (const n of nurses.value) {
    const name = n.service_nom || 'Non affecté'
    if (!map[name]) map[name] = { nom: name, medecins: 0, infirmiers: 0 }
    map[name].infirmiers++
  }
  return Object.values(map)
})

onMounted(async () => {
  const [d, n, s] = await Promise.all([
    doctorService.list(),
    nurseService.list(),
    secretaireService.list(),
  ])
  doctors.value = d
  nurses.value = n
  secretaires.value = s
})
</script>

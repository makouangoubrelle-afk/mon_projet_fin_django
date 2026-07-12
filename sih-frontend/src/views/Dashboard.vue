<template>
  <div class="space-y-8">
    <!-- KPI Cards -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
      <div v-for="kpi in kpis" :key="kpi.label" class="page-card p-6 flex items-center gap-4">
        <div class="w-14 h-14 rounded-2xl flex items-center justify-center text-2xl" :class="kpi.bg">{{ kpi.icon }}</div>
        <div>
          <p class="text-xs text-slate-500 uppercase tracking-wider">{{ kpi.label }}</p>
          <p class="text-3xl font-bold text-white">{{ kpi.value }}</p>
        </div>
      </div>
    </div>

    <!-- Quick access -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div class="page-card p-6">
        <h3 class="text-white font-semibold mb-4 flex items-center gap-2">📍 Patients localisés récemment</h3>
        <div v-if="loading" class="text-slate-500 text-sm">Chargement...</div>
        <div v-else-if="localisations.length === 0" class="text-slate-500 text-sm">Aucun patient localisé.</div>
        <div v-else class="space-y-3">
          <div v-for="loc in localisations.slice(0, 5)" :key="loc.id"
            class="flex items-center justify-between p-3 rounded-xl bg-white/5 border border-white/5">
            <div>
              <p class="text-white text-sm font-medium">{{ loc.patient_nom }}</p>
              <p class="text-xs text-slate-500">{{ loc.batiment }} · {{ loc.salle }}</p>
            </div>
            <span class="text-xs px-2 py-1 rounded-full bg-teal-500/20 text-teal-300">{{ loc.statut_label }}</span>
          </div>
        </div>
      </div>

      <div class="page-card p-6">
        <h3 class="text-white font-semibold mb-4 flex items-center gap-2">🩸 Stock sanguin</h3>
        <div class="grid grid-cols-4 gap-2">
          <div v-for="s in stockSang" :key="s.groupe_sanguin"
            class="text-center p-3 rounded-xl border"
            :class="s.statut === 'CRITIQUE' ? 'border-red-500/40 bg-red-500/10' : s.statut === 'BAS' ? 'border-amber-500/30 bg-amber-500/10' : 'border-white/10 bg-white/5'">
            <p class="text-white font-bold">{{ s.groupe_sanguin }}</p>
            <p class="text-xs text-slate-400">{{ s.poches_disponibles }} poches</p>
            <p class="text-[10px] mt-1" :class="s.statut === 'CRITIQUE' ? 'text-red-400' : 'text-slate-500'">{{ s.statut }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Services -->
    <div class="page-card p-6">
      <h3 class="text-white font-semibold mb-4">🏢 Services hospitaliers & secrétariat</h3>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div v-for="svc in services" :key="svc.id" class="p-4 rounded-2xl bg-white/5 border border-white/5">
          <div class="flex justify-between items-start mb-2">
            <h4 class="text-white font-medium">{{ svc.nom }}</h4>
            <span class="text-[10px] text-teal-400 bg-teal-500/10 px-2 py-0.5 rounded-full">{{ svc.code }}</span>
          </div>
          <p class="text-xs text-slate-500 mb-1">📍 {{ svc.batiment }}, {{ svc.etage }}</p>
          <p class="text-xs text-slate-400">📋 Secrétaire : <span class="text-white">{{ svc.secretaire_nom || 'Non assignée' }}</span></p>
          <p class="text-xs text-slate-500 mt-1">📞 {{ svc.telephone }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { statsService, clinicalService } from '../services/api.js'

const stats = ref({})
const localisations = ref([])
const stockSang = ref([])
const services = ref([])
const loading = ref(true)

const kpis = computed(() => [
  { label: 'Patients', value: stats.value.patients ?? '—', icon: '👥', bg: 'bg-blue-500/20' },
  { label: 'Hospitalisés', value: stats.value.hospitalises ?? '—', icon: '🛏️', bg: 'bg-purple-500/20' },
  { label: 'Consultations', value: stats.value.consultations ?? '—', icon: '🩺', bg: 'bg-teal-500/20' },
  { label: 'Poches de sang', value: stats.value.poches_sang ?? '—', icon: '🩸', bg: 'bg-red-500/20' },
])

onMounted(async () => {
  try {
    const results = await Promise.allSettled([
      statsService.dashboard(),
      clinicalService.localisations(),
      clinicalService.stockSanguin(),
      clinicalService.services(),
    ])
    if (results[0].status === 'fulfilled') stats.value = results[0].value
    if (results[1].status === 'fulfilled') localisations.value = results[1].value
    if (results[2].status === 'fulfilled') stockSang.value = results[2].value
    if (results[3].status === 'fulfilled') services.value = results[3].value
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="space-y-6">
    <div class="page-heading">
      <div>
        <h2 class="text-xl font-bold text-white">📈 Rapports & statistiques</h2>
        <p class="text-slate-400 text-sm">Patients, recettes, occupation, pharmacie, banque de sang</p>
      </div>
      <button type="button" class="btn-save text-sm" @click="load">Actualiser</button>
    </div>

    <div v-if="loading" class="text-slate-500">Chargement…</div>
    <div v-else-if="error" class="text-red-400">{{ error }}</div>
    <template v-else-if="r">
      <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div v-for="k in kpis" :key="k.label" class="page-card p-5">
          <p class="text-xs text-slate-500 uppercase">{{ k.label }}</p>
          <p class="text-2xl font-bold text-white mt-1">{{ k.value }}</p>
        </div>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div class="page-card p-6">
          <h3 class="text-white font-semibold mb-4">🛏️ Occupation des chambres</h3>
          <p class="text-3xl font-bold text-teal-300">{{ r.occupation_chambres?.taux ?? 0 }}%</p>
          <p class="text-slate-400 text-sm mt-1">
            {{ r.occupation_chambres?.lits_occupes }} / {{ r.occupation_chambres?.lits_total }} lits occupés
          </p>
        </div>
        <div class="page-card p-6">
          <h3 class="text-white font-semibold mb-4">💊 Stock pharmacie</h3>
          <p class="text-3xl font-bold text-white">{{ r.stock_pharmacie?.unites ?? 0 }} unités</p>
          <p class="text-amber-400 text-sm mt-1">{{ r.stock_pharmacie?.alertes_rupture ?? 0 }} alertes rupture</p>
          <p class="text-red-400 text-xs">{{ r.stock_pharmacie?.medicaments_expires ?? 0 }} périmés</p>
        </div>
        <div class="page-card p-6">
          <h3 class="text-white font-semibold mb-4">🩸 Banque de sang</h3>
          <p class="text-3xl font-bold text-red-300">{{ r.stock_sang }} poches disponibles</p>
        </div>
        <div class="page-card p-6">
          <h3 class="text-white font-semibold mb-4">💰 Finances</h3>
          <p class="text-teal-300 text-xl font-bold">{{ fmtMoney(r.revenus) }} CDF</p>
          <p class="text-slate-500 text-sm">Recettes encaissées</p>
          <p class="text-slate-400 text-sm mt-2">{{ r.factures_payees }} factures payées · {{ r.factures_en_attente }} en attente</p>
        </div>
      </div>

      <div class="page-card p-6">
        <h3 class="text-white font-semibold mb-4">Médicaments les plus dispensés</h3>
        <div class="space-y-2">
          <div v-for="m in r.medicaments_plus_utilises" :key="m.nom" class="flex justify-between text-sm p-2 rounded-lg bg-white/5">
            <span class="text-white">{{ m.nom }}</span>
            <span class="text-teal-400">{{ m.quantite }} fois</span>
          </div>
          <p v-if="!r.medicaments_plus_utilises?.length" class="text-slate-500 text-sm">Aucune donnée.</p>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { statsService } from '../services/api.js'

const r = ref(null)
const loading = ref(true)
const error = ref('')

const kpis = computed(() => {
  if (!r.value) return []
  return [
    { label: 'Patients', value: r.value.patients },
    { label: 'Consultations', value: r.value.consultations },
    { label: 'Hospitalisés', value: r.value.hospitalises },
    { label: 'Rendez-vous', value: r.value.rendez_vous },
    { label: 'Médecins actifs', value: r.value.medecins },
    { label: 'Infirmiers actifs', value: r.value.infirmiers },
    { label: 'Paiements', value: r.value.paiements_total },
    { label: 'Connexions', value: r.value.connexions_recentes },
  ]
})

function fmtMoney(n) {
  return Number(n || 0).toLocaleString('fr-FR')
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    r.value = await statsService.reports()
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

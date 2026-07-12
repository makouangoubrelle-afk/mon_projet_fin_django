<template>
  <div class="space-y-6">
    <div class="page-heading">
      <div>
        <h2 class="text-xl font-bold text-white">💳 Paiements</h2>
        <p class="text-slate-400 text-sm">Espèces, carte, MTN MoMo, Airtel Money — historique des transactions</p>
      </div>
    </div>

    <div class="grid grid-cols-2 md:grid-cols-5 gap-3">
      <div v-for="m in modes" :key="m.code" class="page-card p-4 text-center">
        <p class="text-lg">{{ m.icon }}</p>
        <p class="text-white font-bold">{{ m.count }}</p>
        <p class="text-[10px] text-slate-500 uppercase">{{ m.label }}</p>
      </div>
    </div>

    <div v-if="error" class="text-red-400 text-sm">{{ error }}</div>

    <div class="page-card overflow-x-auto">
      <table class="w-full text-sm">
        <thead class="bg-white/5 text-slate-500 text-xs uppercase">
          <tr>
            <th class="p-3 text-left">Date</th>
            <th class="p-3 text-left">Patient</th>
            <th class="p-3 text-left">Facture</th>
            <th class="p-3 text-left">Mode</th>
            <th class="p-3 text-right">Montant</th>
            <th class="p-3 text-left">Référence</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="p in paiements" :key="p.id" class="border-t border-white/5 hover:bg-white/5">
            <td class="p-3 text-slate-400 text-xs">{{ fmt(p.date_paiement) }}</td>
            <td class="p-3 text-white">{{ p.patient_nom }}</td>
            <td class="p-3 text-slate-300">{{ p.facture_reference }}</td>
            <td class="p-3"><span class="text-xs px-2 py-0.5 rounded-full bg-teal-500/20 text-teal-300">{{ p.mode_label }}</span></td>
            <td class="p-3 text-right text-white font-medium">{{ Number(p.montant).toLocaleString('fr-FR') }} CDF</td>
            <td class="p-3 text-slate-500 text-xs">{{ p.reference_transaction || '—' }}</td>
          </tr>
        </tbody>
      </table>
      <p v-if="!loading && !paiements.length" class="p-6 text-slate-500">Aucun paiement enregistré.</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { billingService } from '../services/api.js'

const paiements = ref([])
const loading = ref(true)
const error = ref('')

const MODE_META = {
  ESPECES: { label: 'Espèces', icon: '💵' },
  CARTE: { label: 'Carte', icon: '💳' },
  MTN_MOMO: { label: 'MTN MoMo', icon: '📱' },
  AIRTEL_MONEY: { label: 'Airtel', icon: '📲' },
  VIREMENT: { label: 'Virement', icon: '🏦' },
}

const modes = computed(() => {
  const counts = {}
  for (const p of paiements.value) {
    counts[p.mode_paiement] = (counts[p.mode_paiement] || 0) + 1
  }
  return Object.entries(MODE_META).map(([code, meta]) => ({
    code,
    ...meta,
    count: counts[code] || 0,
  }))
})

function fmt(d) {
  return new Date(d).toLocaleString('fr-FR')
}

onMounted(async () => {
  try {
    paiements.value = await billingService.paiements()
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
})
</script>

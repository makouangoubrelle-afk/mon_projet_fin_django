<template>
  <div class="space-y-6">
    <div class="page-heading">
      <div>
        <h2 class="text-xl font-bold text-white">🏦 Banque</h2>
        <p class="text-slate-400 text-sm">Comptes bancaires et mouvements de caisse</p>
      </div>
      <button @click="showModal = true" class="action-button px-5 py-2.5 rounded-xl text-sm font-medium">+ Nouveau compte</button>
    </div>

    <!-- Solde total -->
    <div class="page-card p-6 bg-gradient-to-r from-teal-500/10 to-cyan-500/10 border border-teal-500/20">
      <p class="text-xs text-slate-500 uppercase tracking-wider">Solde total</p>
      <p class="text-3xl font-bold text-white mt-1">{{ formatMoney(resume.solde_total) }}</p>
      <p class="text-sm text-slate-400 mt-1">{{ resume.nb_comptes }} compte(s) · {{ resume.nb_entrees }} entrées enregistrées</p>
    </div>

    <!-- Comptes -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <div v-for="c in comptes" :key="c.id" class="page-card p-5">
        <div class="flex justify-between items-start mb-2">
          <span class="text-2xl">🏦</span>
          <span class="text-xs text-slate-500">{{ c.devise }}</span>
        </div>
        <p class="text-white font-semibold">{{ c.banque }}</p>
        <p class="text-sm text-slate-400">{{ c.nom }}</p>
        <p class="text-xs text-slate-600 font-mono mt-1">{{ c.numero_compte }}</p>
        <p class="text-xl font-bold text-teal-400 mt-3">{{ formatMoney(c.solde) }}</p>
      </div>
    </div>

    <!-- Mouvements récents -->
    <div class="page-card p-6">
      <h3 class="text-white font-semibold mb-4">Mouvements récents</h3>
      <div class="space-y-2">
        <div v-for="m in mouvements" :key="m.id"
          class="flex justify-between items-center p-3 rounded-xl bg-white/5 border border-white/5">
          <div>
            <p class="text-sm text-white">{{ m.libelle }}</p>
            <p class="text-xs text-slate-500">{{ formatDateTime(m.date_mouvement) }}</p>
          </div>
          <span class="font-medium" :class="m.type_mouvement === 'ENTREE' ? 'text-green-400' : 'text-red-400'">
            {{ m.type_mouvement === 'ENTREE' ? '+' : '-' }}{{ formatMoney(m.montant) }}
          </span>
        </div>
        <p v-if="mouvements.length === 0" class="text-slate-500 text-sm text-center py-4">Aucun mouvement.</p>
      </div>
    </div>

    <div v-if="showModal" class="modal" @click.self="showModal = false">
      <div class="modal-content max-w-md">
        <h3 class="text-white font-semibold mb-4">Nouveau compte bancaire</h3>
        <form @submit.prevent="createCompte" class="space-y-3">
          <input v-model="form.banque" placeholder="Banque (ex: Rawbank)" class="modal-input" required />
          <input v-model="form.nom" placeholder="Nom du compte" class="modal-input" required />
          <input v-model="form.numero_compte" placeholder="N° compte" class="modal-input" required />
          <input v-model.number="form.solde" type="number" placeholder="Solde initial" class="modal-input" />
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
import { bankService } from '../services/api.js'

const comptes = ref([])
const mouvements = ref([])
const resume = ref({ solde_total: 0, nb_comptes: 0, nb_entrees: 0 })
const showModal = ref(false)
const form = ref({ banque: 'Rawbank', nom: '', numero_compte: '', solde: 0 })

function formatMoney(n) {
  return new Intl.NumberFormat('fr-FR', { maximumFractionDigits: 0 }).format(n || 0) + ' FC'
}
function formatDateTime(d) {
  return new Date(d).toLocaleString('fr-FR', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' })
}

async function load() {
  const [c, m, r] = await Promise.all([
    bankService.comptes(),
    bankService.mouvements(),
    bankService.soldeTotal(),
  ])
  comptes.value = c
  mouvements.value = m
  resume.value = r
}

async function createCompte() {
  await bankService.createCompte(form.value)
  showModal.value = false
  form.value = { banque: 'Rawbank', nom: '', numero_compte: '', solde: 0 }
  await load()
}

onMounted(load)
</script>
